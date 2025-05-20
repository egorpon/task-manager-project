from django.db import models
from django.contrib.auth.models import User
from task.models import Task

# Create your models here.
class Comment(models.Model):
    task = models.ForeignKey(Task, related_name='comments', on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        if self.posted_by.username == "admin":
            return f'Comment posted by {self.posted_by.username}  and created at {self.created_at}'
        return f'Comment posted by {self.posted_by.get_full_name()} and created at {self.created_at}'