from django.shortcuts import render
from rest_framework import generics
from project.models import Project
from task.models import Task
from project.serializers import ProjectListCreateSerializer, ProjectDetailSerializer
from task.serializers import TaskSerializer, TaskDetailSerializer
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from api.filters import ProjectFilter
from rest_framework.views import APIView
from rest_framework.response import Response


# Create your views here.
class ProjectListCreateAPIView(generics.ListCreateAPIView):
    queryset = Project.objects.all().order_by("pk")
    serializer_class = ProjectListCreateSerializer
    permission_classes = [IsAdminUser]
    filterset_class = ProjectFilter
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["name"]
    ordering_fields = ["name", "due_date"]


class ProjectDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectDetailSerializer
    lookup_url_kwarg = 'project_id'

class TaskListCreateAPIView(generics.ListCreateAPIView):
    queryset = Task.objects.all().order_by('pk')
    serializer_class = TaskSerializer

class TaskDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all().order_by('pk')
    serializer_class = TaskDetailSerializer
    lookup_url_kwarg = 'task_id'


# class TaskViewSet(viewsets.ModelViewSet):
#     queryset = Task.objects.all().order_by("pk")
#     serializer_class = TaskSerializer

#     def get_serializer_class(self):
#         if self.action == "create" or self.action == "update":
#             return TaskCreateUpdateSerializer
#         return super().get_serializer_class()
