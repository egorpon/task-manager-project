from django.urls import path, include
from . import views

urlpatterns = [

   path("projects/", include('api.project.urls')),
   path('tasks/', include('api.task.urls')),
   path('comments/', include('api.comment.urls')),
]
