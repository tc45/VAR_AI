from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Client
from .serializers import ClientSerializer
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .forms import ClientForm
from apps.projects.models import Project

# Create your views here.

class ClientViewSet(viewsets.ModelViewSet):
	"""
	API endpoint that allows clients to be viewed or edited.
	
	list:
		Return a list of all clients.
	
	create:
		Create a new client.
	
	retrieve:
		Return a client instance.
	
	update:
		Update a client instance.
	
	partial_update:
		Update a client instance partially.
	
	destroy:
		Delete a client instance.
	"""
	queryset = Client.objects.all().order_by('-created_at')
	serializer_class = ClientSerializer
	permission_classes = [permissions.IsAuthenticated]
	filterset_fields = ['name', 'active']
	search_fields = ['name', 'contact_name', 'contact_email']
	ordering_fields = ['name', 'created_at', 'updated_at']

class ClientIndexView(LoginRequiredMixin, TemplateView):
	"""View for the clients landing page."""
	template_name = 'clients/index.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['recent_clients'] = Client.objects.order_by('-created_at')[:5]
		context['recent_projects'] = Project.objects.order_by('-created_at')[:5]
		context['total_clients'] = Client.objects.count()
		context['total_projects'] = Project.objects.count()
		context['active_projects'] = Project.objects.filter(status='active').count()
		return context

class ClientListView(LoginRequiredMixin, ListView):
	"""View for listing all clients."""
	model = Client
	template_name = 'clients/client_list.html'
	context_object_name = 'clients'
	paginate_by = 10
	
	def get_queryset(self):
		"""Filter clients based on search query."""
		queryset = super().get_queryset()
		search_query = self.request.GET.get('search', '')
		if search_query:
			queryset = queryset.filter(name__icontains=search_query)
		return queryset

class ClientDetailView(LoginRequiredMixin, DetailView):
	"""View for displaying client details."""
	model = Client
	template_name = 'clients/client_detail.html'
	context_object_name = 'client'

class ClientCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
	"""View for creating a new client."""
	model = Client
	form_class = ClientForm
	template_name = 'clients/client_form.html'
	success_url = reverse_lazy('clients:client-list')
	permission_required = 'clients.add_client'
	
	def form_valid(self, form):
		"""Set the created_by field to the current user."""
		form.instance.created_by = self.request.user
		messages.success(self.request, _('Client created successfully.'))
		return super().form_valid(form)

class ClientUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
	"""View for updating an existing client."""
	model = Client
	form_class = ClientForm
	template_name = 'clients/client_form.html'
	permission_required = 'clients.change_client'
	
	def get_success_url(self):
		"""Return to the client detail page after successful update."""
		return reverse_lazy('clients:client-detail', kwargs={'pk': self.object.pk})
	
	def form_valid(self, form):
		"""Display success message on valid form submission."""
		messages.success(self.request, _('Client updated successfully.'))
		return super().form_valid(form)

class ClientDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
	"""View for deleting a client."""
	model = Client
	template_name = 'clients/client_confirm_delete.html'
	success_url = reverse_lazy('clients:client-list')
	permission_required = 'clients.delete_client'
	
	def delete(self, request, *args, **kwargs):
		"""Display success message on deletion."""
		messages.success(request, _('Client deleted successfully.'))
		return super().delete(request, *args, **kwargs)
