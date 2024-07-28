from tortoise import fields, models
from .writing_session import WritingSession


class WritingSessionPart(models.Model):
    writing_session_part_id = fields.CharField(pk=True, max_length=128)
    writing_session_part_name = fields.CharField(max_length=128)
    writing_session_part_output = fields.TextField(null=True)
    writing_session_part_rate = fields.BooleanField()
    writing_session_part_feedback = fields.TextField(null=True)
    writing_session_part_update_time = fields.DatetimeField(null=True)
    writing_session = fields.ForeignKeyField('models.WritingSession', related_name='parts')

    class Meta:
        table = "writing_session_part"
