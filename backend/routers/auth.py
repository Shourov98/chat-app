from fastapi import APIRouter, Depends, HTTPException, status
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
    token = create_access_token({"sub": str(new_user.id)})
    return {"user": new_user, "token": token}
