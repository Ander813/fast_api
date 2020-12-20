from fastapi import APIRouter, Depends

from .models import User
from .schemas import UserOut, UserIn
from .services import users_s
from ..auth.permissions import get_superuser

admin_router = APIRouter()


@admin_router.get('/',
                  response_model=list[UserOut])
async def get_users_list(user: User = Depends(get_superuser)):
    return await users_s.all()


@admin_router.get('/{pk}')
async def get_user(pk: int, user: User = Depends(get_superuser)):
    return await users_s.get(id=pk)


@admin_router.delete('/{pk}')
async def delete_user(pk: int, user: User = Depends(get_superuser)):
    return await users_s.delete(id=pk)


@admin_router.put('/{pk}')
async def update_user(pk: int,
                      user_data: UserIn,
                      user: User = Depends(get_superuser)):
    return await users_s.update(user_data, id=pk)


@admin_router.post('/')
async def create_user(user_data: UserIn,
                      user: User = Depends(get_superuser)):
    return await users_s.create(user_data)