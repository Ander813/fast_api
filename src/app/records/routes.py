from fastapi import APIRouter, HTTPException, Depends
from tortoise.contrib.fastapi import HTTPNotFoundError

from fastapi_pagination import Page, pagination_params
from fastapi_pagination.ext.tortoise import paginate

from src.app.auth.permissions import get_current_user
from src.app.base.schemas import Msg
from .filters import RecordFilter
from .models import Record
from .schemas import RecordOut, RecordIn
from .services import records_s
from src.app.users.models import User

router = APIRouter()


@router.get('/', response_model=Page[RecordOut], dependencies=[Depends(pagination_params)])
async def get_records(user: User = Depends(get_current_user),
                      filter_params: RecordFilter = Depends()):
    queryset = await records_s.filter_queryset(filter_params, creator_id=user.id)
    return await paginate(queryset)


@router.get('/{id}',
            response_model=RecordOut,
            responses={404: {"model": HTTPNotFoundError}})
async def get_record(id: int, user: User = Depends(get_current_user)):
    return await records_s.get(id=id, creator_id=user.id)


@router.post('/',
             response_model=RecordOut,
             status_code=201)
async def create_record(record: RecordIn,
                        user: User = Depends(get_current_user)):
    return await records_s.create(record, creator_id=user.id)


@router.put('/{pk}',
            responses={404: {"Description": "not found"}})
async def update_record(pk: int, record: RecordIn,
                        user: User = Depends(get_current_user)):
    return await records_s.update(record, id=pk, creator_id=user.id)


@router.delete('/{pk}',
               response_model=Msg,
               responses={404: {'Description': 'not found'}})
async def delete_record(pk: int,
                        user: User = Depends(get_current_user)):
    if await records_s.delete(id=pk, creator_id=user.id):
        return {'msg': 'deleted'}
    else:
        raise HTTPException(status_code=404, detail='object not found')
