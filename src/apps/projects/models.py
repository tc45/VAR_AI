from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from apps.clients.models import Client

User = get_user_model()

class ProjectStatus(models.TextChoices):
	"""Status options for projects."""
	DRAFT = 'draft', _('Draft')
	ACTIVE = 'active', _('Active')
	ON_HOLD = 'on_hold', _('On Hold')
	COMPLETED = 'completed', _('Completed')
	ARCHIVED = 'archived', _('Archived')

class Project(models.Model):
	"""
	Project model to represent client projects.
	
	Projects are associated with a client and contain the project intent,
	which guides AI-assisted report generation.
	"""
	client = models.ForeignKey(
		Client,
		on_delete=models.CASCADE,
		related_name='projects',
		verbose_name=_('Client'),
		help_text=_('The client this project belongs to')
	)
	name = models.CharField(
		_('Project Name'),
		max_length=255,
		help_text=_('The name of the project')
	)
	intent = models.TextField(
		_('Project Intent'),
		blank=True,
		help_text=_('Description of project goals and intent for AI-assisted reporting')
	)
	status = models.CharField(
		_('Status'),
		max_length=20,
		choices=ProjectStatus.choices,
		default=ProjectStatus.DRAFT,
		help_text=_('Current status of the project')
	)
	start_date = models.DateField(
		_('Start Date'),
		null=True,
		blank=True,
		help_text=_('The date when the project started')
	)
	end_date = models.DateField(
		_('End Date'),
		null=True,
		blank=True,
		help_text=_('The date when the project ended or is expected to end')
	)
	is_split_off = models.BooleanField(
		_('Split-off Project'),
		default=False,
		help_text=_('Whether this is a split-off project from a main project')
	)
	parent_project = models.ForeignKey(
		'self',
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='child_projects',
		verbose_name=_('Parent Project'),
		help_text=_('The parent project if this is a split-off project')
	)
	notes = models.TextField(
		_('Notes'),
		blank=True,
		help_text=_('Additional notes about the project')
	)
	
	# Standard fields
	created_at = models.DateTimeField(
		_('Created At'),
		auto_now_add=True,
		help_text=_('Date and time when the project was created')
	)
	updated_at = models.DateTimeField(
		_('Updated At'),
		auto_now=True,
		help_text=_('Date and time when the project was last updated')
	)
	created_by = models.ForeignKey(
		User,
		on_delete=models.SET_NULL,
		null=True,
		related_name='created_projects',
		verbose_name=_('Created By'),
		help_text=_('User who created this project')
	)
	
	class Meta:
		"""Meta options for Project model."""
		verbose_name = _('Project')
		verbose_name_plural = _('Projects')
		ordering = ['-created_at']
		indexes = [
			models.Index(fields=['client', 'name']),
			models.Index(fields=['status']),
		]
	
	def __str__(self) -> str:
		"""Return string representation of Project."""
		return f"{self.client.name} - {self.name}"
