from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
import redis.asyncio as redis
from typing import Optional
from fastapi.security import OAuth2PasswordBearer
from crud import get_user_by_id
from schemas import UserCreate, UserOut
from crud import create_user, get_user_by_email
from config import settings
from database import database

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
redis_client = redis.from_url(settings.redis_url)

SECRET_KEY = settings.jwt_secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
TOKEN_REFRESH_THRESHOLD_MINUTES = 15  # When to refresh token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def is_token_revoked(token: str) -> bool:
    revoked = await redis_client.get(f"blacklist:{token}")
    return revoked is not None


async def revoke_token(token: str, exp_timestamp: int):
    ttl = exp_timestamp - int(datetime.utcnow().timestamp())
    if ttl > 0:
        await redis_client.setex(f"blacklist:{token}", ttl, "true")


async def authenticate_user(username: str, password: str):
    user = await get_user_by_email(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserOut:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    if await is_token_revoked(token):
        raise HTTPException(status_code=401, detail="Token has been revoked")

    user = await get_user_by_id(int(user_id))
    if user is None:
        raise credentials_exception

    return user


@router.post("/signup", response_model=UserOut)
async def signup(user: UserCreate):
    existing_user = await get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user.hashed_password = get_password_hash(user.password)
    new_user = await create_user(user)
    return new_user


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": str(user.id)})
    expires_at = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_at": expires_at.isoformat(),
    }


@router.post("/logout")
async def logout(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp = payload.get("exp")
        if not exp:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    await revoke_token(token, exp)
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserOut)
async def read_users_me(current_user: UserOut = Depends(get_current_user)):
    return current_user

