import os

from aiohttp import web
from cerberus import Validator
from sqlalchemy import create_engine

import api


class ServerException(Exception):
    pass


reply_entity_validator = Validator(
    allow_unknown=False,
    schema={
        "type": {"type": "string", "required": True},
        "entity": {"type": "string", "required": True},
        "token": {"type": "string", "required": True},
        "text": {"type": "string", "required": True}
    })

edit_comment_validator = Validator(
    allow_unknown=False,
    schema={
        "user_token": {"type": "string", "required": True},
        "comment_token": {"type": "string", "required": True},
        "text": {"type": "string", "required": True}
    })


async def reply_entity(connection, data):
    comment_token = await api.add_comment(
        connection,
        entity_type=data["type"],
        entity_token=data["entity"],
        user_token=data["token"],
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


arg_validators = {
    reply_entity: reply_entity_validator,
    edit_comment: edit_comment_validator
}


async def handle_post(connection, request, future):
    try:
        data = {**await request.json(), **dict(request.match_info)}

        validator = arg_validators[future]
        if not validator.validate(data):
            raise ServerException(
                "Invalid arguments ({})".format(validator.errors)
            )

        result = await future(connection, data)
        return web.json_response({"result": result})
    except TimeoutError:
        return web.json_response({"result": "error", "reasons": "Request timeout expired"}, status=500)
    except ServerException as e:
        return web.json_response({"result": "error", "error": str(e)}, status=500)
    except Exception as e:
        return web.json_response({"error": "Internal server error ({})".format(str(e))}, status=500)


if __name__ == "__main__":
    db_engine = create_engine(os.getenv("DATABASE_URL"))
    db_connection = db_engine.connect()

    app = web.Application()
    app.router.add_post(
        "/api/reply/{type}/{entity}", lambda request: handle_post(db_connection, request, reply_entity)
    )
    app.router.add_post(
        "/api/edit/{comment_token}/{user_token}", lambda request: handle_post(db_connection, request, edit_comment)
    )

    web.run_app(app)
