from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, EmailStr, ConfigDict

class CreateUserReq(BaseModel):
    username: str = Field(..., min_length=3, max_length=250, pattern=r'^[a-zA-Z\d\@\.\,\_\-]+$', examples=['alipro123'])
    email: EmailStr = Field(..., min_length=3, max_length=250, examples=['alrezaqurani@gmail.com'])
    password: str = Field(..., min_length=4)
    role: Literal['admin', 'user'] = Field(default='user')


class CreateUserRes(BaseModel):
    id: int
    username: str
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    