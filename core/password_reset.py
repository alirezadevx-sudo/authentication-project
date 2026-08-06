from uuid import UUID
from schemes.exeptions import NotFoundErr, ExeptionErr
from db.database import DB_dependency
from core.CoreSettings import core_settings
from core.security import verify_token
from datetime import datetime, timezone, timedelta
import jwt
from schemes.exeptions import UnAuthorizedErr
from jwt.exceptions import InvalidTokenError
from core.crud import fetch_user_id, fetch_password_reset_token

def create_password_reset_token(payload: dict) -> str:
    token = payload.copy()
    token.update({'exp': datetime.now(timezone.utc) + timedelta(hours=1), 'type': 'password_reset'})
    return jwt.encode(token, key=core_settings.SECRET_KEY, algorithm=core_settings.ALGORITHM)


async def verify_password_reset_token(db: DB_dependency, token: str):
    try:

        payload = jwt.decode(token, key=core_settings.SECRET_KEY, algorithms=[core_settings.ALGORITHM])

        user_id: str = payload.get("sub")
        token_uuid: str = payload.get("token_uuid")

        if payload.get('type') != 'password_reset':
            raise InvalidTokenError()

        user = await fetch_user_id(db, int(user_id))
        if user is None:
            raise NotFoundErr(msg='User Not Found!')

        password_reset_token = await fetch_password_reset_token(db, int(user_id), UUID(token_uuid))
        if password_reset_token is None:
            raise NotFoundErr(msg='NO Password Token Found!')

        if not verify_token(token, password_reset_token.token_hash):
            raise UnAuthorizedErr(msg='Token verification failed')

        return {"password_reset_token": password_reset_token, 'user': user}

    except InvalidTokenError:
        raise
    except NotFoundErr:
        raise
    except UnAuthorizedErr:
        raise
    except Exception as ex:
        raise ExeptionErr(msg=f'Error from verify_password_reset_token: {str(ex)}')