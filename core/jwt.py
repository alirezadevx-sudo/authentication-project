from schemes.exeptions import NotFoundErr, ExeptionErr
from core.crud import fetch_user_username
from fastapi import Depends
from typing import Annotated
from db.database import DB_dependency
from datetime import datetime, timezone, timedelta
from core.CoreSettings import core_settings
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi.security import OAuth2PasswordBearer



oauth2_sheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/login')

def create_jwt_token(payload: dict) -> str:

    payload_with_iat = payload.copy()
    payload.update({'exp': datetime.now(timezone.utc) + timedelta(minutes=int(30))})
    return jwt.encode(payload_with_iat, core_settings.SECRET_KEY, algorithm=core_settings.ALGORITHM)

async def get_current_user(db: DB_dependency, token: Annotated[str, Depends(oauth2_sheme)]):
    try:
        payload = jwt.decode(token, key=core_settings.SECRET_KEY, algorithms=[core_settings.ALGORITHM])
        username: str = payload.get('sub')
        id: int = payload.get('id')
        role: str = payload.get('role')

        if username is None or id is None or role is None:
            raise InvalidTokenError

        user = await fetch_user_username(db, username)
        if user is None:
            raise NotFoundErr(msg='User Not Found!')

        return user

    except InvalidTokenError:
        raise 
    except NotFoundErr:
        raise
    except Exception as ex:
        raise ExeptionErr(msg=str(ex))

    