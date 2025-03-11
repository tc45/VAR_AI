from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Project
from .serializers import ProjectSerializer

# Create your views here.

class ProjectViewSet(viewsets.ModelViewSet):
	"""
	API endpoint that allows projects to be viewed or edited.
	
	list:
		Return a list of all projects.
	
	create:
		Create a new project.
	
	retrieve:
		Return a project instance.
	
	update:
		Update a project instance.
	
	partial_update:
		Update a project instance partially.
	
	destroy:
		Delete a project instance.
	"""
	queryset = Project.objects.all().order_by('-created_at')
	serializer_class = ProjectSerializer
	permission_classes = [permissions.IsAuthenticated]
	filterset_fields = ['name', 'client', 'status']
	search_fields = ['name', 'description', 'client__name']
	ordering_fields = ['name', 'client__name', 'status', 'start_date', 'end_date', 'created_at']
