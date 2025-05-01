from django.db import models
from project.models import Project
from django.contrib.auth.models import User


# Create your models here.
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
    status = models.CharField(
        max_length=11, choices=StatusChoices.choices, default=StatusChoices.PENDING
    )
    project = models.ForeignKey(Project, related_name="tasks", on_delete=models.CASCADE)
    due_date = models.DateTimeField(null=True)
    
    user = models.ManyToManyField(User, through="AssignedUser", related_name="assigned_tasks")

    def __str__(self):
        return self.name

class AssignedUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} assigned to task {self.task.name}'