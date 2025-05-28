from sqlalchemy import create_engine
from models import metadata
from config import settings

engine = create_engine(settings.database_url)

metadata.create_all(engine)
print("Tables created")
