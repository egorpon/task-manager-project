from django.utils import regex_helper
from rest_framework import generics
from api.project.models import Project
from api.project.serializers import (
    ProjectReadSerializer,
    ProjectWriteSerializer,
    ProjectDetailSerializer,
)
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from api.project.filters import ProjectFilter
from api.permissions import IsAdminOrReadOnly
from rest_framework.response import Response
from rest_framework import status
# Create your views here.


class ProjectListAPIView(generics.ListAPIView):
    queryset = Project.objects.all().order_by("pk")
    serializer_class = ProjectReadSerializer
    permission_classes = [IsAdminOrReadOnly]
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


class ProjectCreateAPIView(generics.CreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectWriteSerializer
    permission_classes = [IsAdminOrReadOnly]


class ProjectDetailAPIView(generics.RetrieveAPIView):
    queryset = Project.objects.prefetch_related("tasks").all()
    serializer_class = ProjectDetailSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_url_kwarg = "project_id"

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        return qs.filter(tasks__assigned_users__user=self.request.user)


class ProjectUpdateAPIView(generics.UpdateAPIView):
    queryset = Project.objects.prefetch_related("tasks").all()
    serializer_class = ProjectWriteSerializer
    permission_classes = [IsAdminOrReadOnly]

    lookup_url_kwarg = "project_id"

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        return qs.filter(tasks__assigned_users__user=self.request.user)


class ProjectDeleteAPIView(generics.DestroyAPIView):
    queryset = Project.objects.prefetch_related("tasks").all()
    serializer_class = ProjectDetailSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_url_kwarg = "project_id"

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        return qs.filter(tasks__assigned_users__user=self.request.user)
