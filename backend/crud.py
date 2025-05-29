from typing import List, Optional
from datetime import datetime
from database import database
from models import users, chats, chat_participants, messages, user_tokens
from schemas import UserCreate, UserOut, MessageCreate, MessageOut, ChatOut


# ----- USERS -----

async def get_user_by_id(user_id: int) -> Optional[UserOut]:
    query = users.select().where(users.c.id == user_id)
    user_record = await database.fetch_one(query)
    if user_record:
        return UserOut.from_orm(user_record)
    return None

async def get_user_by_email(email: str) -> Optional[UserOut]:
    query = users.select().where(users.c.email == email)
    user_record = await database.fetch_one(query)
    if user_record:
        return UserOut.from_orm(user_record)
    return None

async def create_user(user: UserCreate) -> UserOut:
    query = users.insert().values(
        full_name=user.full_name,
        email=user.email,
        phone_no=user.phone_no,
        hashed_password=user.hashed_password,
        profile_pic_url=user.profile_pic_url,
        status=user.status,
        created_at=datetime.utcnow(),
    )
    user_id = await database.execute(query)
    return await get_user_by_id(user_id)

async def update_user(user_id: int, password_hash: Optional[str], profile_pic_url: Optional[str], status: Optional[str]) -> Optional[UserOut]:
    values = {}
    if password_hash is not None:
        values["hashed_password"] = password_hash
    if profile_pic_url is not None:
        values["profile_pic_url"] = profile_pic_url
    if status is not None:
        values["status"] = status
    if not values:
        return await get_user_by_id(user_id)
    query = users.update().where(users.c.id == user_id).values(**values)
    await database.execute(query)
    return await get_user_by_id(user_id)

async def search_users(query_str: str, exclude_user_id: int) -> List[UserOut]:
    query = users.select().where(
        users.c.id != exclude_user_id
    ).where(
        (users.c.full_name.ilike(f"%{query_str}%")) | (users.c.email.ilike(f"%{query_str}%"))
    ).limit(20)
    rows = await database.fetch_all(query)
    return [UserOut.from_orm(row) for row in rows]



# ----- CHATS -----

async def get_chat_by_users(user1_id: int, user2_id: int) -> Optional[ChatOut]:
    query = (
        chats.select()
        .join(chat_participants, chats.c.id == chat_participants.c.chat_id)
        .where(chat_participants.c.user_id.in_([user1_id, user2_id]))
        .group_by(chats.c.id)
        .having(database.func.count(chat_participants.c.user_id) == 2)
        .limit(1)
    )
    chat_record = await database.fetch_one(query)
    if chat_record:
        return ChatOut.from_orm(chat_record)
    return None

async def create_chat(user1_id: int, user2_id: int) -> ChatOut:
    query = chats.insert().values(created_at=datetime.utcnow())
    chat_id = await database.execute(query)

    await database.execute(chat_participants.insert().values(chat_id=chat_id, user_id=user1_id, joined_at=datetime.utcnow()))
    await database.execute(chat_participants.insert().values(chat_id=chat_id, user_id=user2_id, joined_at=datetime.utcnow()))

    return await get_chat_by_id(chat_id)

async def get_chat_by_id(chat_id: int) -> Optional[ChatOut]:
    query = chats.select().where(chats.c.id == chat_id)
    chat_record = await database.fetch_one(query)
    if chat_record:
        return ChatOut.from_orm(chat_record)
    return None

async def list_user_chats(user_id: int) -> List[ChatOut]:
    query = (
        chats.select()
        .join(chat_participants, chats.c.id == chat_participants.c.chat_id)
        .where(chat_participants.c.user_id == user_id)
    )
    rows = await database.fetch_all(query)
    return [ChatOut.from_orm(row) for row in rows]

async def remove_chat(chat_id: int, user_id: int):
    # Remove the user from chat participants
    query = chat_participants.delete().where(
        (chat_participants.c.chat_id == chat_id) & (chat_participants.c.user_id == user_id)
    )
    await database.execute(query)


# ----- MESSAGES -----

async def create_message(chat_id: int, sender_id: int, text: Optional[str], file_url: Optional[str]) -> MessageOut:
    query = messages.insert().values(
        chat_id=chat_id,
        sender_id=sender_id,
        text=text,
        file_url=file_url,
        timestamp=datetime.utcnow(),
    )
    message_id = await database.execute(query)
    return await get_message_by_id(message_id)

async def get_message_by_id(message_id: int) -> Optional[MessageOut]:
    query = messages.select().where(messages.c.id == message_id)
    message_record = await database.fetch_one(query)
    if message_record:
        return MessageOut.from_orm(message_record)
    return None

async def get_messages(chat_id: int, limit: int, offset: int) -> List[MessageOut]:
    query = (
        messages.select()
        .where(messages.c.chat_id == chat_id)
        .order_by(messages.c.timestamp.desc())
        .limit(limit)
        .offset(offset)
    )
    rows = await database.fetch_all(query)
    return [MessageOut.from_orm(row) for row in rows]


# ----- USER TOKENS (for blacklisting etc) -----

async def add_token_to_blacklist(token: str, expires_at: datetime):
    ttl = int((expires_at - datetime.utcnow()).total_seconds())
    if ttl > 0:
        await redis_client.setex(f"blacklist:{token}", ttl, "true")

async def is_token_blacklisted(token: str) -> bool:
    val = await redis_client.get(f"blacklist:{token}")
    return val is not None
