from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import DeviceType, DeviceFile
from apps.projects.models import Project
from apps.clients.models import Client

class DeviceTypeModelTest(TestCase):
	"""Test cases for the DeviceType model"""
	
	def setUp(self):
		"""Set up test data"""
		self.device_type_data = {
			'name': 'Cisco Router',
			'slug': 'cisco-router',
			'description': 'Cisco IOS router device type',
		}
		self.device_type = DeviceType.objects.create(**self.device_type_data)
	
	def test_device_type_creation(self):
		"""Test that a device type can be created with the expected attributes"""
		self.assertEqual(self.device_type.name, self.device_type_data['name'])
		self.assertEqual(self.device_type.slug, self.device_type_data['slug'])
		self.assertEqual(self.device_type.description, self.device_type_data['description'])
		
	def test_device_type_str(self):
		"""Test the string representation of a device type"""
		self.assertEqual(str(self.device_type), self.device_type_data['name'])

class DeviceFileModelTest(TestCase):
	"""Test cases for the DeviceFile model"""
	
	def setUp(self):
		"""Set up test data"""
		self.client = Client.objects.create(
			name='Test Company',
			contact_name='John Doe',
			contact_email='john@example.com'
		)
		
		self.project = Project.objects.create(
			name='Test Project',
			client=self.client,
			status='in_progress'
		)
		
		self.device_type = DeviceType.objects.create(
			name='Cisco Router',
			slug='cisco-router'
		)
		
		self.config_content = b"hostname test-router\ninterface GigabitEthernet0/0\n ip address 192.168.1.1 255.255.255.0\n!"
		self.config_file = SimpleUploadedFile("router_config.txt", self.config_content)
		
		self.device_file_data = {
			'name': 'Test Router',
			'project': self.project,
			'device_type': self.device_type,
			'file': self.config_file,
		}
		self.device_file = DeviceFile.objects.create(**self.device_file_data)
	
	def test_device_file_creation(self):
		"""Test that a device file can be created with the expected attributes"""
		self.assertEqual(self.device_file.name, self.device_file_data['name'])
		self.assertEqual(self.device_file.project, self.project)
		self.assertEqual(self.device_file.device_type, self.device_type)
		self.assertFalse(self.device_file.parsed)
		self.assertEqual(self.device_file.parse_errors, '')
		
	def test_device_file_str(self):
		"""Test the string representation of a device file"""
		expected = f"{self.device_file_data['name']} ({self.device_type.name})"
		self.assertEqual(str(self.device_file), expected)
