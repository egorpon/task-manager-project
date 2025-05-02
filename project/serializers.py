from rest_framework import serializers
from project.models import Project
from task.models import Task
from datetime import datetime
from zoneinfo import ZoneInfo
from task.serializers import TaskSerializer


class ProjectSerializer(serializers.ModelSerializer):
    total_tasks = serializers.SerializerMethodField()
    
    def get_total_tasks(self, obj):
        tasks = obj.tasks.all()
        return tasks.count()
    
    class Meta:
        model = Project
        fields = ("id","name", "description", "due_date", "total_tasks")
        extra_kwargs = {"id": {"read_only": True}}

    def validate_due_date(self, value):
        old_due_date = self.instance.due_date
        if value is None:
            return old_due_date
        if value < datetime.now(tz=ZoneInfo("EET")):
            raise serializers.ValidationError(
                "Date cannot be earlier than current time"
            )
        return value


class ProjectDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ("name", "description", "due_date", "tasks")

    tasks = TaskSerializer(many=True, read_only=True)

    