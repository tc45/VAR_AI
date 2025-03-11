from django.contrib import admin
from .models import DeviceType, DeviceFile

@admin.register(DeviceType)
class DeviceTypeAdmin(admin.ModelAdmin):
	"""Admin interface for DeviceType model"""
	list_display = ('name', 'slug', 'created_at')
	prepopulated_fields = {'slug': ('name',)}
	search_fields = ('name', 'description')
	readonly_fields = ('created_at', 'updated_at')
	fieldsets = (
		(None, {
			'fields': ('name', 'slug')
		}),
		('Details', {
			'fields': ('description', 'created_at', 'updated_at')
		}),
	)

@admin.register(DeviceFile)
class DeviceFileAdmin(admin.ModelAdmin):
	"""Admin interface for DeviceFile model"""
	list_display = ('name', 'project', 'device_type', 'parsed', 'created_at')
	list_filter = ('parsed', 'device_type', 'project', 'created_at')
	search_fields = ('name', 'project__name', 'device_type__name')
	readonly_fields = ('parsed', 'parse_errors', 'created_at', 'updated_at')
	fieldsets = (
		(None, {
			'fields': ('name', 'project', 'device_type', 'file')
		}),
		('Parsing Status', {
			'fields': ('parsed', 'parse_errors')
		}),
		('Additional Information', {
			'fields': ('notes', 'created_at', 'updated_at')
		}),
	)
