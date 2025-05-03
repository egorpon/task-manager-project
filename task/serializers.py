from rest_framework import serializers
from project.models import Project
from datetime import datetime
from zoneinfo import ZoneInfo
from project.models import Project
from task.models import Task, AssignedUser
from django.contrib.auth.models import User


class AssignedUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user")

    class Meta:
        model = AssignedUser
        fields = ("user_id", "username")
        extra_kwargs = {"username": {"read_only": True}}


class TaskProjectDetail(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ("name", "due_date")


class TaskSerializer(serializers.ModelSerializer):
    task_id = serializers.IntegerField(source="id", read_only=True)
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), source="project"
    )
    project_detail = TaskProjectDetail(read_only=True, source="project")

    users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)

    class Meta:
        model = Task
        fields = (
            "task_id",
            "name",
            "description",
            "priority",
            "status",
            "due_date",
            "project_id",
            "project_detail",
            "users",
        )

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

    def validate_due_date(self, value):
        if value is None:
            return value
        elif value < datetime.now(tz=ZoneInfo("EET")):
            raise serializers.ValidationError(
                "Date cannot be earlier than current time"
            )
        return value

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        users = instance.users.all()
        representation["users"] = AssignedUserSerializer(users, many=True).data
        return representation


class TaskDetailSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)

    class Meta:
        model = Task
        fields = (
            "id",
            "name",
            "description",
            "priority",
            "status",
            "due_date",
            "users",
        )

    def update(self, instance, validated_data):
        new_users = validated_data.pop("users")
        instance = super().update(instance, validated_data)

        old_users = instance.user.all()
        old_users_set = set(old_users) 
        new_users_set = set(new_users) 

        for user in old_users_set - new_users_set:
            AssignedUser.objects.filter(task=instance, user=user).delete()
        
        for user in new_users_set - old_users_set:
            AssignedUser.objects.create(task=instance, user=user)

        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        users = instance.users.all()
        representation["users"] = AssignedUserSerializer(users, many=True).data
        return representation


# class TaskSerializer(serializers.ModelSerializer):
#     project_name = serializers.CharField(source="project.name", read_only=True)
#     project_id = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
#     project = serializers.HyperlinkedRelatedField(
#         read_only=True, view_name="project-detail"
#     )

#     users = AssignedUserSerializer(many=True)

#     class Meta:
#         model = Task
#         fields = (
#             "project_id",
#             "project",
#             "project_name",
#             "id",
#             "name",
#             "priority",
#             "status",
#             "due_date",
#             "users",
#         )


# class TaskCreateUpdateSerializer(serializers.ModelSerializer):
#     project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
#     users = AssignedUserSerializer(many=True)
#     class Meta:
#         model = Task
#         fields = (
#             "project",
#             "name",
#             "priority",
#             "status",
#             "due_date",
#             "users",
#         )

#     def update(self, instance, validated_data):
#         user_data = validated_data.pop("users")

#         instance = super().update(instance, validated_data)

#         if user_data is not None:
#             instance.users.all().delete()

#             for user in user_data:
#                 AssignedUser.objects.create(task=instance, user_id=user['user_id'].id)

#             return instance

#     def create(self, validated_data):
#         users_data = validated_data.pop("users")
#         task = Task.objects.create(**validated_data)

#         for user in users_data:
#             AssignedUser.objects.create(task=task, user_id=user['user_id'].id)
#         return task

#     def validate_due_date(self, value):


#         if value < datetime.now(tz=ZoneInfo("EET")):
#             raise serializers.ValidationError(
#                 "Date cannot be earlier than current time"
#             )
#         return value
