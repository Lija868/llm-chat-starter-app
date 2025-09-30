from database import database
from models import users, messages
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
MAX_PASSWORD_LEN = 72

def hash_password(password: str):
    return pwd_context.hash(password[:MAX_PASSWORD_LEN])

def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain[:MAX_PASSWORD_LEN], hashed)

async def get_user_by_email(email: str):
    query = users.select().where(users.c.email == email)
    return await database.fetch_one(query)

async def get_user_by_id(user_id: int):
    query = users.select().where(users.c.id == user_id)
    return await database.fetch_one(query)

async def create_user(email: str, password: str, name: str | None = None):
    hashed = hash_password(password)
    print(hashed, "*********************")
    query = users.insert().values(email=email, hashed_password=hashed, name=name)
    user_id = await database.execute(query)
    return {"id": user_id, "email": email, "name": name}
