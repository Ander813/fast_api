from tortoise.contrib.pydantic import pydantic_model_creator
from src.app.records.models import Record


RecordOut = pydantic_model_creator(Record, name='record_in')
RecordIn = pydantic_model_creator(Record, name='record_out', exclude_readonly=True)
