from datetime import datetime
from typing import Optional

from fastapi import Query

from src.app.base.filters import BaseFilter


class RecordFilter(BaseFilter):
    def __init__(self,
                 is_important: Optional[str] = Query(None),
                 date_from: Optional[datetime] = Query(None),
                 date_to: Optional[datetime] = Query(datetime.now()),
                 order: Optional[str] = Query(None)):
        self.is_important = is_important
        self.edit_date__gte = date_from
        self.edit_date__lte = date_to
        self.order = order
