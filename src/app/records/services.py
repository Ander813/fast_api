from src.app.base.services import BaseService
from . import schemas
from .models import Record


class RecordsService(BaseService):
    model = Record
    create_schema = schemas.RecordIn
    update_schema = schemas.RecordIn
    get_schema = schemas.RecordOut


records_s = RecordsService()


