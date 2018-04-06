import os

from aiohttp import web
from sqlalchemy import create_engine
from sqlalchemy_aio import ASYNCIO_STRATEGY

import api
from arg_schemas import reply_entity_validator, reply_comment_validator, edit_comment_validator, \
    remove_comment_validator, read_entity_comments_validator, validate_args, ValidatorException, \
    read_user_comments_validator, read_comment_replies_validator, read_entity_replies_validator, \
    stream_user_comments_validator, stream_entity_replies_validator
from response_streamer import XMLStreamer
from utils import parse_datetime


async def _read_args(request):
    post_data = (await request.json()) if request.method == "POST" else {}
    get_data = dict(request.match_info)

    return {**get_data, **post_data}


async def reply_entity(connection, data):
    comment_token = await api.add_comment(
        connection,
        entity_type=data["type"],
        entity_token=data["entity"],
        user_token=data["user_token"],
        text=data["text"]
    )

    return {"comment_token": comment_token}


async def reply_comment(connection, data):
    comment_token = await api.reply_comment(
        connection,
        parent_comment_token=data["comment_token"],
        user_token=data["user_token"],
        text=data["text"]
    )

    return {"comment_token": comment_token}


async def edit_comment(connection, data):
    revision_key = await api.edit_comment(
        connection,
        user_token=data["user_token"],
        comment_unique_key=data["comment_token"],
        text=data["text"]
    )

    return {"success": revision_key is not None}


async def remove_comment(connection, data):
    try:
        await api.remove_comment(
            connection,
            user_token=data["user_token"],
            comment_unique_key=data["comment_token"]
        )

        return {"success": True}
    except api.APIException:
        return {"success": False}


async def read_entity_comments(connection, data):
    return [
        item async for item in api.get_entity_comments(
            connection,
            entity_type=data["type"],
            entity_token=data["entity"],
            limit=int(data.get("limit", "1000")),
            offset=int(data.get("offset", "0")),
            with_replies=False
        )
    ]


async def read_entity_replies(connection, data):
    return [
        item async for item in api.get_entity_comments(
            connection,
            entity_type=data["type"],
            entity_token=data["entity"],
            limit=int(data.get("limit", "1000")),
            offset=int(data.get("offset", "0")),
            with_replies=True
        )
    ]


async def read_user_comments(connection, data):
    return [
        item async for item in api.get_user_comments(
            connection,
            user_token=data["user_token"]
        )
    ]


async def read_comment_replies(connection, data):
    return [
        item async for item in api.get_comment_replies(
            connection,
            comment_token=data["comment_token"]
        )
    ]


arg_validators = {
    reply_entity: reply_entity_validator,
    reply_comment: reply_comment_validator,
    edit_comment: edit_comment_validator,
    remove_comment: remove_comment_validator,
    read_entity_comments: read_entity_comments_validator,
    read_user_comments: read_user_comments_validator,
    read_comment_replies: read_comment_replies_validator,
    read_entity_replies: read_entity_replies_validator
}


async def handle_request(connection, request, future):
    try:
        data = await _read_args(request)

        validate_args(data, arg_validators[future])

        result = await future(connection, data)
        return web.json_response({"result": result})
    except TimeoutError:
        return web.json_response({"result": "error", "reasons": "Request timeout expired"}, status=500)
    except api.APIException as e:
        return web.json_response({"result": "error", "reason": "API error ({})".format(str(e))}, status=500)
    except ValidatorException as e:
        return web.json_response({"result": "error", "error": str(e)}, status=500)
    except Exception as e:
        return web.json_response({"error": "Internal server error ({})".format(str(e))}, status=500)


async def stream_user_comments(connection, data):
    idx = 1
    async for item in api.get_user_comments(
            connection,
            user_token=data["user_token"],
            timestamp_from=parse_datetime(data.get("timestamp_from", None)),
            timestamp_to=parse_datetime(data.get("timestamp_to", None))
    ):
        yield {"record{}".format(idx): item}
        idx += 1


async def stream_entity_replies(connection, data):
    idx = 1
    async for item in api.get_entity_comments(
            connection,
            entity_type=data["type"],
            entity_token=data["entity"],
            limit=0,
            offset=0,
            timestamp_from=parse_datetime(data.get("timestamp_from", None)),
            timestamp_to=parse_datetime(data.get("timestamp_to", None)),
            with_replies=True
    ):
        yield {"record{}".format(idx): item}
        idx += 1


streamer_arg_validators = {
    stream_user_comments: stream_user_comments_validator,
    stream_entity_replies: stream_entity_replies_validator
}


async def handle_stream(connection, request, future):
    data = await _read_args(request)

    validate_args(data, streamer_arg_validators[future])

    response = web.StreamResponse(
        status=200,
        reason="OK",
        headers={"Content-Type": "application/octet-stream"}
    )

    streamer = XMLStreamer(response)

    await response.prepare(request)

    await streamer.write_head()
    async for item in future(connection, data):
        await streamer.write_body(item)
    await streamer.write_tail()

    return response


async def get_app():
    db_engine = create_engine(os.getenv("DATABASE_URL"), strategy=ASYNCIO_STRATEGY)
    db_connection = await db_engine.connect()

    app = web.Application()
    app.router.add_post(
        "/api/reply/{type}/{entity}",
        lambda request: handle_request(db_connection, request, reply_entity)
    )
    app.router.add_post(
        "/api/reply/{comment_token}",
        lambda request: handle_request(db_connection, request, reply_comment)
    )
    app.router.add_post(
        "/api/edit/{comment_token}/{user_token}",
        lambda request: handle_request(db_connection, request, edit_comment)
    )
    app.router.add_post(
        "/api/remove/{comment_token}",
        lambda request: handle_request(db_connection, request, remove_comment)
    )

    for url in ["/api/comments/{type}/{entity}",
                "/api/comments/{type}/{entity}/{limit}",
                "/api/comments/{type}/{entity}/{offset}/{limit}"]:
        app.router.add_get(
            url, lambda request: handle_request(db_connection, request, read_entity_comments)
        )

    app.router.add_get(
        "/api/comments/{user_token}",
        lambda request: handle_request(db_connection, request, read_user_comments)
    )
    app.router.add_get(
        "/api/replies/{comment_token}",
        lambda request: handle_request(db_connection, request, read_comment_replies)
    )
    app.router.add_get(
        "/api/replies/{type}/{entity}",
        lambda request: handle_request(db_connection, request, read_entity_replies)
    )

    for url in ["/api/user/download/{user_token}",
                "/api/user/download/{user_token}/{timestamp_from}",
                "/api/user/download/{user_token}/{timestamp_from}/{timestamp_to}"]:
        app.router.add_get(
            url,
            lambda request: handle_stream(db_connection, request, stream_user_comments)
        )

    for url in ["/api/download/{type}/{entity}",
                "/api/download/{type}/{entity}/{timestamp_from}",
                "/api/download/{type}/{entity}/{timestamp_from}/{timestamp_to}"]:
        app.router.add_get(
            url,
            lambda request: handle_stream(db_connection, request, stream_entity_replies)
        )

    return app


if __name__ == "__main__":
    web.run_app(get_app())
