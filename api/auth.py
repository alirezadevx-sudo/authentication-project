from fastapi import APIRouter, status
from db.models import Users
from db.database import DB_dependency
from schemes.auth import (CreateUserReq, CreateUserRes,)
from core.crud import (fetch_user_email, fetch_user_username)
from schemes.exeptions import BasRequestErr, ExeptionErr
from core.security import hash_password

router = APIRouter()

@router.post("/signin", status_code=status.HTTP_201_CREATED, response_model=CreateUserRes)
async def create_user(db: DB_dependency, user_req: CreateUserReq):
    try:
        username_exists = await fetch_user_username(db, user_req.username)
        if username_exists:
            raise BasRequestErr(msg="Username already exists")

        email_exists = await fetch_user_email(db, user_req.email)
        if email_exists:
            raise BasRequestErr(msg="Email already exists")

        user_date = user_req.model_dump()
        user_date['password'] = hash_password(user_date["password"])
        user_model = Users(**user_date)

        db.add(user_model)
        await db.commit()
        await db.refresh(user_model)
        return user_model

    except BasRequestErr:
        await db.rollback()
        raise
    except Exception as ex:
        await db.rollback()
        raise ExeptionErr(msg=str(ex))


