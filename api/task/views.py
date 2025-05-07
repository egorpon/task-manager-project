from rest_framework import generics
from api.task.models import Task
from api.task.serializers import (
    TaskReadSerializer,
    TaskDetailSerializer,
    TaskWriteSerializer,
    TaskUpdateSerializer,
)
from api.comment.serializers import CommentsReadSerializer
from api.comment.models import Comment
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from api.task.filters import TaskCommentsFilter, TaskFilter
from api.permissions import IsAdminOrReadOnly
from rest_framework.response import Response
from rest_framework import status




class TaskCommentsListAPIView(generics.ListAPIView):
    queryset = Comment.objects.all()
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
    queryset = Task.objects.all().order_by("pk")
    serializer_class = TaskReadSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = TaskFilter
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    search_fields = ["name"]
    ordering_fields = ["name", "due_date"]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        return qs.filter(user=self.request.user)


class TaskCreateAPIView(generics.CreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskWriteSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        return qs.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        read_serializer = TaskReadSerializer(task)
        custom_response = {"task": read_serializer.data}
        return Response(custom_response, status=status.HTTP_201_CREATED)


class TaskDetailAPIView(generics.RetrieveAPIView):
    queryset = Task.objects.all().prefetch_related("assigned_users").order_by("pk")
    permission_classes = [IsAuthenticated]
    serializer_class = TaskDetailSerializer
    lookup_url_kwarg = "task_id"

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        return qs.filter(user=self.request.user)


class TaskUpdateAPIView(generics.UpdateAPIView):
    queryset = Task.objects.all().prefetch_related("assigned_users").order_by("pk")
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = TaskUpdateSerializer
    lookup_url_kwarg = "task_id"

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        return qs.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance=instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        task.refresh_from_db()
        read_serializer = TaskDetailSerializer(task)
        custom_response = {
            "task": read_serializer.data,
        }
        return Response(custom_response, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance=instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        task.refresh_from_db()
        read_serializer = TaskDetailSerializer(task)
        custom_response = {
            "task": read_serializer.data,
        }
        return Response(custom_response, status=status.HTTP_200_OK)


class TaskDeleteAPIView(generics.DestroyAPIView):
    queryset = Task.objects.all().prefetch_related("assigned_users").order_by("pk")
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = TaskDetailSerializer
    lookup_url_kwarg = "task_id"

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        return qs.filter(user=self.request.user)
