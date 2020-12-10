from fastapi import APIRouter
from .schemas import UserIn, UserOut
from .services import users_s


router = APIRouter()


@router.post('/',
             response_model=UserOut,
             status_code=201)
async def register(user: UserIn):
    return await users_s.create_user(user)


@router.get('/',
            response_model=list[UserOut])
async def get_users_list():
    return await users_s.all()