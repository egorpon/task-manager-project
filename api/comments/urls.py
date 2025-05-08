from django.urls import path
from api.comments import views

urlpatterns = [
    path("", views.CommentsListAPIView.as_view(), name="comments-list"),
    path(
        "create/", views.CommentsCreateAPIView.as_view(), name="comments-create"
    ),
    path(
        "<int:comment_id>/",
        views.CommentsDetailAPIView.as_view(),
        name="comments-detail",
    ),
    path(
        "<int:comment_id>/update",
        views.CommentsUpdateAPIView.as_view(),
        name="comments-update",
    ),
    path(
        "<int:comment_id>/delete",
        views.CommentsDeleteAPIView.as_view(),
        name="comments-delete",
    )
]
