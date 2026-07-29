from fastapi import Depends
from typing import Annotated
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from db.DbSettings import db_settings

engine = create_async_engine(db_settings.DB_URL.get_secret_value() ,echo=True, future=True)

SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with SessionLocal() as session:
        yield session

DB_dependency = Annotated[AsyncSession, Depends(get_db)]