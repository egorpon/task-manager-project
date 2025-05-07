import django_filters
from api.project.models import Project
from rest_framework import filters
from django.db.models import Count



class ProjectFilter(django_filters.FilterSet):
    total_tasks__gt = django_filters.NumberFilter(
        field_name="total_tasks", lookup_expr="gt", label='Total Tasks greater than'
    )
    total_tasks__lt = django_filters.NumberFilter(
        field_name="total_tasks", lookup_expr="lt", label='Total Tasks less than'
    )
    total_tasks = django_filters.NumberFilter(
        field_name="total_tasks", lookup_expr="exact", label='Total Tasks'
    )

    class Meta:
        model = Project
        fields = {
            "name": ["iexact", "icontains"],
            "due_date": ["lt", "gt", "exact", "range"],
        }

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset.annotate(total_tasks=Count("tasks")))
