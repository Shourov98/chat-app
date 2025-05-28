from databases import Database
from config import settings  # your config loader

database = Database(settings.database_url)
