from django.contrib import admin
from django.contrib.auth.models import User
from comment.models import Comment
from project.models import Project
from task.models import Task


# Register your models here.
class ProjectTaskInline(admin.StackedInline):
    model = Task
    extra = 1
    

class ProjectAdmin(admin.ModelAdmin):
    inlines = [ProjectTaskInline]


admin.site.register(Project, ProjectAdmin)
admin.site.register(Task)
admin.site.register(Comment)
