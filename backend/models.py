from sqlalchemy import Table, Column, Integer, String, ForeignKey, Text, DateTime, func
from database import metadata

users = Table(
    "users", metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, unique=True, nullable=False),
    Column("hashed_password", String, nullable=False),
    Column("name", String, nullable=True),
    Column("created_at", DateTime, server_default=func.now()),
)

chats = Table(
    "chats", metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete='CASCADE')),
    Column("title", String, nullable=False),
    Column("created_at", DateTime, server_default=func.now()),
)

messages = Table(
    "messages", metadata,
    Column("id", Integer, primary_key=True),
    Column("chat_id", Integer, ForeignKey("chats.id", ondelete='CASCADE')),
    Column("role", String, nullable=False),
    Column("content", Text, nullable=False),
    Column("created_at", DateTime, server_default=func.now()),
)



files = Table(
    "files",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("chat_id", Integer, ForeignKey("chats.id", ondelete="CASCADE")),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE")),
    Column("filename", String, nullable=False),
    Column("path", String, nullable=False),
    Column("created_at", DateTime, server_default=func.now())
)
