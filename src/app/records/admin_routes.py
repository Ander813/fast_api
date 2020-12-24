from fastapi import APIRouter, HTTPException, Depends
from fastapi_pagination.params import resolve_params
from tortoise.contrib.fastapi import HTTPNotFoundError

from fastapi_pagination import Page, pagination_params

from src.app.auth.permissions import get_superuser
from src.app.base.schemas import Msg
from .filters import RecordAdminFilter
from .models import Record
from .schemas import RecordOut, RecordIn, RecordOutAdmin
from .services import records_s_admin
from src.app.users.models import User

admin_router = APIRouter()


@admin_router.get('/', response_model=Page[RecordOutAdmin], dependencies=[Depends(pagination_params)])
async def get_records(user: User = Depends(get_superuser), filter: RecordAdminFilter = Depends()):
    params = resolve_params(None)
    limit_offset = params.to_limit_offset()
    return Page.create(items=await records_s_admin.get_slice(
        limit_offset.offset, limit_offset.limit, filter_obj=filter),
                       total=await Record.all().count(),
                       params=params)


@admin_router.get('/{id}',
                  response_model=RecordOut,
                  responses={404: {"model": HTTPNotFoundError}})
async def get_record(id: int, user: User = Depends(get_superuser)):
    return await records_s_admin.get(id=id)


@admin_router.post('/',
                   response_model=RecordOut,
                   status_code=201)
async def create_record(record: RecordIn,
                        user: User = Depends(get_superuser)):
    return await records_s_admin.create(record, creator_id=user.id)


@admin_router.put('/{pk}',
                  responses={404: {"Description": "not found"}})
async def update_record(pk: int, record: RecordIn,
                        user: User = Depends(get_superuser)):
    return await records_s_admin.update(record, id=pk)


@admin_router.delete('/{pk}',
                     response_model=Msg,
                     responses={404: {'Description': 'not found'}})
async def delete_record(pk: int,
                        user: User = Depends(get_superuser)):
    if await records_s_admin.delete(id=pk):
        return {'msg': 'deleted'}
    else:
        raise HTTPException(status_code=404, detail='object not found')
