from django.contrib import admin
from django.contrib.auth.models import User
from api.comment.models import Comment
from api.project.models import Project
from api.task.models import Task


# Register your models here.

admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Comment)


