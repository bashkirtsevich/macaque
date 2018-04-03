import os

from aiohttp import web
from cerberus import Validator
from sqlalchemy import create_engine

import api


class ServerException(Exception):
    pass


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


async def add_comment(connection, request):
    try:
        data = await request.json()

        if not add_comment_validator.validate(data):
            raise ServerException("Invalid arguments for '{}' ({})".format(
                add_comment, add_comment_validator.errors
            ))

        entity = data["entity"]

        comment_token = await api.add_comment(
            connection,
            entity_type=entity["type"],
            entity_token=entity["token"],
            user_token=data["user_token"],
            text=data["text"]
        )

        return web.json_response({"result": {"comment_token": comment_token}})
    except ServerException as e:
        return web.json_response({"result": "error", "error": str(e)}, status=500)
    except Exception as e:
        return web.json_response({"error": "Internal server error ({})".format(str(e))}, status=500)


if __name__ == "__main__":
    db_engine = create_engine(os.getenv("DATABASE_URL"))
    db_connection = db_engine.connect()

    app = web.Application()
    app.router.add_post(
        "/api/add_comment", lambda request: add_comment(db_connection, request)
    )

    web.run_app(app)
