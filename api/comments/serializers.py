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

    def __init__(self, instance=None, *args, **kwargs):
        super().__init__(instance, *args, **kwargs)
        user = self.context["request"].user

        if user.is_staff:
            self.fields["task_id"].queryset = Task.objects.all()
        else:
            self.fields["task_id"].queryset = Task.objects.filter(
                Q(assigned_users__user=user) | Q(project__owner=user)
            )


class CommentsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("text",)
