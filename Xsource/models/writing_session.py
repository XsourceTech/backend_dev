from tortoise import fields, models
from .user_info import UserInfo


class WritingSession(models.Model):
    writing_session_id = fields.CharField(pk=True, max_length=128)
    writing_session_major = fields.TextField()
    writing_session_topic = fields.TextField()
    writing_session_field = fields.TextField()
    writing_session_update_time = fields.DatetimeField(null=True)
    user_info = fields.ForeignKeyField('models.UserInfo', related_name='writing_sessions')

    class Meta:
        table = "writing_session"
