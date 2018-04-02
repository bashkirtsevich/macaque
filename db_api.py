from datetime import datetime

from sqlalchemy import select, and_, exists

from schema import *
from utils import sha1_str


async def get_or_create_entity_type(connection, type_name):
    async with connection.begin() as trans:
        ds = await connection.exec(
            select([
                entity_type.c.id.label("type_id")
            ]).select_from(
                entity_type
            ).where(
                entity_type.c.name == type_name.lower()
            )
        )

        if ds.rowcount:
            result = ds.first()["type_id"]
        else:
            result = await connection.exec(
                entity_type.insert().values(
                    name=type_name.lower()
                )
            ).primary_key[0]

        await trans.commit()

        return result


async def get_or_create_entity(connection, type_name, token):
    async with connection.begin() as trans:
        type_id = get_or_create_entity_type(connection, type_name)

        ds = await connection.exec(
            select([
                entity.c.id.label("entity_id")
            ]).select_from(
                entity
            ).where(
                and_(
                    entity.c.type == type_id,
                    entity.c.token == token
                )
            )
        )

        if ds.rowcount:
            result = ds.first()["entity_id"]
        else:
            result = await connection.exec(
                entity.insert().values(
                    type=type_id,
                    token=token
                )
            ).primary_key[0]

        await trans.commit()

        return result


async def get_or_create_user(connection, token):
    async with connection.begin() as trans:
        ds = await connection.exec(
            select([
                user.c.id.label("user_id")
            ]).select_from(
                user
            ).where(
                user.c.token == token
            )
        )

        if ds.rowcount:
            result = ds.first()["user_id"]
        else:
            result = await connection.exec(
                user.insert().values(
                    token=token
                )
            ).primary_key[0]

        await trans.commit()

        return result


async def add_or_update_comment_text(connection, comment_id, text):
    text_hash = sha1_str(text)

    async with connection.begin() as trans:
        if not await connection.scalar(
                exists().select_from(comment_text).where(
                    and_(
                        comment_text.c.comment == comment_id,
                        comment_text.c.hash == text_hash
                    )
                )):
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
