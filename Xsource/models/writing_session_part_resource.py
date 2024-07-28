from tortoise import fields, models
from .writing_session_part import WritingSessionPart
from .resource import Resource


class WritingSessionPartResource(models.Model):
    writing_session_part = fields.ForeignKeyField('models.WritingSessionPart', related_name='resources')
    resource = fields.ForeignKeyField('models.Resource', related_name='parts')

    class Meta:
        table = "writing_session_part_resource"
        unique_together = ('writing_session_part', 'resource')
