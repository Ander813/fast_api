from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model
from tortoise import fields


class Record(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    text = fields.TextField(blank=True, null=True)
    is_important = fields.BooleanField(default=False)
    create_date = fields.DatetimeField(auto_now_add=True)
    edit_date = fields.DatetimeField(auto_now=True)


RecordOut = pydantic_model_creator(Record, name='record_in')
RecordIn = pydantic_model_creator(Record, name='record_out', exclude_readonly=True)
