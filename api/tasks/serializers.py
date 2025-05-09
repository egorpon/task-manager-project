from rest_framework import serializers
from project.models import Project
from django.utils import timezone
from task.models import Task, AssignedUser, AttachedFiles
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


class UploadAttachedFilesSerializer(serializers.ModelSerializer):
    uploaded_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = AttachedFiles
        fields = ("id","files", "uploaded_at")


class TaskDetailSerializer(serializers.ModelSerializer):
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), source="project"
    )
    assigned_users = AssignedUserSerializer(many=True, read_only=True)
    total_comments = serializers.SerializerMethodField()

    files = UploadAttachedFilesSerializer(many=True, read_only=True)
    

    def get_total_comments(self, obj) -> int:
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
            "files",
        )


class TaskReadSerializer(serializers.ModelSerializer):
    task_id = serializers.IntegerField(source="id", read_only=True)

    project_detail = ProjectSerializerForTask(read_only=True, source="project")

    assigned_users = AssignedUserSerializer(many=True, read_only=True)

    files = UploadAttachedFilesSerializer(many=True, read_only=True)

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
            "files",
        )


class TaskWriteSerializer(serializers.ModelSerializer):
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), source="project"
    )
    users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)

    uploaded_files = serializers.ListField(
        child=serializers.FileField(
            max_length=10000, allow_empty_file=False, use_url=False
        ),
        write_only=True,
        required=False,

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
            "uploaded_files",
        )
        extra_kwargs = {"id": {"read_only": True}}

    def create(self, validated_data):
        users_data = validated_data.pop("users")
        uploaded_files = validated_data.pop("uploaded_files", None)
        task = Task.objects.create(**validated_data)

        if uploaded_files is not None:
            for file in uploaded_files:
                AttachedFiles.objects.create(
                    task=task, files=file, uploaded_at=timezone.now()
                )

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
        elif value < timezone.now():
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

    uploaded_files = serializers.ListField(
        child=serializers.FileField(
            max_length=10000, allow_empty_file=False, use_url=False
        ),
        write_only=True,
        required=False,
    )
    deleted_files = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
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
            "uploaded_files",
            "deleted_files",
        )
        extra_kwargs = {
            "id": {"read_only": True},
        }

    def update(self, instance, validated_data):
        new_users = validated_data.pop("users", None)
        uploaded_files = validated_data.pop("uploaded_files",None)
        deleted_files = validated_data.pop("deleted_files",None)
        instance.uploaded_at = timezone.now()
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

        if uploaded_files is not None:
            for file in uploaded_files:
                AttachedFiles.objects.create(
                    task=instance, files=file, uploaded_at=timezone.now()
                )
            instance.refresh_from_db()

        if deleted_files is not None:
            for file_id in deleted_files:
                AttachedFiles.objects.filter(task=instance, pk=file_id).delete()

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
        elif value < timezone.now():
            raise serializers.ValidationError(
                "Date cannot be earlier than current time"
            )
        return value
