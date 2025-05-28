from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    full_name: str
    email: Optional[EmailStr] = None
    phone_no: Optional[str] = None
    profile_pic_url: Optional[str] = None
    status: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    password: Optional[str] = None
    profile_pic_url: Optional[str] = None
    status: Optional[str] = None

class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True


# Chat Schemas
class ChatParticipant(BaseModel):
    user_id: int
    joined_at: datetime

class ChatOut(BaseModel):
    id: int
    participants: List[ChatParticipant]

    class Config:
        orm_mode = True


# Message Schemas
class MessageBase(BaseModel):
    text: Optional[str] = None
    file_url: Optional[str] = None

class MessageCreate(MessageBase):
    pass  # Extend as needed

class MessageOut(MessageBase):
    id: int
    chat_id: int
    sender_id: int
    timestamp: datetime

    class Config:
        orm_mode = True
