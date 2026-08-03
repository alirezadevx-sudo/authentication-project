from datetime import datetime, timedelta, timezone
from services.email_service import send_email
import uuid
from fastapi.responses import JSONResponse
from core.jwt import create_access_token, create_refresh_token, get_current_user_refresh_token, create_resend_email_token
from fastapi import APIRouter, status, Depends, BackgroundTasks
from typing import Annotated
from db.models import Users, Session
from db.database import DB_dependency
from schemes.auth import CreateUserReq, CreateUserRes, Token
from core.crud import fetch_user_email, fetch_user_username, fetch_user_id, fetch_session
from schemes.exeptions import BasRequestErr, ExeptionErr, NotFoundErr, UnAuthorizedErr
from core.security import hash_password, verify_password, hash_token
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(tags=["auth"], prefix="/api/v1/auth")


@router.post(
    "/signin", status_code=status.HTTP_201_CREATED, response_model=CreateUserRes
)
async def create_user(db: DB_dependency, user_req: CreateUserReq, background_tasks: BackgroundTasks):
    try:
        username_exists = await fetch_user_username(db, user_req.username)
        if username_exists:
            raise BasRequestErr(msg="Username already exists")

        email_exists = await fetch_user_email(db, user_req.email)
        if email_exists:
            raise BasRequestErr(msg="Email already exists")

        user_date = user_req.model_dump()
        user_date["password"] = hash_password(user_date["password"])
        user_model = Users(**user_date, email_is_verified=False)

        email_verification_token = create_resend_email_token({'email': user_model.email, 'type': 'resend'})

        background_tasks.add_task(send_email, user_model.email, email_verification_token)


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
async def login_user(
    db: DB_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    try:
        user = await fetch_user_username(db, form_data.username)
        if user is None:
            raise NotFoundErr(msg="User Not Found")

        if not verify_password(form_data.password, user.password):
            raise UnAuthorizedErr(msg="Invalid Credentioals")

        if not user.email_is_verified:
            raise UnAuthorizedErr(msg='Please verify your email')

        access_token = create_access_token(
            {"sub": str(user.id), "type": "bearer", "role": user.role}
        )

        refresh_id = uuid.uuid4()

        print("refresh_id: ", refresh_id)

        refresh_token = create_refresh_token(
            {"refresh_id": str(refresh_id), "type": "refresh", "user_id": user.id}
        )

        print("refresh_token: ", refresh_token)

        session_model = Session(
            id=refresh_id,
            user_id=user.id,
            refresh_token_hash=hash_token(refresh_token),
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )

        print("refresh_model: ", session_model)

        db.add(session_model)
        await db.commit()

        response = JSONResponse(
            content={'access_token': access_token, 'token_type': 'bearer'}
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            path='/',
            httponly=True,
            secure=False
        )

        return response

    except NotFoundErr:
        await db.rollback()
        raise
    except UnAuthorizedErr:
        await db.rollback()
        raise
    except Exception as ex:
        await db.rollback()
        raise ExeptionErr(msg=str(ex))

@router.post("/refresh", status_code=status.HTTP_200_OK, response_model=Token)
async def refresh_token(db: DB_dependency, session: Annotated[Session, Depends(get_current_user_refresh_token)]):
    try:
        user = await fetch_user_id(db, session.user_id)
        if user is None:
            raise NotFoundErr(msg='User Not Found!')

        refresh_id = uuid.uuid4()

        access_token = create_access_token({'sub': str(user.id), 'role': user.role, "type": "bearer"})
        new_refresh_token = create_refresh_token({'refresh_id': str(refresh_id), 'type': 'refresh', 'user_id': user.id})

        old_session = await fetch_session(db, user.id, session.id)
        if old_session is None:
            raise NotFoundErr(msg='Session Not Found!')

        session_model = Session(
            id=refresh_id,
            user_id=user.id,
            refresh_token_hash=hash_token(new_refresh_token),
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )

        old_session.revoked = True
        old_session.last_refreshed_at = datetime.now(timezone.utc)

        db.add(session_model)
        await db.commit()
        await db.refresh(session_model)

        response = JSONResponse(
            content={'access_token': access_token, 'token_type': 'bearer'}
        )

        response.set_cookie(
            key='refresh_token',
            value=new_refresh_token,
            path='/',
            httponly=True,
            secure=False
        )

        return response

    except NotFoundErr:
        await db.rollback()
        raise
    except Exception as ex:
        await db.rollback()
        raise ExeptionErr(msg=f"Refresh token error: {str(ex)}")


@router.post('/logout', status_code=status.HTTP_204_NO_CONTENT)
async def logout_user(db: DB_dependency, session: Annotated[Session, Depends(get_current_user_refresh_token)]):
    try:
        session.revoked = True
        session.last_refreshed_at = datetime.now(timezone.utc)

        await db.commit()
        response = JSONResponse(
            content={
                'msg': 'Loged out successfully!'
            }
        )

        response.delete_cookie(
            path='/',
            key='refresh_token',
            secure=False,
            httponly=True
        )

        return response

    except Exception as ex:
        await db.rollback()
        raise ExeptionErr(msg=f"logout Error: {str(ex)}")