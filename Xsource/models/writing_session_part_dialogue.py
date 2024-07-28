from tortoise import fields, models
from .writing_session_part import WritingSessionPart


class WritingSessionPartDialogue(models.Model):
    writing_session_part_dialogue_id = fields.CharField(pk=True, max_length=128)
    writing_session_part_dialogue_bot = fields.TextField(null=True)
    writing_session_part_dialogue_user_input = fields.TextField()
    writing_session_part_dialogue_update_time = fields.DatetimeField(null=True)
    writing_session_part = fields.ForeignKeyField('models.WritingSessionPart', related_name='dialogues')

    class Meta:
        table = "writing_session_part_dialogue"
