from django.urls import path
from .views import ProjectViewSet, TaskViewSet
from rest_framework.routers import DefaultRouter

urlpatterns = [
   
]

router = DefaultRouter()
router.register('projects', ProjectViewSet )
router.register('tasks', TaskViewSet, basename='task')
urlpatterns += router.urls