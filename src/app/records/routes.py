from fastapi import APIRouter
from tortoise.contrib.fastapi import HTTPNotFoundError

from src.app.records.schemas import RecordOut, RecordIn
from src.app.records.services import records_s

router = APIRouter()


@router.get('/', response_model=list[RecordOut])
async def get_records():
    return await records_s.all()


@router.get('/{id}',
            response_model=RecordOut,
            responses={404: {"model": HTTPNotFoundError}})
async def get_record(id: int):
    return await records_s.get(id=id)


@router.post('/', response_model=RecordOut, status_code=201)
async def create_record(record: RecordIn):
    return await records_s.create(record)


@router.put('/{pk}',
            responses={404: {"Description": "not found"}})
async def update_record(pk: int, record: RecordIn):
    return await records_s.update(record, id=pk)


@router.delete('/{pk}',
               responses={404: {'Description': 'not found'}})
async def delete_record(pk: int):
    return await records_s.delete(id=pk)
