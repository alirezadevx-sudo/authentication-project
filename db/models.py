from uuid import UUID
from datetime import datetime
from db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import func, String, Text, ForeignKey

class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(250), nullable=False)
    email: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    role: Mapped[str] = mapped_column(default='user')
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    sessions: Mapped[list['Session']] = relationship('Session', back_populates='user', cascade='all, delete-orphan')


class Session(Base):
    __tablename__ = 'sessions'

    id: Mapped[UUID] = mapped_column(index=True, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    refresh_token_hash: Mapped[str] = mapped_column(Text)
    expires_at: Mapped[datetime]
    revoked: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    user: Mapped['Users'] = relationship('Users', back_populates='sessions')
    