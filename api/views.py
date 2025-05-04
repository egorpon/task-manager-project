from django.shortcuts import render
from rest_framework import generics
from project.models import Project
from task.models import Task
from project.serializers import ProjectListCreateSerializer, ProjectDetailSerializer
from task.serializers import TaskReadSerializer, TaskDetailSerializer, TaskWriteSerializer
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from api.filters import ProjectFilter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


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


class ProjectDetailRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectDetailSerializer
    lookup_url_kwarg = 'project_id'

class TaskListCreateAPIView(generics.ListCreateAPIView):
    queryset = Task.objects.all().order_by('pk')
    
    def get_serializer_class(self):
        if self.request.method == "POST":
            return TaskWriteSerializer
        return TaskReadSerializer
    
    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        read_serializer= TaskReadSerializer(task)
        custom_response = {
            "message": "Task successfully created",
            "task": read_serializer.data,
        }
        return Response(custom_response, status=status.HTTP_201_CREATED)

class TaskDetailRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all().order_by('pk')
    lookup_url_kwarg = 'task_id'


    def udpate(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        read_serializer= TaskDetailSerializer(task)
        custom_response = {
            "message": "Task successfully updated",
            "task": read_serializer.data,
        }
        return Response(custom_response, status=status.HTTP_200_OK)
    
    def partial_update(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        read_serializer= TaskDetailSerializer(task)
        custom_response = {
            "message": "Task successfully updated",
            "task": read_serializer.data,
        }
        return Response(custom_response, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        response =  super().delete(request, *args, **kwargs)
        custom_response = {
            "message": "Task successfully deleted",
        }
        return Response(custom_response, status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return TaskWriteSerializer
        return TaskDetailSerializer
    
    