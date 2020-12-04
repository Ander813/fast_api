from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    time: Optional[date] = datetime.now()
