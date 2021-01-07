from datetime import datetime

from src.app.base.services import BaseService
from . import schemas
from .models import Record


class BaseRecordService(BaseService):
    model = Record
    create_schema = schemas.RecordIn
    update_schema = schemas.RecordIn

    async def update(self, schema, **kwargs):
        await self.model.filter(**kwargs).update(
            **schema.dict(exclude_unset=True), edit_date=datetime.now()
        )
        return await self.get_schema.from_queryset_single(self.model.get(**kwargs))


class RecordsService(BaseRecordService):
    get_schema = schemas.RecordOut


class RecordsServiceAdmin(BaseRecordService):
    get_schema = schemas.RecordOutAdmin


records_s = RecordsService()
records_s_admin = RecordsServiceAdmin()
