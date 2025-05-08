from django.urls import path, include
from . import views

urlpatterns = [

   path("projects/", include('api.projects.urls')),
   path('tasks/', include('api.tasks.urls')),
   path('comments/', include('api.comments.urls')),
]
