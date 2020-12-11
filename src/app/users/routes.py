from fastapi import APIRouter, HTTPException
from .schemas import UserIn, UserOut
from .services import users_s


router = APIRouter()


@router.get('/',
            response_model=list[UserOut])
async def get_users_list():
    return await users_s.all()

