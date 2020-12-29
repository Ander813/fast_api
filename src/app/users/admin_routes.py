from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, pagination_params
from fastapi_pagination.params import resolve_params

from .filters import UserAdminFilter
from .models import User
from .schemas import UserOutAdmin, UserInAdmin
from .services import users_s, users_s_admin
from ..auth.permissions import get_superuser
from ..base.csrf import ensure_csrf, validate_csrf

admin_router = APIRouter()


@admin_router.get(
    "/",
    response_model=Page[UserOutAdmin],
    dependencies=[Depends(pagination_params)],
    responses={400: {"description": "Bad queryset"}},
    dependencies=[Depends(ensure_csrf)],
)
async def get_users_list(
    user: User = Depends(get_superuser), filter: UserAdminFilter = Depends()
):
    params = resolve_params(None)
    limit_offset = params.to_limit_offset()
    items = await users_s_admin.get_slice(
        limit_offset.offset, limit_offset.limit, filter_obj=filter
    )
    if items is not None:
        return Page.create(items=items, total=await User.all().count(), params=params)
    raise HTTPException(status_code=400, detail="wrong parameters given")


@admin_router.get(
    "/{pk}", response_model=UserOutAdmin, dependencies=[Depends(ensure_csrf)]
)
async def get_user(pk: int, user: User = Depends(get_superuser)):
    return await users_s.get(id=pk)


@admin_router.delete("/{pk}", dependencies=[Depends(validate_csrf)])
async def delete_user(pk: int, user: User = Depends(get_superuser)):
    return await users_s.delete(id=pk)


@admin_router.put("/{pk}", dependencies=[Depends(validate_csrf)])
async def update_user(
    pk: int, user_data: UserInAdmin, user: User = Depends(get_superuser)
):
    return await users_s.update(user_data, id=pk)


@admin_router.post("/", dependencies=[validate_csrf])
async def create_user(user_data: UserInAdmin, user: User = Depends(get_superuser)):
    return await users_s.create(user_data)
