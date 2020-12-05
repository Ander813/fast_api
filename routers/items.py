from fastapi import APIRouter

from schemas.schemas import Item

router = APIRouter()


@router.get('/')
async def get(item: Item):
    return item