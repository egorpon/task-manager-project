from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import APIView
from django.contrib.auth.models import User
from task.models import Task, AttachedFiles
from api.tasks.serializers import (
    TaskReadSerializer,
    TaskDetailSerializer,
    TaskWriteSerializer,
    TaskUpdateSerializer,
    AttachedFilesSerializer,
)
from api.permissions import IsAdminOrProjectOwner
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from api.comments.serializers import CommentsReadSerializer
from comment.models import Comment
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from api.tasks.filters import TaskCommentsFilter, TaskFilter
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.exceptions import PermissionDenied, NotFound
from api.task import send_assigned_task_email
import sys

class TaskCommentsListAPIView(generics.ListAPIView):
    queryset = Comment.objects.select_related("posted_by", "task").all()
    serializer_class = CommentsReadSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = TaskCommentsFilter
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    ordering_fields = ["posted_by__username", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        task_id = self.kwargs.get("task_id")
        qs = super().get_queryset()
        return qs.filter(task=task_id)


class TaskListAPIView(generics.ListAPIView):
    queryset = (
        Task.objects.prefetch_related("assigned_users__user")
        .select_related("project")
        .all()
        .order_by("pk")
    )
    serializer_class = TaskReadSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = TaskFilter
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["name"]
    ordering_fields = ["name", "due_date"]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        return qs.filter(
            Q(user=self.request.user) | Q(project__owner=self.request.user)
        )


class TaskCreateAPIView(generics.CreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskWriteSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        users_id = task.assigned_users.values_list("user", flat=True)
        emails = []
        for user_id in users_id:
            user = User.objects.get(id=user_id)
            emails.append(user.email)
        print(emails)
        sys.stdout.flush()
        send_assigned_task_email.apply_async(kwargs={"task_id":task.id, "user_emails": emails })
        read_serializer = TaskDetailSerializer(task)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)


class TaskDetailAPIView(generics.RetrieveAPIView):
    queryset = (
        Task.objects.prefetch_related("assigned_users__user").all().order_by("pk")
    )
    permission_classes = [IsAuthenticated]
    serializer_class = TaskDetailSerializer
    lookup_url_kwarg = "task_id"

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        return qs.filter(
            Q(user=self.request.user) | Q(project__owner=self.request.user)
        ).distinct()


class TaskUpdateAPIView(generics.UpdateAPIView):
    queryset = Task.objects.all().order_by("pk")
    permission_classes = [IsAuthenticated]
    serializer_class = TaskUpdateSerializer
    parser_classes = [MultiPartParser, FormParser]
    lookup_url_kwarg = "task_id"

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        return qs.filter(project__owner=self.request.user).distinct()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance=instance, data=request.data, partial=False
        )
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        read_serializer = TaskDetailSerializer(task)
        return Response(read_serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance=instance, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        task.refresh_from_db()
        read_serializer = TaskDetailSerializer(task)

        return Response(read_serializer.data, status=status.HTTP_200_OK)


class TaskDeleteAPIView(generics.DestroyAPIView):
    queryset = Task.objects.all().order_by("pk")
    permission_classes = [IsAuthenticated]
    serializer_class = TaskDetailSerializer
    lookup_url_kwarg = "task_id"

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        return qs.filter(project__owner=self.request.user)


class TasksAttachmentsDeleteAPIView(generics.DestroyAPIView):
    queryset = AttachedFiles.objects.all()
    permission_classes = [IsAdminOrProjectOwner]
    serializer_class = AttachedFilesSerializer

    def delete(self, request, task_id, file_id):
        file = get_object_or_404(AttachedFiles, task=task_id, id=file_id)
        self.check_object_permissions(request, file)
        file.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TasksAttachmentsListAPIView(generics.ListAPIView):
    queryset = AttachedFiles.objects.all().order_by("pk")
    permission_classes = [IsAuthenticated]
    serializer_class = AttachedFilesSerializer

    def get_queryset(self):
        task_id = self.kwargs.get("task_id")
        qs = super().get_queryset()
        qs = qs.filter(task=task_id)
        if self.request.user.is_staff:
            return qs
        if qs.filter(
            Q(task__user=self.request.user) | Q(task__project__owner=self.request.user)
        ).exists():
            return qs
        raise PermissionDenied(
            {"error": "You do not have permission to access this files"},
        )
