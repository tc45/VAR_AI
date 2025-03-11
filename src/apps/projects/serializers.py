from rest_framework import serializers
from .models import Project
from apps.clients.serializers import ClientSerializer

class ProjectSerializer(serializers.ModelSerializer):
	"""Serializer for the Project model"""
	client_detail = ClientSerializer(source='client', read_only=True)
	
	class Meta:
		model = Project
		fields = [
			'id', 'name', 'client', 'client_detail', 'description', 
			'start_date', 'end_date', 'status', 'notes', 
			'created_at', 'updated_at'
		]
		read_only_fields = ['created_at', 'updated_at'] 