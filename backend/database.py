import os
from databases import Database
from sqlalchemy import MetaData
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
database = Database(DATABASE_URL)
metadata = MetaData()
