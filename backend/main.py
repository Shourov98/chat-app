from fastapi import FastAPI, Request
from routers import auth
from config import settings
from database import database
from jose import jwt, JWTError
from datetime import datetime, timedelta

app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=["auth"])

@app.middleware("http")
async def refresh_token_middleware(request: Request, call_next):
    response = await call_next(request)
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])
            exp = payload.get("exp")
            if exp:
                expires_in = exp - int(datetime.utcnow().timestamp())
                if expires_in < 15 * 60:  # 15 minutes threshold
                    new_token = jwt.encode(
                        {"sub": payload.get("sub"),
                        "exp": datetime.now(datetime.timezone.utc) + timedelta(minutes=60)},
                        settings.jwt_secret_key,
                        algorithm="HS256"
                    )
                    response.headers["X-New-Token"] = new_token
        except JWTError:
            pass
    return response


@app.get("/")
async def root():
    return {"message": "Welcome to your chat backend!"}

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/config")
def get_config():
    return {
        "database_url": settings.database_url,
        "cloudinary": settings.cloudinary_cloud_name,
    }

