from rest_framework import serializers
from project.models import Project
from datetime import datetime
from zoneinfo import ZoneInfo
from task.models import Task, AssignedUser

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ("name", "priority","status","due_date")


    def validate_due_date(self, value):
        if value < datetime.now(tz=ZoneInfo("EET")):
            raise serializers.ValidationError(
                "Date cannot be earlier than current time"
            )
        return value