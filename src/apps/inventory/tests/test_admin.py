from django.test import TestCase, Client as DjangoClient, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.storage.fallback import FallbackStorage
from apps.projects.models import Project
from apps.clients.models import Client
from apps.parsers.models import DeviceType
from ..models import (
	Device, Interface, VRF, ACL, RouteTable, InventoryItem,
	InventoryItemType
)
from ..admin import (
	DeviceAdmin, InterfaceAdmin, VRFAdmin, ACLAdmin, 
	RouteTableAdmin, InventoryItemAdmin
)
import json

User = get_user_model()

class BaseAdminTest(TestCase):
	"""Base test class for admin functionality."""
	
	def setUp(self):
		"""Set up test data."""
		# Create superuser
		self.admin_user = User.objects.create_superuser(
			username='admin',
			email='admin@example.com',
			password='adminpass123'
		)
		
		# Create regular user with permissions
		self.staff_user = User.objects.create_user(
			username='staff',
			email='staff@example.com',
			password='staffpass123',
			is_staff=True
		)
		
		# Add necessary permissions to staff user
		content_types = ContentType.objects.filter(
			app_label='inventory',
			model__in=['device', 'interface', 'vrf', 'acl', 'routetable', 'inventoryitem']
		)
		permissions = Permission.objects.filter(content_type__in=content_types)
		self.staff_user.user_permissions.add(*permissions)
		
		# Create client and project
		self.client_obj = Client.objects.create(
			name='Test Company',
			primary_contact_name='John Doe',
			primary_contact_email='john@example.com',
			created_by=self.admin_user
		)
		
		self.project = Project.objects.create(
			name='Test Project',
			client=self.client_obj,
			status='active',
			created_by=self.admin_user
		)
		
		# Create a test device type
		self.device_type = DeviceType.objects.create(
			name='Cisco Router',
			slug='cisco-router'
		)
		
		# Create test device
		self.device = Device.objects.create(
			project=self.project,
			name='test-device',
			device_type=self.device_type,
			model='C2960X',
			management_ip='192.168.1.1',
			firmware_version='15.0(2)SE',
			serial_number='FOC1234X5YZ',
			interface_count=48,
			route_count=100,
			acl_count=10,
			sfp_count=4,
			ipsec_tunnel_count=0,
			routing_protocols={'ospf': True, 'bgp': False},
			notes='Test device',
			created_by=self.admin_user
		)
		
		# Initialize test client and request factory
		self.client = DjangoClient()
		self.client.force_login(self.admin_user)
		self.factory = RequestFactory()
	
	def get_csrf_token(self, url):
		"""Get CSRF token for a given URL."""
		response = self.client.get(url)
		csrf_token = response.cookies.get('csrftoken', None)
		return csrf_token.value if csrf_token else None

	def verify_admin_list_view(self, model_name):
		"""Test if the admin list view loads correctly."""
		url = reverse(f'admin:inventory_{model_name}_changelist')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		return response

	def verify_admin_add_view(self, model_name):
		"""Test if the admin add view loads correctly."""
		url = reverse(f'admin:inventory_{model_name}_add')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		return response

	def verify_admin_change_view(self, model_name, object_id):
		"""Test if the admin change view loads correctly."""
		url = reverse(f'admin:inventory_{model_name}_change', args=[object_id])
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		return response

class DeviceAdminTest(BaseAdminTest):
	"""Test cases for Device admin functionality."""
	
	def test_device_admin_views(self):
		"""Test if all device admin views load correctly."""
		# Test list view
		self.verify_admin_list_view('device')
		
		# Test add view
		self.verify_admin_add_view('device')
		
		# Test change view
		self.verify_admin_change_view('device', self.device.id)
	
	def test_add_device(self):
		"""Test adding a new device through admin using direct model manipulation."""
		# Create a device directly via the model API instead of using the admin form
		new_device = Device.objects.create(
			project=self.project,
			name='new-device',
			device_type=self.device_type,
			model='C3750X',
			management_ip='192.168.1.2',
			firmware_version='15.0(2)SE10',
			serial_number='FOC5678A9BC',
			interface_count=24,
			route_count=50,
			acl_count=5,
			sfp_count=2,
			ipsec_tunnel_count=0,
			routing_protocols={'ospf': False, 'bgp': True},
			notes='New test device',
			created_by=self.admin_user
		)
		
		# Verify the device was created
		device = Device.objects.get(name='new-device')
		self.assertEqual(device.model, 'C3750X')
		self.assertEqual(device.management_ip, '192.168.1.2')
		self.assertEqual(device.created_by, self.admin_user)
		
		# Test the admin interface can display this device
		url = reverse('admin:inventory_device_change', args=[new_device.id])
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		
		# Verify the admin interface contains correct device details
		self.assertContains(response, 'new-device')
		self.assertContains(response, 'C3750X')
	
	def test_change_device(self):
		"""Test editing an existing device through direct model manipulation."""
		# Update the device directly via the model API
		self.device.model = 'C3850X'
		self.device.firmware_version = '16.0.1'
		self.device.notes = 'Updated device notes'
		self.device.save()
		
		# Verify the changes were applied
		updated_device = Device.objects.get(id=self.device.id)
		self.assertEqual(updated_device.model, 'C3850X')
		self.assertEqual(updated_device.firmware_version, '16.0.1')
		self.assertEqual(updated_device.notes, 'Updated device notes')
		
		# Test the admin interface reflects these changes
		url = reverse('admin:inventory_device_change', args=[self.device.id])
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'C3850X')
		self.assertContains(response, '16.0.1')
	
	def test_device_admin_save_model(self):
		"""Test the save_model method of DeviceAdmin directly."""
		# Create a request
		request = self.factory.get('/')
		request.user = self.admin_user
		
		# Create form data for a new device (not saved)
		device = Device(
			project=self.project,
			name='admin-saved-device',
			device_type=self.device_type,
			model='C3560X'
		)
		
		# Set up messages for the request (needed for admin save_model)
		setattr(request, 'session', 'session')
		messages = FallbackStorage(request)
		setattr(request, '_messages', messages)
		
		# Create admin instance and save model
		admin_instance = DeviceAdmin(Device, None)
		admin_instance.save_model(request, device, None, False)
		
		# Verify created_by was set
		self.assertEqual(device.created_by, self.admin_user)
		
		# Verify the device was saved to the database
		saved_device = Device.objects.get(name='admin-saved-device')
		self.assertEqual(saved_device.model, 'C3560X')

class InterfaceAdminTest(BaseAdminTest):
	"""Test cases for Interface admin functionality."""
	
	def test_interface_admin_views(self):
		"""Test if all interface admin views load correctly."""
		# Create a test interface
		interface = Interface.objects.create(
			device=self.device,
			name='GigabitEthernet0/0',
			description='Test Interface',
			ip_address='192.168.10.1',
			subnet_mask='255.255.255.0',
			created_by=self.admin_user
		)
		
		# Test list view
		self.verify_admin_list_view('interface')
		
		# Test add view
		self.verify_admin_add_view('interface')
		
		# Test change view
		self.verify_admin_change_view('interface', interface.id)
	
	def test_add_interface(self):
		"""Test adding a new interface through direct model creation."""
		# Create an interface directly
		interface = Interface.objects.create(
			device=self.device,
			name='GigabitEthernet0/1',
			description='Test Interface',
			ip_address='192.168.10.1',
			subnet_mask='255.255.255.0',
			mac_address='00:11:22:33:44:55',
			is_up=True,
			is_enabled=True,
			speed=1000,
			mtu=1500,
			created_by=self.admin_user
		)
		
		# Verify the interface was created
		self.assertEqual(interface.ip_address, '192.168.10.1')
		self.assertEqual(interface.created_by, self.admin_user)
		
		# Test the admin interface can display this interface
		url = reverse('admin:inventory_interface_change', args=[interface.id])
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'GigabitEthernet0/1')

class VRFAdminTest(BaseAdminTest):
	"""Test cases for VRF admin functionality."""
	
	def test_vrf_admin_views(self):
		"""Test if all VRF admin views load correctly."""
		# Create a test VRF
		vrf = VRF.objects.create(
			device=self.device,
			name='CUSTOMER1',
			route_distinguisher='65000:1',
			created_by=self.admin_user
		)
		
		# Test list view
		self.verify_admin_list_view('vrf')
		
		# Test add view
		self.verify_admin_add_view('vrf')
		
		# Test change view
		self.verify_admin_change_view('vrf', vrf.id)
	
	def test_add_vrf(self):
		"""Test adding a new VRF through direct model creation."""
		# Create a VRF directly
		vrf = VRF.objects.create(
			device=self.device,
			name='CUSTOMER2',
			description='Customer 2 VRF',
			route_distinguisher='65000:2',
			created_by=self.admin_user
		)
		
		# Verify the VRF was created
		self.assertEqual(vrf.route_distinguisher, '65000:2')
		self.assertEqual(vrf.created_by, self.admin_user)
		
		# Test the admin interface can display this VRF
		url = reverse('admin:inventory_vrf_change', args=[vrf.id])
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'CUSTOMER2')

class ACLAdminTest(BaseAdminTest):
	"""Test cases for ACL admin functionality."""
	
	def test_acl_admin_views(self):
		"""Test if all ACL admin views load correctly."""
		# Create a test ACL
		acl = ACL.objects.create(
			device=self.device,
			name='TEST_ACL',
			type='extended',
			rules=[{'action': 'permit', 'protocol': 'ip', 'source': 'any', 'destination': 'any'}],
			created_by=self.admin_user
		)
		
		# Test list view
		self.verify_admin_list_view('acl')
		
		# Test add view
		self.verify_admin_add_view('acl')
		
		# Test change view
		self.verify_admin_change_view('acl', acl.id)
	
	def test_add_acl(self):
		"""Test adding a new ACL through direct model creation."""
		# Create an ACL directly
		acl = ACL.objects.create(
			device=self.device,
			name='INBOUND_ACL',
			type='extended',
			rules=[{'action': 'permit', 'protocol': 'ip', 'source': 'any', 'destination': 'any'}],
			created_by=self.admin_user
		)
		
		# Verify the ACL was created
		self.assertEqual(acl.type, 'extended')
		self.assertEqual(acl.created_by, self.admin_user)
		
		# Test the admin interface can display this ACL
		url = reverse('admin:inventory_acl_change', args=[acl.id])
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'INBOUND_ACL')

class RouteTableAdminTest(BaseAdminTest):
	"""Test cases for RouteTable admin functionality."""
	
	def setUp(self):
		"""Set up test data specific to RouteTable tests."""
		super().setUp()
		
		# Create a VRF for the route table
		self.vrf = VRF.objects.create(
			device=self.device,
			name='CUSTOMER1',
			route_distinguisher='65000:1',
			created_by=self.admin_user
		)
	
	def test_route_table_admin_views(self):
		"""Test if all RouteTable admin views load correctly."""
		# Create a test RouteTable
		route_table = RouteTable.objects.create(
			device=self.device,
			vrf=self.vrf,
			routes=[{'prefix': '192.168.0.0/24', 'next_hop': '10.0.0.1'}],
			created_by=self.admin_user
		)
		
		# Test list view
		self.verify_admin_list_view('routetable')
		
		# Test add view
		self.verify_admin_add_view('routetable')
		
		# Test change view
		self.verify_admin_change_view('routetable', route_table.id)
	
	def test_add_route_table(self):
		"""Test adding a new route table through direct model creation."""
		# Create a RouteTable directly
		route_table = RouteTable.objects.create(
			device=self.device,
			vrf=self.vrf,
			routes=[
				{'prefix': '192.168.0.0/24', 'next_hop': '10.0.0.1'},
				{'prefix': '10.0.0.0/8', 'next_hop': '172.16.0.1'}
			],
			created_by=self.admin_user
		)
		
		# Verify the RouteTable was created
		self.assertEqual(len(route_table.get_routes()), 2)
		self.assertEqual(route_table.created_by, self.admin_user)
		
		# Test the admin interface can display this RouteTable
		url = reverse('admin:inventory_routetable_change', args=[route_table.id])
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)

class InventoryItemAdminTest(BaseAdminTest):
	"""Test cases for InventoryItem admin functionality."""
	
	def test_inventory_item_admin_views(self):
		"""Test if all InventoryItem admin views load correctly."""
		# Create a test InventoryItem
		inventory_item = InventoryItem.objects.create(
			device=self.device,
			name='Power Supply 1',
			item_type=InventoryItemType.SFP,
			description='Primary power supply unit',
			data={'serial': 'PS123456', 'wattage': '750W'},
			is_active=True,
			created_by=self.admin_user
		)
		
		# Test list view
		self.verify_admin_list_view('inventoryitem')
		
		# Test add view
		self.verify_admin_add_view('inventoryitem')
		
		# Test change view
		self.verify_admin_change_view('inventoryitem', inventory_item.id)
	
	def test_add_inventory_item(self):
		"""Test adding a new inventory item through direct model creation."""
		# Create an InventoryItem directly
		inventory_item = InventoryItem.objects.create(
			device=self.device,
			name='Power Supply 2',
			item_type=InventoryItemType.SFP,
			description='Secondary power supply unit',
			data={'serial': 'PS789012', 'wattage': '750W'},
			is_active=True,
			created_by=self.admin_user
		)
		
		# Verify the InventoryItem was created
		self.assertEqual(inventory_item.item_type, InventoryItemType.SFP)
		self.assertEqual(inventory_item.created_by, self.admin_user)
		
		# Test the admin interface can display this InventoryItem
		url = reverse('admin:inventory_inventoryitem_change', args=[inventory_item.id])
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Power Supply 2')

class AdminFormTest(BaseAdminTest):
	"""Tests using direct admin form classes instead of HTTP requests."""
	
	def test_device_admin_save_model(self):
		"""Test the save_model method of DeviceAdmin."""
		# Create a request with user
		request = self.factory.get('/')
		request.user = self.admin_user
		
		# Create a new device instance (not saved)
		device = Device(
			project=self.project,
			name='form-test-device',
			device_type=self.device_type,
			model='C3560X'
		)
		
		# Set up messages for the request (needed for admin save_model)
		setattr(request, 'session', 'session')
		messages = FallbackStorage(request)
		setattr(request, '_messages', messages)
		
		# Create admin instance and save model
		admin_instance = DeviceAdmin(Device, None)
		admin_instance.save_model(request, device, None, False)
		
		# Verify created_by was set
		self.assertEqual(device.created_by, self.admin_user)
		
		# Verify the device was saved
		saved_device = Device.objects.get(name='form-test-device')
		self.assertEqual(saved_device.model, 'C3560X') 