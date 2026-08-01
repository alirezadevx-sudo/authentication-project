from core.crud import fetch_user_id
from schemes.auth import CreateUserRes
from core.jwt import CurrentUser
from db.database import DB_dependency
from fastapi import APIRouter, status

router = APIRouter()

@router.get('/me', status_code=status.HTTP_200_OK, response_model=CreateUserRes)
async def get_me(db: DB_dependency, current_user: CurrentUser):
    user = await fetch_user_id(db, current_user.id)
    return user