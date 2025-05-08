from django.urls import path, include
from api.tasks import views


urlpatterns = [
    path("", views.TaskListAPIView.as_view(), name="task-list"),
    path(
        "create/", views.TaskCreateAPIView.as_view(), name="task-create"
    ),
    path(
        "<int:task_id>/",
        views.TaskDetailAPIView.as_view(),
        name="task-detail",
    ),
    path(
        "<int:task_id>/comments",
        views.TaskCommentsListAPIView.as_view(),
        name="task-detail",
    ),
    path(
        "<int:task_id>/update",
        views.TaskUpdateAPIView.as_view(),
        name="task-update",
    ),
    path(
        "<int:task_id>/delete",
        views.TaskDeleteAPIView.as_view(),
        name="task-delete",
    )
]
