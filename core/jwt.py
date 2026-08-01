from fastapi import Cookie
from core.security import verify_token
from schemes.exeptions import NotFoundErr, ExeptionErr, UnAuthorizedErr
from db.models import Users, Session
from core.crud import fetch_user_id, fetch_session
from fastapi import Depends
from typing import Annotated
from db.database import DB_dependency
from datetime import datetime, timezone, timedelta
from core.CoreSettings import core_settings
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi.security import OAuth2PasswordBearer

oauth2_sheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/login')

def create_access_token(payload: dict) -> str:
    payload_with_iat = payload.copy()
    payload_with_iat.update({'exp': datetime.now(timezone.utc) + timedelta(minutes=int(30))})
    return jwt.encode(payload_with_iat, core_settings.SECRET_KEY, algorithm=core_settings.ALGORITHM)

def create_refresh_token(payload: dict) -> str:
    payload_with_iat = payload.copy()
    payload_with_iat.update({'exp': datetime.now(timezone.utc) + timedelta(days=7)})
    return jwt.encode(payload_with_iat, core_settings.SECRET_KEY, algorithm=core_settings.ALGORITHM)

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

async def get_current_user_refresh_token(db: DB_dependency, refresh_token: Annotated[str | None, Cookie()]):
    try:
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

        existing_token = await fetch_session(db, user_id, refresh_id)
        if existing_token is None:
            raise InvalidTokenError()

        if not verify_token(token=refresh_token, hashed_token=existing_token.refresh_token_hash):
            raise UnAuthorizedErr(msg='Token mismatch')

        return existing_token

    except InvalidTokenError:
        raise 
    except UnAuthorizedErr:
        raise 
    except ExeptionErr:
        raise


CurrentUser = Annotated[Users, Depends(get_current_user_access_token)]