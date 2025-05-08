from rest_framework import serializers
from project.models import Project
from datetime import datetime
from zoneinfo import ZoneInfo
from task.models import Task, AssignedUser
from django.contrib.auth.models import User


class AssignedUserSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id")
    username = serializers.CharField(source="user.username")

    class Meta:
        model = AssignedUser
        fields = ("user_id", "username")


class ProjectSerializerForTask(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ("id", "name", "due_date")


class TaskDetailSerializer(serializers.ModelSerializer):
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), source="project"
    )
    assigned_users = AssignedUserSerializer(many=True, read_only=True)
    total_comments = serializers.SerializerMethodField()

    def get_total_comments(self, obj):
        return obj.comments.count()

    class Meta:
        model = Task
        fields = (
            "id",
            "name",
            "description",
            "priority",
            "status",
            "due_date",
            "assigned_users",
            "project_id",
            "total_comments",
        )


class TaskReadSerializer(serializers.ModelSerializer):
    task_id = serializers.IntegerField(source="id", read_only=True)

    project_detail = ProjectSerializerForTask(read_only=True, source="project")

    assigned_users = AssignedUserSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = (
            "task_id",
            "name",
            "description",
            "priority",
            "status",
            "due_date",
            "project_detail",
            "assigned_users",
        )


class TaskWriteSerializer(serializers.ModelSerializer):
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), source="project"
    )
    users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)

    class Meta:
        model = Task
        fields = (
            "id",
            "name",
            "description",
            "priority",
            "due_date",
            "status",
            "project_id",
            "users",
        )
        extra_kwargs = {"id": {"read_only": True}}

    def create(self, validated_data):
        users_data = validated_data.pop("users")
        task = Task.objects.create(**validated_data)

        for user in users_data:
            AssignedUser.objects.create(task=task, user_id=user.id)
        return task

    def validate(self, attrs):
        project = attrs.get("project")
        due_date = attrs.get("due_date")
        if project and due_date and project.due_date is None:
            return attrs
        elif project and due_date and due_date > project.due_date:
            raise serializers.ValidationError(
                "Date cannot be later than project's due date"
            )
        return attrs

    def validate_users(self, value):
        for user in value:
            if not User.objects.filter(id=user.id).exists():
                raise serializers.ValidationError(
                    f"User with id {user.id} doesn't exist"
                )
        return value

    def validate_due_date(self, value):
        if value is None:
            return value
        elif value < datetime.now(tz=ZoneInfo("EET")):
            raise serializers.ValidationError(
                "Date cannot be earlier than current time"
            )
        return value


class TaskUpdateSerializer(serializers.ModelSerializer):
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), source="project", required=False
    )
    users = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="user", many=True, required=False
    )

    class Meta:
        model = Task
        fields = (
            "id",
            "name",
            "description",
            "priority",
            "due_date",
            "status",
            "project_id",
            "users",
        )
        extra_kwargs = {
            "id": {"read_only": True},
            
        }

    def update(self, instance, validated_data):

        new_users = validated_data.pop("users",None)
        instance = super().update(instance, validated_data)

        if new_users is not None:
            old_users = instance.user.all()
            old_users_set = set(old_users)
            new_users_set = set(new_users)

            for user in old_users_set - new_users_set:
                AssignedUser.objects.filter(task=instance, user=user).delete()

            for user in new_users_set - old_users_set:
                AssignedUser.objects.create(task=instance, user=user)
            
            instance.refresh_from_db()
        return instance

    def validate(self, attrs):
        project = attrs.get("project")
        due_date = attrs.get("due_date")
        if project and due_date and project.due_date is None:
            return attrs
        elif project and due_date and due_date > project.due_date:
            raise serializers.ValidationError(
                "Date cannot be later than project's due date"
            )
        return attrs

    def validate_due_date(self, value):
        if value is None:
            return value
        elif value < datetime.now(tz=ZoneInfo("EET")):
            raise serializers.ValidationError(
                "Date cannot be earlier than current time"
            )
        return value
