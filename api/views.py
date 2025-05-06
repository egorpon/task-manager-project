from rest_framework import generics
from comment.models import Comment

from comment.serializers import (
    CommentsUpdateSerializer,
    CommentsReadSerializer,
    CommentsWriteSerializer,
)
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from api.filters import ProjectFilter
from .permissions import IsAdminOrReadOnly
from rest_framework.response import Response
from rest_framework import status

