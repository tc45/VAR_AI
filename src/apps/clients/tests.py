from django.test import TestCase
from .models import Client

# Create your tests here.

class ClientModelTest(TestCase):
	"""Test cases for the Client model"""
	
	def setUp(self):
		"""Set up test data"""
		self.client_data = {
			'name': 'Test Company',
			'contact_name': 'John Doe',
			'contact_email': 'john@example.com',
			'contact_phone': '555-123-4567',
			'address': '123 Test St, Test City, TS 12345',
			'notes': 'Test notes',
		}
		self.client = Client.objects.create(**self.client_data)
	
	def test_client_creation(self):
		"""Test that a client can be created with the expected attributes"""
		self.assertEqual(self.client.name, self.client_data['name'])
		self.assertEqual(self.client.contact_name, self.client_data['contact_name'])
		self.assertEqual(self.client.contact_email, self.client_data['contact_email'])
		self.assertEqual(self.client.contact_phone, self.client_data['contact_phone'])
		self.assertEqual(self.client.address, self.client_data['address'])
		self.assertEqual(self.client.notes, self.client_data['notes'])
		self.assertTrue(self.client.active)
		
	def test_client_str(self):
		"""Test the string representation of a client"""
		self.assertEqual(str(self.client), self.client_data['name'])
