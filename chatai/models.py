from django.db import models


# Create your models here.


class chat_logs(models.Model):
    session_key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    messages = models.JSONField(default=dict)
