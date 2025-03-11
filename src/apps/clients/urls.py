from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
	path('', views.ClientIndexView.as_view(), name='index'),
	path('list/', views.ClientListView.as_view(), name='client-list'),
	path('<int:pk>/', views.ClientDetailView.as_view(), name='client-detail'),
	path('create/', views.ClientCreateView.as_view(), name='client-create'),
	path('<int:pk>/edit/', views.ClientUpdateView.as_view(), name='client-update'),
	path('<int:pk>/delete/', views.ClientDeleteView.as_view(), name='client-delete'),
] 