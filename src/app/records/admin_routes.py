from fastapi import APIRouter, HTTPException, Depends
from tortoise.contrib.fastapi import HTTPNotFoundError

from fastapi_pagination import Page, pagination_params
from fastapi_pagination.ext.tortoise import paginate

from src.app.auth.permissions import get_superuser
from src.app.base.schemas import Msg
from .models import Record
from src.app.records.schemas import RecordOut, RecordIn
from src.app.records.services import records_s
from src.app.users.models import User

admin_router = APIRouter()


@admin_router.get('/', response_model=Page[RecordOut], dependencies=[Depends(pagination_params)])
async def get_records(user: User = Depends(get_superuser)):
    return await paginate(Record)


@admin_router.get('/{id}',
                  response_model=RecordOut,
                  responses={404: {"model": HTTPNotFoundError}})
async def get_record(id: int, user: User = Depends(get_superuser)):
    return await records_s.get(id=id)


@admin_router.post('/',
                   response_model=RecordOut,
                   status_code=201)
async def create_record(record: RecordIn,
                        user: User = Depends(get_superuser)):
    return await records_s.create(record, creator_id=user.id)


@admin_router.put('/{pk}',
                  responses={404: {"Description": "not found"}})
async def update_record(pk: int, record: RecordIn,
                        user: User = Depends(get_superuser)):
    return await records_s.update(record, id=pk)


@admin_router.delete('/{pk}',
                     response_model=Msg,
                     responses={404: {'Description': 'not found'}})
async def delete_record(pk: int,
                        user: User = Depends(get_superuser)):
    if await records_s.delete(id=pk):
        return {'msg': 'deleted'}
    else:
        raise HTTPException(status_code=404, detail='object not found')
