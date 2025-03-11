from django.contrib import admin
from .models import Device, Interface, VRF, ACL, RouteTable, InventoryItem

class InterfaceInline(admin.TabularInline):
	"""Inline admin for interfaces."""
	model = Interface
	extra = 0
	fields = ('name', 'description', 'ip_address', 'subnet_mask', 'is_up', 'is_enabled')
	readonly_fields = ('created_at', 'updated_at')

class VRFInline(admin.TabularInline):
	"""Inline admin for VRFs."""
	model = VRF
	extra = 0
	fields = ('name', 'description', 'route_distinguisher')
	readonly_fields = ('created_at', 'updated_at')

class ACLInline(admin.TabularInline):
	"""Inline admin for ACLs."""
	model = ACL
	extra = 0
	fields = ('name', 'type')
	readonly_fields = ('created_at', 'updated_at')

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
	"""Admin configuration for Device model."""
	list_display = ['name', 'project', 'device_type', 'model', 'management_ip']
	list_filter = ['device_type', 'project']
	search_fields = ['name', 'model', 'serial_number']
	readonly_fields = ['created_at', 'updated_at', 'created_by']
	inlines = [InterfaceInline, VRFInline, ACLInline]
	
	fieldsets = (
		(None, {
			'fields': ('project', 'name', 'device_type', 'model')
		}),
		('Hardware Details', {
			'fields': ('firmware_version', 'serial_number', 'management_ip')
		}),
		('Statistics', {
			'fields': ('interface_count', 'route_count', 'acl_count', 'sfp_count', 'ipsec_tunnel_count')
		}),
		('Configuration', {
			'fields': ('routing_protocols', 'last_config_snapshot')
		}),
		('Additional Information', {
			'fields': ('notes', 'created_at', 'updated_at', 'created_by')
		}),
	)
	
	def save_model(self, request, obj, form, change):
		"""Save model and set created_by if not set."""
		if not change:  # Only set created_by during the first save
			obj.created_by = request.user
		super().save_model(request, obj, form, change)

@admin.register(Interface)
class InterfaceAdmin(admin.ModelAdmin):
	"""Admin configuration for Interface model."""
	list_display = ['name', 'device', 'ip_address', 'is_up', 'is_enabled']
	list_filter = ['device', 'is_up', 'is_enabled']
	search_fields = ['name', 'description', 'ip_address']
	readonly_fields = ['created_at', 'updated_at', 'created_by']
	
	fieldsets = (
		(None, {
			'fields': ('device', 'name', 'description')
		}),
		('Network Configuration', {
			'fields': ('ip_address', 'subnet_mask', 'mac_address')
		}),
		('Status', {
			'fields': ('is_up', 'is_enabled', 'speed', 'mtu')
		}),
		('Additional Information', {
			'fields': ('created_at', 'updated_at', 'created_by')
		}),
	)
	
	def save_model(self, request, obj, form, change):
		"""Save model and set created_by if not set."""
		if not change:  # Only set created_by during the first save
			obj.created_by = request.user
		super().save_model(request, obj, form, change)

@admin.register(VRF)
class VRFAdmin(admin.ModelAdmin):
	"""Admin configuration for VRF model."""
	list_display = ['name', 'device', 'route_distinguisher']
	list_filter = ['device']
	search_fields = ['name', 'description', 'route_distinguisher']
	readonly_fields = ['created_at', 'updated_at', 'created_by']
	
	fieldsets = (
		(None, {
			'fields': ('device', 'name', 'description')
		}),
		('VRF Configuration', {
			'fields': ('route_distinguisher',)
		}),
		('Additional Information', {
			'fields': ('created_at', 'updated_at', 'created_by')
		}),
	)
	
	def save_model(self, request, obj, form, change):
		"""Save model and set created_by if not set."""
		if not change:  # Only set created_by during the first save
			obj.created_by = request.user
		super().save_model(request, obj, form, change)

@admin.register(ACL)
class ACLAdmin(admin.ModelAdmin):
	"""Admin configuration for ACL model."""
	list_display = ['name', 'device', 'type']
	list_filter = ['device', 'type']
	search_fields = ['name']
	readonly_fields = ['created_at', 'updated_at', 'created_by']
	
	fieldsets = (
		(None, {
			'fields': ('device', 'name', 'type')
		}),
		('ACL Configuration', {
			'fields': ('rules',)
		}),
		('Additional Information', {
			'fields': ('created_at', 'updated_at', 'created_by')
		}),
	)
	
	def save_model(self, request, obj, form, change):
		"""Save model and set created_by if not set."""
		if not change:  # Only set created_by during the first save
			obj.created_by = request.user
		super().save_model(request, obj, form, change)

@admin.register(RouteTable)
class RouteTableAdmin(admin.ModelAdmin):
	"""Admin configuration for RouteTable model."""
	list_display = ['device', 'vrf']
	list_filter = ['device', 'vrf']
	readonly_fields = ['created_at', 'updated_at', 'created_by']
	
	fieldsets = (
		(None, {
			'fields': ('device', 'vrf')
		}),
		('Route Configuration', {
			'fields': ('routes',)
		}),
		('Additional Information', {
			'fields': ('created_at', 'updated_at', 'created_by')
		}),
	)
	
	def save_model(self, request, obj, form, change):
		"""Save model and set created_by if not set."""
		if not change:  # Only set created_by during the first save
			obj.created_by = request.user
		super().save_model(request, obj, form, change)

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
	"""Admin configuration for InventoryItem model."""
	list_display = ['name', 'device', 'item_type', 'is_active']
	list_filter = ['device', 'item_type', 'is_active']
	search_fields = ['name', 'description']
	readonly_fields = ['created_at', 'updated_at', 'created_by']
	
	fieldsets = (
		(None, {
			'fields': ('device', 'item_type', 'name')
		}),
		('Item Details', {
			'fields': ('description', 'data', 'is_active', 'last_seen')
		}),
		('Additional Information', {
			'fields': ('created_at', 'updated_at', 'created_by')
		}),
	)
	
	def save_model(self, request, obj, form, change):
		"""Save model and set created_by if not set."""
		if not change:  # Only set created_by during the first save
			obj.created_by = request.user
		super().save_model(request, obj, form, change)
