from db.models import Users
from typing import Annotated
from schemes.exeptions import UnAuthorizedErr, ExeptionErr
from core.jwt import verify_resend_email
from fastapi import APIRouter, status, Depends
from db.database import DB_dependency


router = APIRouter(prefix='/api/auth/verification', tags=['verification'])

@router.post("/verify_email", status_code=status.HTTP_200_OK)
async def verify_email(db: DB_dependency, user: Annotated[Users, Depends(verify_resend_email)]):
    try:
        if user is None:
            raise UnAuthorizedErr(msg="Invalid Credentioals")

        user.email_is_verified = True

        await db.commit()
        return {"msg": 'Your email has been verified'}

    except UnAuthorizedErr:
        raise
    except Exception as ex:
        raise ExeptionErr(msg=f'Email verification failed: {str(ex)}')