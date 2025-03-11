from django.contrib import admin
from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
	"""Admin configuration for Client model."""
	list_display = ['name', 'primary_contact_name', 'primary_contact_email', 'created_at']
	list_filter = ['created_at']
	search_fields = ['name', 'primary_contact_name', 'primary_contact_email']
	readonly_fields = ['created_at', 'updated_at', 'created_by']
	
	fieldsets = (
		(None, {
			'fields': ('name', 'industry', 'website')
		}),
		('Primary Contact', {
			'fields': ('primary_contact_name', 'primary_contact_email', 'primary_contact_phone')
		}),
		('Secondary Contact', {
			'fields': ('secondary_contact_name', 'secondary_contact_email', 'secondary_contact_phone')
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
