from typing import TypeVar, Type

from pydantic import BaseModel
from tortoise import Model


ModelType = TypeVar('ModelType', bound=Model)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)
GetSchemaType = TypeVar('GetSchemaType', bound=BaseModel)


class BaseService:
    model: Type[ModelType]
    create_schema: CreateSchemaType
    update_schema: UpdateSchemaType
    get_schema: GetSchemaType

    async def create(self, schema: CreateSchemaType, **kwargs) -> GetSchemaType:
        obj = await self.model.create(**schema.dict(), **kwargs)
        return await self.get_schema.from_tortoise_orm(obj)

    async def update(self, schema: UpdateSchemaType, **kwargs) -> GetSchemaType:
        await self.model.filter(**kwargs).update(**schema.dict(exclude_unset=True))
        return await self.get_schema.from_queryset(self.model.filter(**kwargs))

    async def delete(self, **kwargs):
        obj = await self.model.filter(**kwargs).delete()
        return obj

    async def get(self, **kwargs) -> GetSchemaType:
        return await self.get_schema.from_queryset_single(self.model.get(**kwargs))

    async def all(self) -> GetSchemaType:
        return await self.get_schema.from_queryset(self.model.all())

    async def filter(self, **kwargs) -> GetSchemaType:
        return await self.get_schema.from_queryset(self.model.filter(**kwargs))

    async def get_obj(self, **kwargs) -> ModelType:
        return await self.model.get_or_none(**kwargs)

    async def get_or_create(self, defaults: CreateSchemaType, **kwargs) -> GetSchemaType:
        return await self.model.get_or_create(**kwargs, defaults=defaults.dict())

    async def get_slice(self, page=0, size=50):
        queryset = self.model.all()
        items = queryset.offset(page * size).limit(size).all()
        return await self.get_schema.from_queryset(items)
