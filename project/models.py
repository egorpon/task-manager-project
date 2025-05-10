from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Project(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=1, related_name="projects")
    due_date = models.DateTimeField(null=True)

    def __str__(self):
        return self.name