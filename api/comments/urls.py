from django.urls import path
from api.comments import views

urlpatterns = [
    path("", views.CommentsListAPIView.as_view(), name="comment-list"),
    path(
        "create/", views.CommentsCreateAPIView.as_view(), name="comment-create"
    ),
    path(
        "<int:comment_id>/",
        views.CommentsDetailAPIView.as_view(),
        name="comment-detail",
    ),
    path(
        "<int:comment_id>/update",
        views.CommentsUpdateAPIView.as_view(),
        name="comment-update",
    ),
    path(
        "<int:comment_id>/delete",
        views.CommentsDeleteAPIView.as_view(),
        name="comment-delete",
    )
]
