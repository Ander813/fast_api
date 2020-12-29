from fastapi import APIRouter, HTTPException, Depends
from fastapi_pagination.params import resolve_params
from tortoise.contrib.fastapi import HTTPNotFoundError

from fastapi_pagination import Page, pagination_params

from src.app.auth.permissions import get_superuser
from src.app.base.schemas import Msg
from .filters import RecordAdminFilter
from .models import Record
from .schemas import RecordIn, RecordOutAdmin, RecordInAdmin
from .services import records_s_admin
from src.app.users.models import User
from ..base.csrf import ensure_csrf, validate_csrf

admin_router = APIRouter()


@admin_router.get(
    "/",
    response_model=Page[RecordOutAdmin],
    dependencies=[Depends(pagination_params), Depends(ensure_csrf)],
    responses={400: {"detail": "Bad queryset"}},
)
async def get_records(
    user: User = Depends(get_superuser), filter: RecordAdminFilter = Depends()
):
    params = resolve_params(None)
    limit_offset = params.to_limit_offset()
    items = await records_s_admin.get_slice(
        limit_offset.offset, limit_offset.limit, filter_obj=filter
    )
    if items is not None:
        return Page.create(items=items, total=await Record.all().count(), params=params)
    raise HTTPException(status_code=400, detail="wrong parameters given")


@admin_router.get(
    "/{id}",
    response_model=RecordOutAdmin,
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[Depends(ensure_csrf)],
)
async def get_record(id: int, user: User = Depends(get_superuser)):
    return await records_s_admin.get(id=id)


@admin_router.post(
    "/",
    response_model=RecordOutAdmin,
    status_code=201,
    dependencies=[Depends(validate_csrf)],
)
async def create_record(record: RecordIn, user: User = Depends(get_superuser)):
    return await records_s_admin.create(record, creator_id=user.id)


@admin_router.put(
    "/{pk}",
    responses={404: {"Description": "not found"}},
    dependencies=[Depends(validate_csrf)],
)
async def update_record(
    pk: int, record: RecordInAdmin, user: User = Depends(get_superuser)
):
    return await records_s_admin.update(record, id=pk)


@admin_router.delete(
    "/{pk}",
    response_model=Msg,
    responses={404: {"Description": "not found"}},
    dependencies=[Depends(validate_csrf)],
)
async def delete_record(pk: int, user: User = Depends(get_superuser)):
    if await records_s_admin.delete(id=pk):
        return {"msg": "deleted"}
    else:
        raise HTTPException(status_code=404, detail="object not found")
