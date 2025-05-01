from rest_framework import serializers
from project.models import Project
from task.models import Task
from datetime import datetime
from zoneinfo import ZoneInfo
from task.serializers import TaskSerializer

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ("name", "description", "due_date", "tasks")

    tasks = TaskSerializer(many=True, read_only=True)

    def create(self, validated_data):
        tasks_data = validated_data.pop('tasks')
        project = Project.objects.create(**validated_data)

        for task in tasks_data:
            Task.objects.create(project=project, **task)
        return project

    def validate_due_date(self, value):
        if value < datetime.now(tz=ZoneInfo("EET")):
            raise serializers.ValidationError(
                "Date cannot be earlier than current time"
            )
        return value
    
