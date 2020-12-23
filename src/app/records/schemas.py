from tortoise.contrib.pydantic import pydantic_model_creator, PydanticModel
from .models import Record


RecordOut = pydantic_model_creator(Record, name='record_out', exclude=('creator', 'creator_id'))
RecordIn = pydantic_model_creator(Record, name='record_in', exclude_readonly=True)
RecordOutAdmin = pydantic_model_creator(Record, name='record_out_admin', exclude=('creator',))