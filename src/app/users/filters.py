from typing import Optional

from fastapi import Query

from src.app.base.filters import BaseFilter


class UserAdminFilter(BaseFilter):
    def __init__(self,
                 email: Optional[str] = Query(None),
                 order: Optional[str] = Query(None)):
        self.email__contains = email
        self.order = order
