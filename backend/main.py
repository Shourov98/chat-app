from fastapi import FastAPI
from config import settings
from database import database

app = FastAPI()

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

