from uuid import uuid4

import db_api
from utils import sha1

class APIException(Exception):
    pass

def _create_comment_identifiers(text):
    return str(uuid4()), sha1(text)


async def add_comment(connection, entity_type, entity_token, user_token, text):
    entity_type_id = await db_api.get_or_create_entity_type(connection, entity_type)
    entity_id = await db_api.get_or_create_entity(connection, entity_type_id, entity_token)
    user_id = await db_api.get_or_create_user(connection, user_token)

    result, text_hash = _create_comment_identifiers(text)
    await db_api.insert_comment(
        connection,
        entity_id=entity_id,
        user_id=user_id,
        unique_key=result,
        text=text,
        text_hash=text_hash
    )

    return result


async def reply_comment(connection, parent_comment_token, user_token, text):
    comment = await db_api.get_comment_by_key(connection, parent_comment_token)

    if not comment:
        raise APIException("Comment with token '{}' was not found".format(parent_comment_token))

    user_id = await db_api.get_or_create_user(connection, user_token)

    result, text_hash = _create_comment_identifiers(text)
    await db_api.insert_comment(
        connection,
        entity_id=comment["entity"],
        user_id=user_id,
        unique_key=result,
        text=text,
        text_hash=text_hash,
        parent_comment_id=comment["id"]
    )

    return result


async def _try_get_comment(connection, user_token, comment_unique_key):
    user_id = await db_api.get_user_id_by_token(connection, user_token)
    comment = await db_api.get_comment_by_key(connection, comment_unique_key)

    if comment["user"] != user_id:
        raise APIException("Access denied. Invalid user token.")
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
    if not await db_api.delete_comment(connection, comment["id"]):
        raise APIException("Could not delete comment")
    else:
        return True


async def get_comments(connection, entity_type, entity_token):
    type_id = await db_api.get_or_create_entity_type(connection, entity_type, create_if_none=False)
    if not type_id:
        raise APIException("Unknown entity type '{}'".format(entity_type))

    entity_id = await db_api.get_or_create_entity(connection, type_id, entity_token, create_if_none=False)
    if not entity_id:
        raise APIException("Entity '{}' was not found".format(entity_token))

    for item in await db_api.get_entity_comments(connection, entity_id):
        yield {
            "text": item["text"],
            "created": item["created"],
            "updated": item["updated"],
        }
