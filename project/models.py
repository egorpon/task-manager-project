from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
# Create your models here.

class Project(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=1, related_name="projects")
    due_date = models.DateTimeField(null=True)

    def __str__(self):
        return self.name
    
    def clean(self):
        super().clean()
        if self.due_date < timezone.now():
            raise ValidationError("Date cannot be earlier than current time")