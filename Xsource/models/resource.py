from tortoise import fields, models
from .writing_session import WritingSession


class Resource(models.Model):
    resource_id = fields.CharField(pk=True, max_length=128)
    resource_title = fields.CharField(max_length=512)
    resource_authors_names = fields.TextField(null=True)
    resource_publish_time = fields.DateField(null=True)
    resource_journal_name = fields.CharField(max_length=512, null=True)
    resource_address = fields.TextField()
    writing_session = fields.ForeignKeyField('models.WritingSession', related_name='resources')

    class Meta:
        table = "resource"
