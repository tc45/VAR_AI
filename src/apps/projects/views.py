from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Project
from .serializers import ProjectSerializer
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from django.db.models import Count
import json

from apps.clients.models import Client
from apps.parsers.models import DeviceFile
from .forms import ProjectForm

# Create your views here.

class ProjectViewSet(viewsets.ModelViewSet):
	"""
	API endpoint that allows projects to be viewed or edited.
	
	list:
		Return a list of all projects.
	
	create:
		Create a new project.
	
	retrieve:
		Return a project instance.
	
	update:
		Update a project instance.
	
	partial_update:
		Update a project instance partially.
	
	destroy:
		Delete a project instance.
	"""
	queryset = Project.objects.all().order_by('-created_at')
	serializer_class = ProjectSerializer
	permission_classes = [permissions.IsAuthenticated]
	filterset_fields = ['name', 'client', 'status']
	search_fields = ['name', 'description', 'client__name']
	ordering_fields = ['name', 'client__name', 'status', 'start_date', 'end_date', 'created_at']

class ProjectListView(LoginRequiredMixin, ListView):
	"""View for listing all projects."""
	model = Project
	template_name = 'projects/project_list.html'
	context_object_name = 'projects'
	paginate_by = 10
	
	def get_queryset(self):
		"""Filter projects based on search query and client."""
		queryset = super().get_queryset()
		search_query = self.request.GET.get('search', '')
		client_id = self.request.GET.get('client', '')
		
		if search_query:
			queryset = queryset.filter(name__icontains=search_query)
		
		if client_id:
			queryset = queryset.filter(client_id=client_id)
		
		return queryset
	
	def get_context_data(self, **kwargs):
		"""Add client filter to context."""
		context = super().get_context_data(**kwargs)
		client_id = self.request.GET.get('client', '')
		if client_id:
			context['selected_client'] = get_object_or_404(Client, pk=client_id)
		return context

class ProjectDetailView(LoginRequiredMixin, DetailView):
	"""View for displaying project details."""
	model = Project
	template_name = 'projects/project_detail.html'
	context_object_name = 'project'

class ProjectCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
	"""View for creating a new project."""
	model = Project
	form_class = ProjectForm
	template_name = 'projects/project_form.html'
	permission_required = 'projects.add_project'
	
	def get_initial(self):
		"""Set initial client if provided in GET parameters."""
		initial = super().get_initial()
		client_id = self.request.GET.get('client')
		if client_id:
			initial['client'] = get_object_or_404(Client, pk=client_id)
		return initial
	
	def form_valid(self, form):
		"""Set the created_by field to the current user."""
		form.instance.created_by = self.request.user
		messages.success(self.request, _('Project created successfully.'))
		return super().form_valid(form)
	
	def get_success_url(self):
		"""Return to the project detail page after successful creation."""
		return reverse_lazy('projects:project-detail', kwargs={'pk': self.object.pk})

class ProjectUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
	"""View for updating an existing project."""
	model = Project
	form_class = ProjectForm
	template_name = 'projects/project_form.html'
	permission_required = 'projects.change_project'
	
	def form_valid(self, form):
		"""Display success message on valid form submission."""
		messages.success(self.request, _('Project updated successfully.'))
		return super().form_valid(form)
	
	def get_success_url(self):
		"""Return to the project detail page after successful update."""
		return reverse_lazy('projects:project-detail', kwargs={'pk': self.object.pk})

class ProjectDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
	"""View for deleting a project."""
	model = Project
	template_name = 'projects/project_confirm_delete.html'
	permission_required = 'projects.delete_project'
	
	def get_success_url(self):
		"""Return to the client detail page after successful deletion."""
		client_id = self.object.client.pk
		messages.success(self.request, _('Project deleted successfully.'))
		return reverse_lazy('clients:client-detail', kwargs={'pk': client_id})

class ProjectIndexView(LoginRequiredMixin, TemplateView):
	"""View for the projects landing page."""
	template_name = 'projects/index.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		
		# Get recent projects
		context['recent_projects'] = Project.objects.order_by('-created_at')[:5]
		
		# Get project statistics
		context['total_projects'] = Project.objects.count()
		context['total_clients'] = Client.objects.count()
		
		# Get projects by status
		projects_by_status = (
			Project.objects.values('status')
			.annotate(count=Count('id'))
			.order_by('status')
		)
		context['projects_by_status'] = projects_by_status
		
		# Prepare chart data
		chart_data = {
			'labels': [status['status'] for status in projects_by_status],
			'data': [status['count'] for status in projects_by_status]
		}
		context['chart_data'] = json.dumps(chart_data)
		
		# Get device counts
		context['total_devices'] = DeviceFile.objects.count()
		
		return context
