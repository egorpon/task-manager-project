from rest_framework import serializers
from project.models import Project
from datetime import datetime
from zoneinfo import ZoneInfo
from task.models import Task, AssignedUser
from django.contrib.auth.models import User


class AssignedUserSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(queryset = User.objects.all())
    class Meta:
        model = AssignedUser
        fields = ("user_id", "assigned_at")


class TaskSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source="project.name", read_only=True)
    project_id = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    project = serializers.HyperlinkedRelatedField(
        read_only=True, view_name="project-detail"
    )

    users = AssignedUserSerializer(many=True)

    class Meta:
        model = Task
        fields = (
            "project_id",
            "project",
            "project_name",
            "id",
            "name",
            "priority",
            "status",
            "due_date",
            "users",
        )


class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    users = AssignedUserSerializer(many=True)
    class Meta:
        model = Task
        fields = (
            "project",
            "name",
            "priority",
            "status",
            "due_date",
            "users",
        )
    
    def update(self, instance, validated_data):
        user_data = validated_data.pop("users")

        instance = super().update(instance, validated_data)

        if user_data is not None:
            instance.users.all().delete()

            for user in user_data:
                AssignedUser.objects.create(task=instance, user_id=user['user_id'].id)

            return instance

    def create(self, validated_data):
        users_data = validated_data.pop("users")
        task = Task.objects.create(**validated_data)

        for user in users_data:
            AssignedUser.objects.create(task=task, user_id=user['user_id'].id)
        return task

    def validate_due_date(self, value):
        if value < datetime.now(tz=ZoneInfo("EET")):
            raise serializers.ValidationError(
                "Date cannot be earlier than current time"
            )
        return value
    