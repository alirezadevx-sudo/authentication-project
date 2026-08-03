from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select
from db.database import DB_dependency
from db.models import Users, Session


async def fetch_user_username(db: DB_dependency, username: str):
    result = await db.execute(select(Users).where(Users.username == username))
    return result.scalar_one_or_none()


async def fetch_user_email(db: DB_dependency, email: str):
    result = await db.execute(select(Users).where(Users.email == email))
    return result.scalar_one_or_none()


async def fetch_user_id(db: DB_dependency, id: int):
    result = await db.execute(select(Users).where(Users.id == id))
    return result.scalar_one_or_none()


async def fetch_session(db: DB_dependency, user_id: int, refresh_id: UUID):
    result = await db.execute(
        select(Session).where(
            Session.user_id == user_id,
            Session.id == refresh_id,
            Session.revoked == False,
            Session.expires_at > datetime.now(timezone.utc),
            Session.last_refreshed_at.is_(None)
        )
    )
    return result.scalar_one_or_none()
