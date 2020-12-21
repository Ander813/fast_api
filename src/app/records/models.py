from tortoise.models import Model
from tortoise import fields, Tortoise


class Record(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    text = fields.TextField(blank=True, null=True)
    is_important = fields.BooleanField(default=False)
    create_date = fields.DatetimeField(auto_now_add=True)
    edit_date = fields.DatetimeField(auto_now=True)
    creator = fields.ForeignKeyField('models.User', related_name='records')

    class Meta:
        ordering = ['-edit_date']


Tortoise.init_models(['src.app.users.models', 'src.app.records.models'], 'models')
