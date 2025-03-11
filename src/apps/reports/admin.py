from django.contrib import admin
from .models import ReportType, Report

@admin.register(ReportType)
class ReportTypeAdmin(admin.ModelAdmin):
	"""Admin interface for ReportType model"""
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

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
	"""Admin interface for Report model"""
	list_display = ('name', 'project', 'report_type', 'status', 'created_by', 'created_at')
	list_filter = ('status', 'report_type', 'project', 'created_at')
	search_fields = ('name', 'description', 'project__name', 'created_by__username')
	readonly_fields = ('created_by', 'created_at', 'updated_at')
	fieldsets = (
		(None, {
			'fields': ('name', 'project', 'report_type')
		}),
		('Report Details', {
			'fields': ('description', 'parameters', 'file', 'status')
		}),
		('Error Information', {
			'fields': ('error_message',),
			'classes': ('collapse',),
		}),
		('Additional Information', {
			'fields': ('created_by', 'created_at', 'updated_at')
		}),
	)
