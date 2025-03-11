from django.contrib import admin
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
	"""Admin configuration for Project model."""
	list_display = ['name', 'client', 'status', 'start_date', 'end_date']
	list_filter = ['status', 'client', 'is_split_off']
	search_fields = ['name', 'client__name', 'intent']
	readonly_fields = ['created_at', 'updated_at', 'created_by']
	
	fieldsets = (
		(None, {
			'fields': ('client', 'name', 'status')
		}),
		('Project Details', {
			'fields': ('intent', 'start_date', 'end_date')
		}),
		('Split Project Information', {
			'fields': ('is_split_off', 'parent_project'),
			'classes': ('collapse',),
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
