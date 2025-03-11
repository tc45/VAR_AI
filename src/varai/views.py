from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.clients.models import Client
from apps.projects.models import Project
from apps.parsers.models import DeviceFile
from apps.reports.models import Report

class HomeView(TemplateView):
	"""View for the home page"""
	template_name = 'home.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		if self.request.user.is_authenticated:
			# Get counts
			context['client_count'] = Client.objects.count()
			context['project_count'] = Project.objects.count()
			context['device_count'] = DeviceFile.objects.count()
			context['report_count'] = Report.objects.count()

			# Get recent items
			context['recent_projects'] = Project.objects.order_by('-created_at')[:5]
			context['recent_device_files'] = DeviceFile.objects.order_by('-created_at')[:5]

		return context 