from datetime import datetime

from sqlalchemy import select, and_, func

from schema import *


async def select_or_insert(connection, query_select, field, query_insert):
    ds = await connection.exec(query_select)

    if ds.rowcount:
        result = ds.first()[field]
    else:
        async with connection.begin() as trans:
            result = await connection.exec(query_insert).inserted_primary_key[0]

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

    return await select_or_insert(connection, query_select, "type_id", query_insert)


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

    return await select_or_insert(connection, query_select, "entity_id", query_insert)


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

    return await select_or_insert(connection, query_select, "user_id", query_insert)


async def add_or_update_comment_text(connection, comment_id, text, text_hash):
    query = select([func.count()]).select_from(comment_text).where(
        and_(
            comment_text.c.comment == comment_id,
            comment_text.c.hash == text_hash
        )
    )

    async with connection.begin() as trans:
        if await connection.scalar(query) == 0:
            result = await connection.exec(
                comment_text.insert().values(
                    comment=comment_id,
                    timestamp=datetime.now(),
                    hash=text_hash,
                    data=text
                )
            ).inserted_primary_key[0]

            await trans.commit()

            return result
        else:
            return None


async def insert_comment(connection, entity_id, user_id, unique_key, parent_comment_id=None):
    async with connection.begin() as trans:
        result = await connection.exec(
            comment.insert().values(
                entity=entity_id,
                user=user_id,
                key=unique_key,
                comment=parent_comment_id
            )
        ).inserted_primary_key[0]

        await trans.commit()

        return result


async def delete_comment(connection, comment_id):
    query = select([func.count()]).select_from(comment).where(
        comment.c.comment == comment_id
    )

    async with connection.begin() as trans:
        if await connection.scalar(query) > 0:
            return False
        else:
            await connection.exec(
                comment.delete().where(
                    comment=comment_id
                )
            )

            await trans.commit()

            return True
