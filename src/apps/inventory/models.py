from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from apps.parsers.models import DeviceFile, DeviceType
from apps.projects.models import Project
import uuid
import json

User = get_user_model()

class Device(models.Model):
	"""
	Device model to represent network devices.
	
	Stores device information, configuration details, and relationships
	to projects and inventory items.
	"""
	project = models.ForeignKey(
		Project,
		on_delete=models.CASCADE,
		related_name='devices',
		verbose_name=_('Project'),
		help_text=_('The project this device belongs to')
	)
	name = models.CharField(
		_('Device Name'),
		max_length=255,
		help_text=_('The hostname or identifier of the device')
	)
	device_type = models.ForeignKey(
		DeviceType,
		on_delete=models.CASCADE,
		verbose_name=_('Device Type'),
		help_text=_('The type/platform of the device')
	)
	model = models.CharField(
		_('Model'),
		max_length=100,
		blank=True,
		help_text=_('The hardware model of the device')
	)
	firmware_version = models.CharField(
		_('Firmware Version'),
		max_length=100,
		blank=True,
		help_text=_('The firmware/OS version running on the device')
	)
	serial_number = models.CharField(
		_('Serial Number'),
		max_length=100,
		blank=True,
		help_text=_('The serial number of the device')
	)
	management_ip = models.GenericIPAddressField(
		_('Management IP'),
		null=True,
		blank=True,
		help_text=_('The management IP address of the device')
	)
	interface_count = models.PositiveIntegerField(
		_('Interface Count'),
		default=0,
		help_text=_('Total number of interfaces on the device')
	)
	route_count = models.PositiveIntegerField(
		_('Route Count'),
		default=0,
		help_text=_('Total number of routes in the routing table')
	)
	acl_count = models.PositiveIntegerField(
		_('ACL Count'),
		default=0,
		help_text=_('Total number of ACL rules configured')
	)
	sfp_count = models.PositiveIntegerField(
		_('SFP Count'),
		default=0,
		help_text=_('Total number of SFP modules installed')
	)
	ipsec_tunnel_count = models.PositiveIntegerField(
		_('IPSec Tunnel Count'),
		default=0,
		help_text=_('Total number of configured IPSec tunnels')
	)
	routing_protocols = models.JSONField(
		_('Routing Protocols'),
		default=dict,
		help_text=_('JSON object containing routing protocol details')
	)
	last_config_snapshot = models.DateTimeField(
		_('Last Config Snapshot'),
		null=True,
		blank=True,
		help_text=_('When the last configuration snapshot was taken')
	)
	notes = models.TextField(
		_('Notes'),
		blank=True,
		help_text=_('Additional notes about the device')
	)
	
	# Standard fields
	created_at = models.DateTimeField(
		_('Created At'),
		auto_now_add=True,
		help_text=_('Date and time when the device was created')
	)
	updated_at = models.DateTimeField(
		_('Updated At'),
		auto_now=True,
		help_text=_('Date and time when the device was last updated')
	)
	created_by = models.ForeignKey(
		User,
		on_delete=models.SET_NULL,
		null=True,
		related_name='created_devices',
		verbose_name=_('Created By'),
		help_text=_('User who created this device')
	)
	
	class Meta:
		"""Meta options for Device model."""
		verbose_name = _('Device')
		verbose_name_plural = _('Devices')
		ordering = ['project', 'name']
		indexes = [
			models.Index(fields=['project', 'name']),
			models.Index(fields=['device_type']),
		]
		unique_together = ['project', 'name']
	
	def __str__(self) -> str:
		"""Return string representation of Device."""
		return f"{self.project.name} - {self.name} ({self.device_type.name})"

class Interface(models.Model):
	"""
	Represents a network interface on a device.
	"""
	device = models.ForeignKey(
		Device,
		on_delete=models.CASCADE,
		related_name="interfaces",
		verbose_name=_("Device")
	)
	name = models.CharField(
		_("Interface Name"),
		max_length=255
	)
	description = models.CharField(
		_("Description"),
		max_length=255,
		blank=True
	)
	ip_address = models.GenericIPAddressField(
		_("IP Address"),
		blank=True,
		null=True
	)
	subnet_mask = models.CharField(
		_("Subnet Mask"),
		max_length=15,
		blank=True
	)
	mac_address = models.CharField(
		_("MAC Address"),
		max_length=17,
		blank=True
	)
	is_up = models.BooleanField(
		_("Is Up"),
		default=True
	)
	is_enabled = models.BooleanField(
		_("Is Enabled"),
		default=True
	)
	speed = models.IntegerField(
		_("Speed (Mbps)"),
		blank=True,
		null=True
	)
	mtu = models.IntegerField(
		_("MTU"),
		blank=True,
		null=True
	)
	created_at = models.DateTimeField(
		_("Created At"),
		auto_now_add=True
	)
	updated_at = models.DateTimeField(
		_("Updated At"),
		auto_now=True
	)
	created_by = models.ForeignKey(
		User,
		on_delete=models.SET_NULL,
		null=True,
		related_name="created_interfaces",
		verbose_name=_("Created By")
	)
	
	class Meta:
		verbose_name = _("Interface")
		verbose_name_plural = _("Interfaces")
		ordering = ["device", "name"]
		unique_together = ["device", "name"]
	
	def __str__(self):
		return f"{self.device.name}:{self.name}"

class VRF(models.Model):
	"""
	Represents a Virtual Routing and Forwarding instance.
	"""
	device = models.ForeignKey(
		Device,
		on_delete=models.CASCADE,
		related_name="vrfs",
		verbose_name=_("Device")
	)
	name = models.CharField(
		_("VRF Name"),
		max_length=255
	)
	description = models.CharField(
		_("Description"),
		max_length=255,
		blank=True
	)
	route_distinguisher = models.CharField(
		_("Route Distinguisher"),
		max_length=100,
		blank=True
	)
	created_at = models.DateTimeField(
		_("Created At"),
		auto_now_add=True
	)
	updated_at = models.DateTimeField(
		_("Updated At"),
		auto_now=True
	)
	created_by = models.ForeignKey(
		User,
		on_delete=models.SET_NULL,
		null=True,
		related_name="created_vrfs",
		verbose_name=_("Created By")
	)
	
	class Meta:
		verbose_name = _("VRF")
		verbose_name_plural = _("VRFs")
		ordering = ["device", "name"]
		unique_together = ["device", "name"]
	
	def __str__(self):
		return f"{self.device.name}:{self.name}"

class ACL(models.Model):
	"""
	Represents an Access Control List.
	"""
	TYPE_CHOICES = [
		('standard', _('Standard')),
		('extended', _('Extended')),
		('other', _('Other')),
	]
	
	device = models.ForeignKey(
		Device,
		on_delete=models.CASCADE,
		related_name="acls",
		verbose_name=_("Device")
	)
	name = models.CharField(
		_("ACL Name"),
		max_length=255
	)
	type = models.CharField(
		_("Type"),
		max_length=20,
		choices=TYPE_CHOICES,
		default='extended'
	)
	rules = models.JSONField(
		_("Rules"),
		default=dict
	)
	created_at = models.DateTimeField(
		_("Created At"),
		auto_now_add=True
	)
	updated_at = models.DateTimeField(
		_("Updated At"),
		auto_now=True
	)
	created_by = models.ForeignKey(
		User,
		on_delete=models.SET_NULL,
		null=True,
		related_name="created_acls",
		verbose_name=_("Created By")
	)
	
	class Meta:
		verbose_name = _("ACL")
		verbose_name_plural = _("ACLs")
		ordering = ["device", "name"]
		unique_together = ["device", "name"]
	
	def __str__(self):
		return f"{self.device.name}:{self.name}"
	
	def get_rules(self):
		"""Return the rules as a Python object"""
		if isinstance(self.rules, str):
			return json.loads(self.rules)
		return self.rules

class RouteTable(models.Model):
	"""
	Represents a routing table from a device.
	"""
	device = models.ForeignKey(
		Device,
		on_delete=models.CASCADE,
		related_name="route_tables",
		verbose_name=_("Device")
	)
	vrf = models.ForeignKey(
		VRF,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="route_tables",
		verbose_name=_("VRF")
	)
	routes = models.JSONField(
		_("Routes"),
		default=dict
	)
	created_at = models.DateTimeField(
		_("Created At"),
		auto_now_add=True
	)
	updated_at = models.DateTimeField(
		_("Updated At"),
		auto_now=True
	)
	created_by = models.ForeignKey(
		User,
		on_delete=models.SET_NULL,
		null=True,
		related_name="created_route_tables",
		verbose_name=_("Created By")
	)
	
	class Meta:
		verbose_name = _("Route Table")
		verbose_name_plural = _("Route Tables")
		ordering = ["device", "vrf__name"]
		unique_together = ["device", "vrf"]
	
	def __str__(self):
		vrf_name = self.vrf.name if self.vrf else "Global"
		return f"{self.device.name}:{vrf_name}"
	
	def get_routes(self):
		"""Return the routes as a Python object"""
		if isinstance(self.routes, str):
			return json.loads(self.routes)
		return self.routes

class InventoryItemType(models.TextChoices):
	"""Types of inventory items that can be tracked."""
	INTERFACE = 'interface', _('Interface')
	ACL = 'acl', _('Access Control List')
	VRF = 'vrf', _('Virtual Routing and Forwarding')
	ROUTE = 'route', _('Route')
	IPSEC_TUNNEL = 'ipsec_tunnel', _('IPSec Tunnel')
	SFP = 'sfp', _('SFP Module')
	OTHER = 'other', _('Other')

class InventoryItem(models.Model):
	"""
	InventoryItem model to store structured data about device components.
	
	This model represents various types of inventory items like interfaces,
	ACLs, VRFs, routes, etc. The data is stored in a flexible JSON structure
	to accommodate different item types.
	"""
	device = models.ForeignKey(
		Device,
		on_delete=models.CASCADE,
		related_name='inventory_items',
		verbose_name=_('Device'),
		help_text=_('The device this inventory item belongs to')
	)
	item_type = models.CharField(
		_('Item Type'),
		max_length=20,
		choices=InventoryItemType.choices,
		help_text=_('The type of inventory item')
	)
	name = models.CharField(
		_('Item Name'),
		max_length=255,
		help_text=_('The name or identifier of the item')
	)
	description = models.TextField(
		_('Description'),
		blank=True,
		help_text=_('Description of the inventory item')
	)
	data = models.JSONField(
		_('Item Data'),
		help_text=_('JSON object containing item-specific data')
	)
	is_active = models.BooleanField(
		_('Is Active'),
		default=True,
		help_text=_('Whether this item is currently active')
	)
	last_seen = models.DateTimeField(
		_('Last Seen'),
		null=True,
		blank=True,
		help_text=_('When this item was last observed in device configuration')
	)
	
	# Standard fields
	created_at = models.DateTimeField(
		_('Created At'),
		auto_now_add=True,
		help_text=_('Date and time when the item was created')
	)
	updated_at = models.DateTimeField(
		_('Updated At'),
		auto_now=True,
		help_text=_('Date and time when the item was last updated')
	)
	created_by = models.ForeignKey(
		User,
		on_delete=models.SET_NULL,
		null=True,
		related_name='created_inventory_items',
		verbose_name=_('Created By'),
		help_text=_('User who created this inventory item')
	)
	
	class Meta:
		"""Meta options for InventoryItem model."""
		verbose_name = _('Inventory Item')
		verbose_name_plural = _('Inventory Items')
		ordering = ['device', 'item_type', 'name']
		indexes = [
			models.Index(fields=['device', 'item_type', 'name']),
			models.Index(fields=['item_type']),
		]
		unique_together = ['device', 'item_type', 'name']
	
	def __str__(self) -> str:
		"""Return string representation of InventoryItem."""
		return f"{self.device.name} - {self.get_item_type_display()} - {self.name}"
