from django.urls import path
from . import views

urlpatterns = [
   path('projects/', views.ProjectListCreateAPIView.as_view()),
   path('projects/<int:project_id>/', views.ProjectDetailAPIView.as_view()),
   path('tasks/', views.TaskListCreateAPIView.as_view()),
   path('tasks/<int:task_id>/', views.TaskDetailAPIView.as_view())
]
