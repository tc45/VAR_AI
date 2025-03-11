from django.test import TestCase
from .models import Device, Interface
from apps.projects.models import Project
from apps.clients.models import Client
from apps.parsers.models import DeviceType

class DeviceModelTest(TestCase):
	"""Test cases for the Device model"""
	
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
		
		self.device_data = {
			'name': 'Test Router',
			'project': self.project,
			'device_type': self.device_type,
			'hostname': 'test-router',
			'management_ip': '192.168.1.1',
			'serial_number': 'ABC123XYZ',
			'model': 'CISCO2901/K9',
			'os_version': '15.1(4)M4',
			'notes': 'Test device notes',
		}
		self.device = Device.objects.create(**self.device_data)
	
	def test_device_creation(self):
		"""Test that a device can be created with the expected attributes"""
		self.assertEqual(self.device.name, self.device_data['name'])
		self.assertEqual(self.device.project, self.project)
		self.assertEqual(self.device.device_type, self.device_type)
		self.assertEqual(self.device.hostname, self.device_data['hostname'])
		self.assertEqual(str(self.device.management_ip), self.device_data['management_ip'])
		self.assertEqual(self.device.serial_number, self.device_data['serial_number'])
		self.assertEqual(self.device.model, self.device_data['model'])
		self.assertEqual(self.device.os_version, self.device_data['os_version'])
		self.assertEqual(self.device.notes, self.device_data['notes'])
		
	def test_device_str(self):
		"""Test the string representation of a device"""
		self.assertEqual(str(self.device), self.device_data['name'])

class InterfaceModelTest(TestCase):
	"""Test cases for the Interface model"""
	
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
		
		self.device = Device.objects.create(
			name='Test Router',
			project=self.project,
			device_type=self.device_type,
			hostname='test-router',
			management_ip='192.168.1.1'
		)
		
		self.interface_data = {
			'device': self.device,
			'name': 'GigabitEthernet0/0',
			'description': 'LAN Interface',
			'ip_address': '192.168.1.1',
			'subnet_mask': '255.255.255.0',
			'mac_address': '00:11:22:33:44:55',
			'is_up': True,
			'is_enabled': True,
			'speed': 1000,
			'mtu': 1500,
		}
		self.interface = Interface.objects.create(**self.interface_data)
	
	def test_interface_creation(self):
		"""Test that an interface can be created with the expected attributes"""
		self.assertEqual(self.interface.device, self.device)
		self.assertEqual(self.interface.name, self.interface_data['name'])
		self.assertEqual(self.interface.description, self.interface_data['description'])
		self.assertEqual(str(self.interface.ip_address), self.interface_data['ip_address'])
		self.assertEqual(self.interface.subnet_mask, self.interface_data['subnet_mask'])
		self.assertEqual(self.interface.mac_address, self.interface_data['mac_address'])
		self.assertEqual(self.interface.is_up, self.interface_data['is_up'])
		self.assertEqual(self.interface.is_enabled, self.interface_data['is_enabled'])
		self.assertEqual(self.interface.speed, self.interface_data['speed'])
		self.assertEqual(self.interface.mtu, self.interface_data['mtu'])
		
	def test_interface_str(self):
		"""Test the string representation of an interface"""
		expected = f"{self.device.name}:{self.interface_data['name']}"
		self.assertEqual(str(self.interface), expected)
