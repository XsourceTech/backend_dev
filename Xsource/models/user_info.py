from tortoise import fields, models


class UserInfo(models.Model):
    user_info_id = fields.CharField(pk=True, max_length=128)
    user_info_name = fields.CharField(max_length=128, null=True)
    user_info_gender = fields.CharField(max_length=50, null=True)
    user_info_email = fields.CharField(max_length=128)
    user_info_password = fields.TextField()
    user_info_activation = fields.BooleanField()
    user_info_status = fields.CharField(max_length=128, null=True)
    user_info_goal = fields.CharField(max_length=256, null=True)
    user_info_registration_source = fields.TextField(null=True)
    user_info_registration_date = fields.DatetimeField()

    class Meta:
        table = "user_info"
