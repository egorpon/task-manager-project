from django.shortcuts import render
from rest_framework import generics
from project.models import Project
from task.models import Task
from comment.models import Comment
from project.serializers import ProjectListCreateSerializer, ProjectDetailSerializer
from task.serializers import (
    TaskReadSerializer,
    TaskDetailSerializer,
    TaskWriteSerializer,
)
from comment.serializers import CommentsUpdateSerializer, CommentsReadSerializer, CommentsWriteSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from api.filters import ProjectFilter
from .mixins import AdminOrReadOnlyMixin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


# Create your views here.
class ProjectListCreateAPIView(AdminOrReadOnlyMixin, generics.ListCreateAPIView):
    queryset = Project.objects.all().order_by("pk")
    serializer_class = ProjectListCreateSerializer
    filterset_class = ProjectFilter
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
        return qs.filter(tasks__assigned_users__user=self.request.user)


class ProjectDetailRetrieveUpdateDestroyAPIView(
    AdminOrReadOnlyMixin, generics.RetrieveUpdateDestroyAPIView
):
    queryset = Project.objects.all()
    serializer_class = ProjectDetailSerializer
    lookup_url_kwarg = "project_id"

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        return qs.filter(tasks__assigned_users__user=self.request.user)


class TaskListCreateAPIView(AdminOrReadOnlyMixin, generics.ListCreateAPIView):
    queryset = Task.objects.all().order_by("pk")

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        return qs.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TaskWriteSerializer
        return TaskReadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        read_serializer = TaskReadSerializer(task)
        custom_response = {
            "message": "Task successfully created",
            "task": read_serializer.data,
        }
        return Response(custom_response, status=status.HTTP_201_CREATED)


class TaskDetailRetrieveUpdateDestroyAPIView(
    AdminOrReadOnlyMixin, generics.RetrieveUpdateDestroyAPIView
):
    queryset = Task.objects.all().order_by("pk")
    lookup_url_kwarg = "task_id"
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        return qs.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return TaskWriteSerializer
        return TaskDetailSerializer

    def udpate(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        read_serializer = TaskDetailSerializer(task)
        custom_response = {
            "message": "Task successfully updated",
            "task": read_serializer.data,
        }
        return Response(custom_response, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        read_serializer = TaskDetailSerializer(task)
        custom_response = {
            "message": "Task successfully updated",
            "task": read_serializer.data,
        }
        return Response(custom_response, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        custom_response = {
            "status": "Task successfully deleted",
        }
        return Response(custom_response, status=status.HTTP_204_NO_CONTENT)


class CommentsListCreateAPIView(generics.ListCreateAPIView):
    queryset = Comment.objects.all().order_by("pk")
    permission_classes=[IsAuthenticated]

    # def get_permissions(self):
    #     if self.request.method == 'POST':
    #         self.permission_classes=[IsAuthenticated]
    #     return super().get_permissions()
    
    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        return qs.filter(posted_by=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CommentsWriteSerializer
        return CommentsReadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save(posted_by=self.request.user)
        read_serializer = CommentsReadSerializer(comment)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)


class CommentsRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all().order_by("pk")
    lookup_url_kwarg = "comment_id"
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        return qs.filter(posted_by=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            if self.request.user.is_staff:
                return CommentsWriteSerializer
            comment = self.get_object()
            if comment.posted_by != self.request.user:
                PermissionError("You don't have permission to edit this comment")
                return CommentsUpdateSerializer
        return CommentsReadSerializer

    

class CommentListAPIView(generics.ListAPIView):
    queryset = Comment.objects.all().order_by("pk")
    serializer_class = CommentsReadSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        task_id = self.kwargs.get("task_id")
        qs = super().get_queryset()
        return qs.filter(task=task_id)
