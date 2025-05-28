from models import users
from database import database
from schemas import UserCreate, UserOut
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_user_by_email(email: str) -> UserOut | None:
    query = users.select().where(users.c.email == email)
    user_record = await database.fetch_one(query)
    if user_record:
        return UserOut.from_orm(user_record)
    return None

async def create_user(user: UserCreate) -> UserOut:
    hashed_password = pwd_context.hash(user.password)
    query = users.insert().values(
        full_name=user.full_name,
        email=user.email,
        phone_no=user.phone_no,
        hashed_password=hashed_password,
        profile_pic_url=user.profile_pic_url,
        status=user.status,
    )
    user_id = await database.execute(query)
    return UserOut(id=user_id, **user.dict(exclude={"password"}))
