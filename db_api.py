from datetime import datetime

from sqlalchemy import select, and_, exists

from schema import *
from utils import sha1_str


async def select_or_insert(connection, query_select, query_insert):
    async with connection.begin() as trans:
        ds = await connection.exec(query_select)

        if ds.rowcount:
            result = ds.first()
        else:
            result = await connection.exec(query_insert).primary_key[0]

        await trans.commit()

        return result


async def get_or_create_entity_type(connection, type_name):
    query_select = select([
        entity_type.c.id.label("type_id")
    ]).select_from(
        entity_type
    ).where(
        entity_type.c.name == type_name.lower()
    )

    query_insert = entity_type.insert().values(
        name=type_name.lower()
    )

    return await select_or_insert(connection, query_select, query_insert)


async def get_or_create_entity(connection, type_id, token):
    query_select = select([
        entity.c.id.label("entity_id")
    ]).select_from(
        entity
    ).where(
        and_(
            entity.c.type == type_id,
            entity.c.token == token
        )
    )

    query_insert = entity.insert().values(
        type=type_id,
        token=token
    )

    return await select_or_insert(connection, query_select, query_insert)


async def get_or_create_user(connection, token):
    query_select = select([
        user.c.id.label("user_id")
    ]).select_from(
        user
    ).where(
        user.c.token == token
    )

    query_insert = user.insert().values(
        token=token
    )

    return await select_or_insert(connection, query_select, query_insert)


async def add_or_update_comment_text(connection, comment_id, text):
    text_hash = sha1_str(text)

    query = exists().select_from(comment_text).where(
        and_(
            comment_text.c.comment == comment_id,
            comment_text.c.hash == text_hash
        )
    )

    async with connection.begin() as trans:
        if not await connection.scalar(query):
            result = await connection.exec(
                comment_text.insert().values(
                    comment=comment_id,
                    timestamp=datetime.now(),
                    hash=text_hash,
                    data=text
                )
            ).primary_key[0]

            await trans.commit()

            return result
        else:
            return None
