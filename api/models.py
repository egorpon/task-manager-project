from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    pass

class Project(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField(null=True)

    def __str__(self):
        return self.name

class Task(models.Model):
    class PriorityChoices(models.TextChoices):
        HIGH = "High"
        MEDIUM = "Medium"
        LOW = "Low"

    class StatusChoices(models.TextChoices):
        PENDING = "Pending"
        IN_PROGRESS = "In_Progress"
        COMPLETED = "Completed"

    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=6, choices=PriorityChoices.choices)
    status = models.CharField(max_length=11, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    project = models.ForeignKey(Project, related_name= 'tasks', on_delete=models.CASCADE)
    due_date = models.DateTimeField(null=True)

    def __str__(self):
        return self.name
    

class Comment(models.Model):
    task = models.ForeignKey(Task, related_name='comments', on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'Comment posted by {self.posted_by.get_full_name} and created at {self.created_at}'
