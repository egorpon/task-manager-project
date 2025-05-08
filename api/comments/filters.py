import django_filters
from comment.models import Comment
from task.models import Task


class CommentsFilter(django_filters.FilterSet):

    class Meta:
        model = Comment
        fields = {
            "task__id":["exact"],
            "task__name":["iexact", "icontains"],
            "posted_by__username": ["iexact", "icontains"],
            "created_at": ["lt", "gt", "exact", "range"],
            "text" :["iexact", "icontains"],
        }