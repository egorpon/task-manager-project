from rest_framework import serializers
from comment.models import Comment
from task.models import Task
from django.contrib.auth.models import User
from django.db.models import Q


class PostedBySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username")


class TaskSerializerForComment(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ("id", "name")


class CommentsReadSerializer(serializers.ModelSerializer):
    posted_by = PostedBySerializer(read_only=True)
    comments_id = serializers.IntegerField(read_only=True, source="id")
    task = TaskSerializerForComment(read_only=True)

    class Meta:
        model = Comment
        fields = (
            "task",
            "posted_by",
            "comments_id",
            "created_at",
            "text",
        )


class CommentsWriteSerializer(serializers.ModelSerializer):
    task_id = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(), source="task"
    )

    class Meta:
        model = Comment
        fields = ("task_id", "text")

    def validate_task_id(self, value):
        user = self.context["request"].user
        if not user.is_staff and (
            user not in value.user.all() and value.project.owner != user
        ):
            raise serializers.ValidationError("You cannot write comment on other task")
        return value


class CommentsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("text",)
