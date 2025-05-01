from django.db import models
# Create your models here.

class Project(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField(null=True)

    def __str__(self):
        return self.name