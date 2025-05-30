from rest_framework import serializers
from project.models import Project
from task.models import Task
from django.utils import timezone
from api.tasks.serializers import TaskReadSerializer


class ProjectReadSerializer(serializers.ModelSerializer):
    total_tasks = serializers.SerializerMethodField()

    def get_total_tasks(self, obj) -> int:
        tasks = obj.tasks.all()
        return tasks.count()

    class Meta:
        model = Project
        fields = ("id", "name", "description", "owner", "due_date", "total_tasks")
        extra_kwargs = {"id": {"read_only": True}}


class ProjectWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
            "name",
            "description",
            "owner",
            "due_date",
        )
        extra_kwargs = {"owner": {"read_only": "owner"}}

    def validate_due_date(self, value):
        if value is None:
            return value
        elif value < timezone.now():
            raise serializers.ValidationError(
                "Date cannot be earlier than current time"
            )
        return value


class TaskSerializerForProject(serializers.ModelSerializer):
    total_assigned_user = serializers.SerializerMethodField()

    def get_total_assigned_user(self, obj) -> int:
        return obj.assigned_users.count()

    class Meta:
        model = Task
        fields = (
            "id",
            "name",
            "description",
            "priority",
            "status",
            "due_date",
            "total_assigned_user",
        )


class ProjectDetailSerializer(serializers.ModelSerializer):
    tasks = TaskSerializerForProject(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ("name", "description", "due_date", "tasks")
