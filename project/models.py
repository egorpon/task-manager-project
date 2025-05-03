from django.db import models
from datetime import datetime
from django.utils import timezone
from zoneinfo import ZoneInfo
# Create your models here.

class Project(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField(null=True)

    def __str__(self):
        return self.name