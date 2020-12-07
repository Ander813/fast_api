from fastapi import APIRouter
from tortoise.contrib.fastapi import HTTPNotFoundError

from ..models.records import RecordIn, RecordOut
from ..models.records import Record

router = APIRouter()


@router.get('/', response_model=list[RecordOut])
async def get_records():
    return await RecordOut.from_queryset(Record.all())


@router.get('/{id}',
            response_model=RecordOut,
            responses={404: {"model": HTTPNotFoundError}})
async def get_record(id: int):
    return await RecordOut.from_queryset_single(Record.get(id=id))


@router.post('/', response_model=RecordOut)
async def create_record(id: int, record: RecordIn):
    record_obj = await Record.create(**record.dict(exclude_unset=True))
    return await RecordOut.from_tortoise_orm(record_obj)