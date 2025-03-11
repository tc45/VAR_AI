from rest_framework import serializers
from .models import Client

class ClientSerializer(serializers.ModelSerializer):
	"""Serializer for the Client model"""
	
	class Meta:
		model = Client
		fields = [
			'id', 'name', 'contact_name', 'contact_email', 'contact_phone',
			'address', 'notes', 'active', 'created_at', 'updated_at'
		]
		read_only_fields = ['created_at', 'updated_at'] 