from django.urls import path
from . import views

app_name = 'parsers'

urlpatterns = [
	path('', views.ParserIndexView.as_view(), name='index'),
	path('device-files/', views.DeviceFileListView.as_view(), name='devicefile-list'),
	path('device-files/<int:pk>/', views.DeviceFileDetailView.as_view(), name='devicefile-detail'),
	path('device-files/create/', views.DeviceFileCreateView.as_view(), name='devicefile-create'),
	path('device-files/<int:pk>/edit/', views.DeviceFileUpdateView.as_view(), name='devicefile-update'),
	path('device-files/<int:pk>/delete/', views.DeviceFileDeleteView.as_view(), name='devicefile-delete'),
] 