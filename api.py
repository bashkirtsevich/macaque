from uuid import uuid4

import db_api
from utils import sha1


async def add_comment(connection, entity_type, entity_token, user_token, text):
    entity_type_id = await db_api.get_or_create_entity_type(connection, entity_type)
    entity_id = await db_api.get_or_create_entity(connection, entity_type_id, entity_token)
    user_id = await db_api.get_or_create_user(connection, user_token)

    result = uuid4()
    await db_api.insert_comment(
        connection,
        entity_id=entity_id,
        user_id=user_id,
        unique_key=result,
        text=text,
        text_hash=sha1(text)
    )

    return result


async def _try_get_comment(connection, user_token, comment_unique_key):
    user_id = await db_api.get_user_id_by_token(connection, user_token)
    comment = await db_api.get_comment_by_key(connection, comment_unique_key)

    if comment["user"] != user_id:
        raise Exception("Access denied. Invalid user token.")
    else:
        return comment


async def edit_comment(connection, user_token, comment_unique_key, text):
    comment = await _try_get_comment(connection, user_token, comment_unique_key)
    result = await db_api.add_or_update_comment_text(
        connection,
        comment_id=comment["id"],
        text=text,
        text_hash=sha1(text)
    )

    return result


async def remove_comment(connection, user_token, comment_unique_key):
    comment = await _try_get_comment(connection, user_token, comment_unique_key)
    result = await db_api.delete_comment(connection, comment["id"])
    return result
