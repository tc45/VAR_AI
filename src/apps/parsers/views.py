from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from django.db.models import Count
import json

from apps.projects.models import Project
from .models import DeviceFile, DeviceType
from .forms import DeviceFileForm

# Create your views here.

class ParserIndexView(LoginRequiredMixin, TemplateView):
	"""View for the device management landing page."""
	template_name = 'parsers/index.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['recent_device_files'] = DeviceFile.objects.order_by('-created_at')[:5]
		context['device_types'] = DeviceType.objects.annotate(
			device_count=Count('devicefile')
		).order_by('-device_count')
		context['total_devices'] = DeviceFile.objects.count()
		context['device_type_count'] = DeviceType.objects.count()
		context['projects_with_devices'] = Project.objects.filter(devicefile__isnull=False).distinct().count()

		# Prepare data for the device distribution chart
		device_type_data = DeviceType.objects.annotate(
			count=Count('devicefile')
		).values('name', 'count')
		
		context['device_type_labels'] = json.dumps([dt['name'] for dt in device_type_data])
		context['device_type_counts'] = json.dumps([dt['count'] for dt in device_type_data])

		return context

class DeviceFileListView(LoginRequiredMixin, ListView):
	"""View for listing all device files."""
	model = DeviceFile
	template_name = 'parsers/devicefile_list.html'
	context_object_name = 'device_files'
	paginate_by = 10
	
	def get_queryset(self):
		"""Filter device files based on search query and project."""
		queryset = super().get_queryset()
		search_query = self.request.GET.get('search', '')
		project_id = self.request.GET.get('project', '')
		device_type_id = self.request.GET.get('device_type', '')
		
		if search_query:
			queryset = queryset.filter(name__icontains=search_query)
		
		if project_id:
			queryset = queryset.filter(project_id=project_id)
		
		if device_type_id:
			queryset = queryset.filter(device_type_id=device_type_id)
		
		return queryset
	
	def get_context_data(self, **kwargs):
		"""Add project and device type filters to context."""
		context = super().get_context_data(**kwargs)
		project_id = self.request.GET.get('project', '')
		device_type_id = self.request.GET.get('device_type', '')
		
		if project_id:
			context['selected_project'] = get_object_or_404(Project, pk=project_id)
		
		if device_type_id:
			context['selected_device_type'] = get_object_or_404(DeviceType, pk=device_type_id)
		
		context['device_types'] = DeviceType.objects.all()
		return context

class DeviceFileDetailView(LoginRequiredMixin, DetailView):
	"""View for displaying device file details."""
	model = DeviceFile
	template_name = 'parsers/devicefile_detail.html'
	context_object_name = 'device_file'

class DeviceFileCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
	"""View for creating a new device file."""
	model = DeviceFile
	form_class = DeviceFileForm
	template_name = 'parsers/devicefile_form.html'
	permission_required = 'parsers.add_devicefile'
	
	def get_initial(self):
		"""Set initial project if provided in GET parameters."""
		initial = super().get_initial()
		project_id = self.request.GET.get('project')
		if project_id:
			initial['project'] = get_object_or_404(Project, pk=project_id)
		return initial
	
	def form_valid(self, form):
		"""Set additional fields and trigger parsing."""
		response = super().form_valid(form)
		
		# Trigger file parsing
		try:
			self.object.parse_file()
			messages.success(self.request, _('Device file uploaded and parsed successfully.'))
		except Exception as e:
			messages.error(self.request, _('File uploaded but parsing failed: %(error)s') % {'error': str(e)})
		
		return response
	
	def get_success_url(self):
		"""Return to the project detail page after successful creation."""
		return reverse_lazy('projects:project-detail', kwargs={'pk': self.object.project.pk})

class DeviceFileUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
	"""View for updating an existing device file."""
	model = DeviceFile
	form_class = DeviceFileForm
	template_name = 'parsers/devicefile_form.html'
	permission_required = 'parsers.change_devicefile'
	
	def form_valid(self, form):
		"""Display success message on valid form submission."""
		messages.success(self.request, _('Device file updated successfully.'))
		return super().form_valid(form)
	
	def get_success_url(self):
		"""Return to the project detail page after successful update."""
		return reverse_lazy('projects:project-detail', kwargs={'pk': self.object.project.pk})

class DeviceFileDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
	"""View for deleting a device file."""
	model = DeviceFile
	template_name = 'parsers/devicefile_confirm_delete.html'
	permission_required = 'parsers.delete_devicefile'
	
	def get_success_url(self):
		"""Return to the project detail page after successful deletion."""
		project_id = self.object.project.pk
		messages.success(self.request, _('Device file deleted successfully.'))
		return reverse_lazy('projects:project-detail', kwargs={'pk': project_id})

from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404

from apps.projects.models import Project
from .models import DeviceFile, DeviceType
from .forms import DeviceFileForm

# Create your views here.

class DeviceFileListView(LoginRequiredMixin, ListView):
	"""View for listing all device files."""
	model = DeviceFile
	template_name = 'parsers/devicefile_list.html'
	context_object_name = 'device_files'
	paginate_by = 10
	
	def get_queryset(self):
		"""Filter device files based on search query and project."""
		queryset = super().get_queryset()
		search_query = self.request.GET.get('search', '')
		project_id = self.request.GET.get('project', '')
		device_type_id = self.request.GET.get('device_type', '')
		
		if search_query:
			queryset = queryset.filter(name__icontains=search_query)
		
		if project_id:
			queryset = queryset.filter(project_id=project_id)
		
		if device_type_id:
			queryset = queryset.filter(device_type_id=device_type_id)
		
		return queryset
	
	def get_context_data(self, **kwargs):
		"""Add project and device type filters to context."""
		context = super().get_context_data(**kwargs)
		project_id = self.request.GET.get('project', '')
		device_type_id = self.request.GET.get('device_type', '')
		
		if project_id:
			context['selected_project'] = get_object_or_404(Project, pk=project_id)
		
		if device_type_id:
			context['selected_device_type'] = get_object_or_404(DeviceType, pk=device_type_id)
		
		context['device_types'] = DeviceType.objects.all()
		return context

class DeviceFileDetailView(LoginRequiredMixin, DetailView):
	"""View for displaying device file details."""
	model = DeviceFile
	template_name = 'parsers/devicefile_detail.html'
	context_object_name = 'device_file'

class DeviceFileCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
	"""View for creating a new device file."""
	model = DeviceFile
	form_class = DeviceFileForm
	template_name = 'parsers/devicefile_form.html'
	permission_required = 'parsers.add_devicefile'
	
	def get_initial(self):
		"""Set initial project if provided in GET parameters."""
		initial = super().get_initial()
		project_id = self.request.GET.get('project')
		if project_id:
			initial['project'] = get_object_or_404(Project, pk=project_id)
		return initial
	
	def form_valid(self, form):
		"""Set additional fields and trigger parsing."""
		response = super().form_valid(form)
		
		# Trigger file parsing
		try:
			self.object.parse_file()
			messages.success(self.request, _('Device file uploaded and parsed successfully.'))
		except Exception as e:
			messages.error(self.request, _('File uploaded but parsing failed: %(error)s') % {'error': str(e)})
		
		return response
	
	def get_success_url(self):
		"""Return to the project detail page after successful creation."""
		return reverse_lazy('projects:project-detail', kwargs={'pk': self.object.project.pk})

class DeviceFileUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
	"""View for updating an existing device file."""
	model = DeviceFile
	form_class = DeviceFileForm
	template_name = 'parsers/devicefile_form.html'
	permission_required = 'parsers.change_devicefile'
	
	def form_valid(self, form):
		"""Display success message on valid form submission."""
		messages.success(self.request, _('Device file updated successfully.'))
		return super().form_valid(form)
	
	def get_success_url(self):
		"""Return to the project detail page after successful update."""
		return reverse_lazy('projects:project-detail', kwargs={'pk': self.object.project.pk})

class DeviceFileDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
	"""View for deleting a device file."""
	model = DeviceFile
	template_name = 'parsers/devicefile_confirm_delete.html'
	permission_required = 'parsers.delete_devicefile'
	
	def get_success_url(self):
		"""Return to the project detail page after successful deletion."""
		project_id = self.object.project.pk
		messages.success(self.request, _('Device file deleted successfully.'))
		return reverse_lazy('projects:project-detail', kwargs={'pk': project_id})
