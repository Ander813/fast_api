from datetime import datetime

from src.app.base.services import BaseService
from . import schemas
from .models import Record


class RecordsService(BaseService):
    model = Record
    create_schema = schemas.RecordIn
    update_schema = schemas.RecordIn
    get_schema = schemas.RecordOut

    async def update(self, schema, **kwargs):
        await self.model.filter(**kwargs).update(**schema.dict(exclude_unset=True),
                                                 edit_date=datetime.now())
        return await self.get_schema.from_queryset(self.model.filter(**kwargs))


records_s = RecordsService()


