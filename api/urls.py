from django.urls import path
import project.views as views
from rest_framework.routers import DefaultRouter

urlpatterns = [
    path("projects/", views.ProjectListCreateAPIView.as_view()),
    path("projects/<int:project_id>/", views.ProjectRetrieveUpdateDeleteAPIView.as_view())
]

# router = DefaultRouter()
# router.register('projects', views.ProjectAPIView)
# urlpatterns += router.urls