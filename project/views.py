from django.shortcuts import render
from rest_framework import generics
from .models import Project
from .serializers import ProjectSerializer
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework import viewsets

# Create your views here.
class ProjectListCreateAPIView(generics.ListCreateAPIView):
    queryset = Project.objects.all().order_by('pk')
    serializer_class = ProjectSerializer
    permission_classes = [IsAdminUser]

class ProjectRetrieveUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAdminUser]
    lookup_url_kwarg = "project_id"
    


