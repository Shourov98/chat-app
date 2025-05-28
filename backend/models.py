from sqlalchemy import Table, Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Users table
from sqlalchemy import MetaData

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("full_name", String(length=100), nullable=False),
    Column("email", String(length=100), nullable=True),       # optional and NOT unique as per your requirement
    Column("phone_no", String(length=20), nullable=True),      # optional and NOT unique as per your requirement
    Column("hashed_password", String(length=255), nullable=False),
    Column("profile_pic_url", String(length=255), nullable=True),
    Column("status", String(length=255), nullable=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), onupdate=func.now()),
)

chats = Table(
    "chats",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)

chat_participants = Table(
    "chat_participants",
    metadata,
    Column("chat_id", Integer, ForeignKey("chats.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("joined_at", DateTime(timezone=True), server_default=func.now()),
)

messages = Table(
    "messages",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("chat_id", Integer, ForeignKey("chats.id")),
    Column("sender_id", Integer, ForeignKey("users.id")),
    Column("text", Text, nullable=True),
    Column("file_url", String(length=255), nullable=True),
    Column("timestamp", DateTime(timezone=True), server_default=func.now()),
)

user_tokens = Table(
    "user_tokens",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("token", String(length=500)),
    Column("issued_at", DateTime(timezone=True), server_default=func.now()),
    Column("expires_at", DateTime(timezone=True)),
    Column("revoked", Boolean, default=False),
)
