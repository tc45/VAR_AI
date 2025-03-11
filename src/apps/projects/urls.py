from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
	path('', views.ProjectIndexView.as_view(), name='index'),
	path('list/', views.ProjectListView.as_view(), name='project-list'),
	path('<int:pk>/', views.ProjectDetailView.as_view(), name='project-detail'),
	path('create/', views.ProjectCreateView.as_view(), name='project-create'),
	path('<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='project-update'),
	path('<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project-delete'),
] 