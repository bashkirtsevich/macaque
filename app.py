import os

from aiohttp import web
from cerberus import Validator
from sqlalchemy import create_engine

import api


class ServerException(Exception):
    pass


add_comment_validator = Validator(
    allow_unknown=False,
    schema={
        "type": {"type": "str", "required": True},
        "entity": {"type": "str", "required": True},
        "user_token": {"type": "str", "required": True},
        "text": {"type": "str", "required": True}
    })

edit_comment_validator = Validator(
    allow_unknown=False,
    schema={
        "user": {"type": "str", "required": True},
        "comment": {"type": "str", "required": True},
        "text": {"type": "str", "required": True}
    })


async def add_comment(connection, data):
    entity = data["entity"]

    comment_token = await api.add_comment(
        connection,
        entity_type=entity["type"],
        entity_token=entity["token"],
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


arg_validators = {
    add_comment: add_comment_validator,
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
        "/api/{type}/{entity}/add_comment", lambda request: handle_post(db_connection, request, add_comment)
    )
    app.router.add_post(
        "/api/{user}/{comment}/edit_comment", lambda request: handle_post(db_connection, request, edit_comment)
    )

    web.run_app(app)
