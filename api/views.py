from django.shortcuts import render
from rest_framework import generics
from project.models import Project
from task.models import Task
from project.serializers import ProjectSerializer, ProjectDetailSerializer
from task.serializers import TaskSerializer, TaskCreateUpdateSerializer
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from api.filters import ProjectFilter


# Create your views here.
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by('pk')
    permission_classes = [IsAdminUser]
    filterset_class = ProjectFilter
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter,
                       ]
    search_fields = ['name']
    ordering_fields = ['name','due_date']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProjectDetailSerializer
        return ProjectSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().order_by('pk')
    serializer_class = TaskSerializer
    def get_serializer_class(self):
        if self.action == "create" or self.action == "update":
            return TaskCreateUpdateSerializer
        return super().get_serializer_class()

