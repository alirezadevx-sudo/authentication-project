from core.jwt import create_jwt_token
from fastapi import APIRouter, status, Depends
from typing import Annotated
from db.models import Users
from db.database import DB_dependency
from schemes.auth import (CreateUserReq, CreateUserRes, Token)
from core.crud import (fetch_user_email, fetch_user_username)
from schemes.exeptions import BasRequestErr, ExeptionErr, NotFoundErr, UnAuthorizedErr
from core.security import hash_password, verify_password
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(tags=['auth'], prefix='/api/v1/auth')

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

@router.post("/login", status_code=status.HTTP_200_OK, response_model=Token)
async def login_user(db: DB_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    try:
        user = await fetch_user_username(db, form_data.username)
        if user is None:
            raise NotFoundErr(msg="User Not Found")

        if not verify_password(form_data.password, user.password):
            raise UnAuthorizedErr(msg="Invalid Credentioals")

        token = create_jwt_token({'sub': user.username, 'id': user.id, 'role': user.role})
        return {'access_token': token}

    except NotFoundErr:
        raise
    except UnAuthorizedErr:
        raise
    except Exception as ex:
        raise ExeptionErr(msg=str(ex))
