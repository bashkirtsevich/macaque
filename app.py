import os

from aiohttp import web
from cerberus import Validator
from sqlalchemy import create_engine

import api


class ServerException(Exception):
    pass


async def handle_post(connection, request, future):
    try:
        data = await request.json()
        result = await future(connection, data)
        return web.json_response({"result": result})
    except TimeoutError:
        return web.json_response({"result": "error", "reasons": "Request timeout expired"}, status=500)
    except ServerException as e:
        return web.json_response({"result": "error", "error": str(e)}, status=500)
    except Exception as e:
        return web.json_response({"error": "Internal server error ({})".format(str(e))}, status=500)


add_comment_schema = {
    "entity": {
        "type": "dict", "required": True,
        "schema": {
            "type": {"type": "str", "required": True},
            "token": {"type": "str", "required": True}
        }
    },
    "user_token": {"type": "str", "required": True},
    "text": {"type": "str", "required": True}
}

add_comment_validator = Validator(add_comment_schema, allow_unknown=False)

edit_comment_schema = {
    "user_token": {"type": "str", "required": True},
    "comment_token": {"type": "str", "required": True},
    "text": {"type": "str", "required": True}
}

edit_comment_validator = Validator(edit_comment_schema, allow_unknown=False)


async def add_comment(connection, data):
    if not add_comment_validator.validate(data):
        raise ServerException(
            "Invalid arguments for '{}' ({})".format(add_comment, add_comment_validator.errors)
        )

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
    if not edit_comment_validator.validate(data):
        raise ServerException(
            "Invalid arguments for '{}' ({})".format(edit_comment, edit_comment_validator.errors)
        )

    success = await api.edit_comment(
        connection,
        user_token=data["user_token"],
        comment_unique_key=data["comment_token"],
        text=data["text"]
    )

    return {"success": success is not None}


if __name__ == "__main__":
    db_engine = create_engine(os.getenv("DATABASE_URL"))
    db_connection = db_engine.connect()

    app = web.Application()
    app.router.add_post(
        "/api/add_comment", lambda request: handle_post(db_connection, request, add_comment)
    )
    app.router.add_post(
        "/api/edit_comment", lambda request: handle_post(db_connection, request, edit_comment)
    )

    web.run_app(app)
