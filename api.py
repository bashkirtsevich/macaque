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

