from django.urls import path, include
from . import views

urlpatterns = [

   path("projects/", include('project.urls')),
   path('tasks/', include('task.urls')),
   path('comments/', include('comment.urls')),
]
