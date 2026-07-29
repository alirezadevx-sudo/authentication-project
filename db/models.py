from datetime import datetime
from db.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func,  String

class Users(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(primary_key=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(250), nullable=False)
    email: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    role: Mapped[str] = mapped_column(default='user')
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    