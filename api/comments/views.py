from rest_framework import generics
from comment.models import Comment
from task.models import Task
from api.comments.serializers import (
    CommentsUpdateSerializer,
    CommentsReadSerializer,
    CommentsWriteSerializer,
)
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from api.comments.filters import CommentsFilter
from api.permissions import IsAdminOrReadOnly
from rest_framework.response import Response
from rest_framework import status


class CommentsListAPIView(generics.ListAPIView):
    queryset = Comment.objects.all().select_related("posted_by", "task").order_by("pk")
    permission_classes = [IsAuthenticated]
    serializer_class = CommentsReadSerializer
    filterset_class = CommentsFilter
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    ordering_fields = ["posted_by__username", "created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        return qs.filter(task__assigned_users__user=self.request.user)


class CommentsCreateAPIView(generics.CreateAPIView):
    queryset = Comment.objects.all().order_by("pk")
    permission_classes = [IsAuthenticated]
    serializer_class = CommentsWriteSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.validated_data["task"]
        if (
            not request.user.is_staff
            and not task.user.filter(id=request.user.id).exists()
        ):
            return Response(
                {"message": "You don't have permission to comment this task"},
                status=status.HTTP_403_FORBIDDEN,
            )
        comment = serializer.save(posted_by=self.request.user)
        read_serializer = CommentsReadSerializer(comment)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)


class CommentsDetailAPIView(generics.RetrieveAPIView):
    queryset = Comment.objects.all().order_by("pk")
    lookup_url_kwarg = "comment_id"
    permission_classes = [IsAuthenticated]
    serializer_class = CommentsReadSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        return qs.filter(task__assigned_users__user=self.request.user)


class CommentsUpdateAPIView(generics.UpdateAPIView):
    queryset = Comment.objects.all().order_by("pk")
    lookup_url_kwarg = "comment_id"
    permission_classes = [IsAuthenticated]
    serializer_class = CommentsUpdateSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        return qs.filter(posted_by=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance=instance, data=request.data, partial=False
        )
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        task.refresh_from_db()
        read_serializer = CommentsReadSerializer(task)
        custom_response = {
            "task": read_serializer.data,
        }
        return Response(custom_response, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance=instance, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        task.refresh_from_db()
        read_serializer = CommentsReadSerializer(task)
        custom_response = {
            "task": read_serializer.data,
        }
        return Response(custom_response, status=status.HTTP_200_OK)


class CommentsDeleteAPIView(generics.DestroyAPIView):
    queryset = Comment.objects.all().order_by("pk")
    lookup_url_kwarg = "comment_id"
    permission_classes = [IsAuthenticated]
    serializer_class = CommentsReadSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        return qs.filter(posted_by=self.request.user)
