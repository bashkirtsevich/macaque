from sqlalchemy import Column, Integer, MetaData, Table, Text, ForeignKey, UniqueConstraint, DateTime

metadata = MetaData()

entity_type = Table(
    "entity_type", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", nullable=False, index=True, unique=True),
)

entity = Table(
    "entity", metadata,
    Column("id", Integer, primary_key=True),
    Column("type", ForeignKey("entity_type.id"), index=True, nullable=False),
    Column("token", nullable=False, index=True),
    UniqueConstraint("type", "token"),
)

user = Table(
    "user", metadata,
    Column("id", Integer, primary_key=True),
    Column("token", nullable=False, index=True, unique=True),
)

comment = Table(
    "comment", metadata,
    Column("id", Integer, primary_key=True),
    Column("entity", ForeignKey("entity.id"), index=True, nullable=False),
    Column("user", ForeignKey("user.id"), index=True, nullable=False),
    Column("comment", ForeignKey("comment.id"), index=True),
    Column("key", Text, index=True),
)

comment_text = Table(
    "comment_text", metadata,
    Column("id", Integer, primary_key=True),
    Column("comment", ForeignKey("comment.id"), index=True, nullable=False),
    Column("timestamp", DateTime, index=True, nullable=False),
    Column("hash", Text, index=True),
    Column("data", Text),
)
