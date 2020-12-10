from typing import TypeVar, Type

from pydantic import BaseModel
from tortoise import Model
from fastapi import HTTPException

ModelType = TypeVar('ModelType', bound=Model)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)
GetSchemaType = TypeVar('GetSchemaType', bound=BaseModel)


class BaseService:
    model: Type[ModelType]
    create_schema: CreateSchemaType
    update_schema: UpdateSchemaType
    get_schema: GetSchemaType

    async def create(self, schema: CreateSchemaType) -> GetSchemaType:
        obj = await self.model.create(**schema.dict())
        return await self.get_schema.from_tortoise_orm(obj)

    async def update(self, schema: UpdateSchemaType, **kwargs) -> GetSchemaType:
        await self.model.filter(**kwargs).update(**schema.dict(exculde_unset=True))
        return await self.get_schema.from_queryset_single(self.model.filter(**kwargs))

    async def delete(self, **kwargs):
        obj = await self.model.filter(**kwargs).delete()
        if not obj:
            raise HTTPException(status_code=404, detail='object not found')

    async def get(self, **kwargs) -> GetSchemaType:
        return await self.get_schema.from_queryset_single(self.model.get(**kwargs))

    async def all(self) -> GetSchemaType:
        return await self.get_schema.from_queryset(self.model.all())

    async def filter(self, **kwargs) -> GetSchemaType:
        return await self.get_schema.from_queryset(self.model.filter(**kwargs))

    async def get_obj(self, **kwargs) -> ModelType:
        return await self.model.get_or_none(**kwargs)

    async def get_or_create(self, defaults: dict=None, **kwargs) -> GetSchemaType:
        return await self.model.get_or_create(**kwargs, defaults=defaults)
