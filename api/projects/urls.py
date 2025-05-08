from django.urls import path
from api.projects import views

urlpatterns = [
    path("", views.ProjectListAPIView.as_view(), name="project-list"),
    path(
        "create/", views.ProjectCreateAPIView.as_view(), name="project-create"
    ),
    path(
        "<int:project_id>/",
        views.ProjectDetailAPIView.as_view(),
        name="project-detail",
    ),
    path(
        "<int:project_id>/update",
        views.ProjectUpdateAPIView.as_view(),
        name="project-update",
    ),
    path(
        "<int:project_id>/delete",
        views.ProjectDeleteAPIView.as_view(),
        name="project-delete",
    )
]
