from rest_framework import serializers
from .models import Comment, Task
from django.contrib.auth.models import User

class PostedBySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username"
        )

class CommentsReadSerializer(serializers.ModelSerializer):
    posted_by = PostedBySerializer(read_only=True)
    comments_id = serializers.IntegerField(read_only=True, source='id')
    class Meta:
        model = Comment
        fields = (
            "task_id",
            "comments_id",
            "created_at",
            "posted_by",
            "text",
        )

class CommentsWriteSerializer(serializers.ModelSerializer):
    task_id = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all(), source='task')
    class Meta:
        model = Comment
        fields = (
            "task_id",
            "text"
        )

class CommentsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            "text",
        )