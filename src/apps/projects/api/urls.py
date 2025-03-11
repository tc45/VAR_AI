from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.projects.views import ProjectViewSet

app_name = 'api_projects'

router = DefaultRouter()
router.register(r'', ProjectViewSet)

urlpatterns = [
	path('', include(router.urls)),
]
