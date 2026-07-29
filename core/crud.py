from sqlalchemy import select
from db.database import DB_dependency
from db.models import Users

async def fetch_user_username(db: DB_dependency, username: str):
    result = await db.execute(select(Users).where(Users.username == username))
    return result.scalar_one_or_none()

async def fetch_user_email(db: DB_dependency, email: str):
    result = await db.execute(select(Users).where(Users.email == email))
    return result.scalar_one_or_none()