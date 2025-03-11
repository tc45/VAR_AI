from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'clients'

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'', views.ClientViewSet)

urlpatterns = [
	# API endpoints
	path('', include(router.urls)),
] 