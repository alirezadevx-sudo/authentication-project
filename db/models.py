from uuid import UUID
import uuid
from datetime import datetime
from db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import func, String, Text, ForeignKey, DateTime, Boolean, Integer
from typing import Optional


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(250), nullable=False)
    email: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    role: Mapped[str] = mapped_column(default="user")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    email_is_verified: Mapped[bool] = mapped_column(nullable=False, default=False)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, nullable=False, server_default='0')
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    sessions: Mapped[list["Session"]] = relationship(
        "Session", back_populates="user", cascade="all, delete-orphan"
    )
    password_resets: Mapped[list["PasswordReset"]] = relationship(
        "PasswordReset", back_populates="user", cascade="all, delete-orphan"
    )


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    refresh_token_hash: Mapped[str] = mapped_column(Text, nullable=False)
    last_refreshed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    revoked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    user: Mapped["Users"] = relationship("Users", back_populates="sessions")


class PasswordReset(Base):
    __tablename__ = "password_resets"

    id: Mapped[UUID] = mapped_column(
        index=True, primary_key=True, nullable=False, default=uuid.uuid4
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    token_hash: Mapped[str] = mapped_column(Text, nullable=False)

    used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    revoked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user: Mapped["Users"] = relationship("Users")
