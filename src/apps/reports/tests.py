from django.test import TestCase
from django.contrib.auth.models import User
from .models import ReportType, Report
from apps.projects.models import Project
from apps.clients.models import Client

class ReportTypeModelTest(TestCase):
	"""Test cases for the ReportType model"""
	
	def setUp(self):
		"""Set up test data"""
		self.report_type_data = {
			'name': 'Network Inventory',
			'slug': 'network-inventory',
			'description': 'A report of all network devices and interfaces',
		}
		self.report_type = ReportType.objects.create(**self.report_type_data)
	
	def test_report_type_creation(self):
		"""Test that a report type can be created with the expected attributes"""
		self.assertEqual(self.report_type.name, self.report_type_data['name'])
		self.assertEqual(self.report_type.slug, self.report_type_data['slug'])
		self.assertEqual(self.report_type.description, self.report_type_data['description'])
		
	def test_report_type_str(self):
		"""Test the string representation of a report type"""
		self.assertEqual(str(self.report_type), self.report_type_data['name'])

class ReportModelTest(TestCase):
	"""Test cases for the Report model"""
	
	def setUp(self):
		"""Set up test data"""
		self.user = User.objects.create_user(
			username='testuser',
			email='test@example.com',
			password='testpassword'
		)
		
		self.client_obj = Client.objects.create(
			name='Test Company',
			contact_name='John Doe',
			contact_email='john@example.com'
		)
		
		self.project = Project.objects.create(
			name='Test Project',
			client=self.client_obj,
			status='in_progress'
		)
		
		self.report_type = ReportType.objects.create(
			name='Network Inventory',
			slug='network-inventory',
			description='A report of all network devices and interfaces'
		)
		
		self.report_data = {
			'name': 'Test Report',
			'project': self.project,
			'report_type': self.report_type,
			'description': 'A test report',
			'parameters': {'include_interfaces': True, 'include_routes': False},
			'status': 'pending',
			'created_by': self.user,
		}
		self.report = Report.objects.create(**self.report_data)
	
	def test_report_creation(self):
		"""Test that a report can be created with the expected attributes"""
		self.assertEqual(self.report.name, self.report_data['name'])
		self.assertEqual(self.report.project, self.project)
		self.assertEqual(self.report.report_type, self.report_type)
		self.assertEqual(self.report.description, self.report_data['description'])
		self.assertEqual(self.report.parameters, self.report_data['parameters'])
		self.assertEqual(self.report.status, self.report_data['status'])
		self.assertEqual(self.report.created_by, self.user)
		
	def test_report_str(self):
		"""Test the string representation of a report"""
		expected = f"{self.report_data['name']} ({self.project.name})"
		self.assertEqual(str(self.report), expected)
