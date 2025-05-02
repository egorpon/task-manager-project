from django.db import models
from datetime import datetime
from django.utils import timezone
from zoneinfo import ZoneInfo
# Create your models here.

class Project(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField(null=False,default=(datetime.now(tz=ZoneInfo("EET"))+timezone.timedelta(days=365*5)))

    def __str__(self):
        return self.name