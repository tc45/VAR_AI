from django.test import TestCase
from .models import Project
from apps.clients.models import Client

class ProjectModelTest(TestCase):
	"""Test cases for the Project model"""
	
	def setUp(self):
		"""Set up test data"""
		self.client = Client.objects.create(
			name='Test Company',
			contact_name='John Doe',
			contact_email='john@example.com'
		)
		
		self.project_data = {
			'name': 'Test Project',
			'client': self.client,
			'description': 'A test project',
			'status': 'in_progress',
			'notes': 'Test project notes',
		}
		self.project = Project.objects.create(**self.project_data)
	
	def test_project_creation(self):
		"""Test that a project can be created with the expected attributes"""
		self.assertEqual(self.project.name, self.project_data['name'])
		self.assertEqual(self.project.client, self.client)
		self.assertEqual(self.project.description, self.project_data['description'])
		self.assertEqual(self.project.status, self.project_data['status'])
		self.assertEqual(self.project.notes, self.project_data['notes'])
		
	def test_project_str(self):
		"""Test the string representation of a project"""
		expected = f"{self.project_data['name']} ({self.client.name})"
		self.assertEqual(str(self.project), expected)
