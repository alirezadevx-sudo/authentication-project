from core.security import verify_token
from uuid import UUID
from fastapi import Cookie, Depends, Query
from schemes.exeptions import NotFoundErr, UnAuthorizedErr
from db.models import Users, Session
from core.crud import fetch_user_id, fetch_session, fetch_user_email
from typing import Annotated
from db.database import DB_dependency
from datetime import datetime, timezone, timedelta
from core.CoreSettings import core_settings
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi.security import OAuth2PasswordBearer

oauth2_sheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/login')

def create_access_token(payload: dict) -> str:
    token = payload.copy()
    token.update({'exp': datetime.now(timezone.utc) + timedelta(minutes=int(30))})
    return jwt.encode(token, core_settings.SECRET_KEY, algorithm=core_settings.ALGORITHM)

def create_refresh_token(payload: dict) -> str:
    token = payload.copy()
    token.update({'exp': datetime.now(timezone.utc) + timedelta(days=7)})
    return jwt.encode(token, core_settings.SECRET_KEY, algorithm=core_settings.ALGORITHM)

def create_resend_email_token(payload: dict) -> str:
    token = payload.copy()
    token.update({'exp': datetime.now(timezone.utc) + timedelta(hours=1)})
    return jwt.encode(token, key=core_settings.SECRET_KEY, algorithm=core_settings.ALGORITHM)

async def get_current_user_access_token(db: DB_dependency, token: Annotated[str, Depends(oauth2_sheme)]):
    try:
        payload = jwt.decode(token, key=core_settings.SECRET_KEY, algorithms=[core_settings.ALGORITHM])
        id: int = int(payload.get('sub'))
        type: str = payload.get('type')
        role: str = payload.get('role')

        if type != "bearer":
            raise InvalidTokenError()

        if id is None or type is None or role is None:
            raise InvalidTokenError()

        user = await fetch_user_id(db, id)
        if user is None:
            raise NotFoundErr(msg='User Not Found!')
        
        return user

    except InvalidTokenError:
        raise 
    except NotFoundErr:
        raise
    except Exception as ex:
        raise

def is_valid_refresh_session(session: Session | None, refresh_token: str) -> bool:
    if session is None:
        return False
    if session.revoked:
        return False
    if not verify_token(refresh_token, session.refresh_token_hash):
        return False
    if session.last_refreshed_at is not None:
        return False
    return session.expires_at > datetime.now(timezone.utc)


async def get_current_user_refresh_token(db: DB_dependency, refresh_token: Annotated[str | None, Cookie()] = None):

    if refresh_token is None:
        raise UnAuthorizedErr(msg='Missing Refresh Token!')

    payload = jwt.decode(refresh_token, key=core_settings.SECRET_KEY, algorithms=[core_settings.ALGORITHM])
    refresh_id: str = payload.get('refresh_id')
    token_type: str = payload.get('type')
    user_id: int = payload.get("user_id")

    if token_type != 'refresh':
        raise InvalidTokenError()

    if user_id is None or token_type is None or refresh_id is None:
        raise InvalidTokenError()

    session = await fetch_session(db, user_id, UUID(refresh_id))
    if not is_valid_refresh_session(session, refresh_token):
        raise UnAuthorizedErr(msg='Refresh token mismatch or session revoked')

    return session

async def verify_resend_email(db: DB_dependency, token: str = Query(...)):
    payload = jwt.decode(token, key=core_settings.SECRET_KEY, algorithms=[core_settings.ALGORITHM])

    if payload.get("type") != 'resend':
        raise InvalidTokenError()

    email: str = payload.get('email')

    user = await fetch_user_email(db, email=email)
    if user is None:
        raise NotFoundErr(msg="User Not Found!")

    return user

CurrentUser = Annotated[Users, Depends(get_current_user_access_token)]