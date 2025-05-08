import django_filters
from comment.models import Comment
from task.models import Task


class TaskCommentsFilter(django_filters.FilterSet):

    class Meta:
        model = Comment
        fields = {
            "posted_by__username": ["iexact", "icontains"],
            "created_at": ["lt", "gt", "exact", "range"],
            "text" :["iexact", "icontains"],
        }

class TaskFilter(django_filters.FilterSet):

    class Meta:
        model = Task
        fields = {
            "id": ["exact", "range"],
            "name":["iexact", "icontains"],
            "description":["iexact", "icontains"],
            "due_date": ["lt", "gt", "exact", "range"],
            "priority" :["iexact", "icontains"],
            "status" :["iexact", "icontains"],
            "user__username" :["iexact", "icontains"],
            "project__name": ["iexact", "icontains"],
        }

