from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.clients.views import ClientViewSet

app_name = 'api_clients'

router = DefaultRouter()
router.register(r'', ClientViewSet)

urlpatterns = [
	path('', include(router.urls)),
]
