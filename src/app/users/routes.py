from fastapi import APIRouter
from src.app.users.schemas import UserIn, UserOut
from src.app.users.models import User


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