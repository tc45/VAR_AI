from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Client
from .serializers import ClientSerializer

# Create your views here.

class ClientViewSet(viewsets.ModelViewSet):
	"""
	API endpoint that allows clients to be viewed or edited.
	
	list:
		Return a list of all clients.
	
	create:
		Create a new client.
	
	retrieve:
		Return a client instance.
	
	update:
		Update a client instance.
	
	partial_update:
		Update a client instance partially.
	
	destroy:
		Delete a client instance.
	"""
	queryset = Client.objects.all().order_by('-created_at')
	serializer_class = ClientSerializer
	permission_classes = [permissions.IsAuthenticated]
	filterset_fields = ['name', 'active']
	search_fields = ['name', 'contact_name', 'contact_email']
	ordering_fields = ['name', 'created_at', 'updated_at']
