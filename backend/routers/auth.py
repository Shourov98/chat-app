from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from schemas import UserCreate, UserOut
from crud import create_user, get_user_by_email
from auth import create_access_token, verify_password
from database import database

router = APIRouter()

@router.post("/signup", response_model=UserOut)
async def signup(user: UserCreate):
    existing_user = await get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = await create_user(user)
    return new_user


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # form_data.username could be email or phone no as you prefer
    user = await get_user_by_email(form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}
