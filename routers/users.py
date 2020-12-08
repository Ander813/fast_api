from fastapi import APIRouter
from schemas.users import UserIn, UserOut
from models.users import User


router = APIRouter()


@router.post('/',
             response_model=UserOut,
             status_code=201)
async def register(user: UserIn):
    user = await User.create_user(**user.dict())
    return await UserOut.from_tortoise_orm(user)


@router.get('/',
            response_model=list[UserOut])
async def get_users_list():
    return await UserOut.from_queryset(User.all())