from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
	path('', views.ReportIndexView.as_view(), name='index'),
	path('create/', views.ReportCreateView.as_view(), name='report-create'),
	path('<int:pk>/', views.ReportDetailView.as_view(), name='report-detail'),
] 