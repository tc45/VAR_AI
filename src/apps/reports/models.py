from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from apps.projects.models import Project
import uuid
import os

def report_file_path(instance, filename):
	"""
	Function to generate a unique path for report files.
	
	Args:
		instance: The Report instance being saved
		filename: The original filename
	
	Returns:
		str: The path where the file should be saved
	"""
	ext = filename.split('.')[-1]
	new_filename = f"{uuid.uuid4()}.{ext}"
	return os.path.join('reports', str(instance.project.id), new_filename)

class ReportType(models.Model):
	"""
	Represents a type of report that can be generated.
	
	Attributes:
		name (str): The name of the report type.
		slug (str): A URL-friendly slug for the report type.
		description (str): A description of the report type.
		created_at (datetime): The datetime when the report type was created.
		updated_at (datetime): The datetime when the report type was last updated.
	"""
	name = models.CharField(_("Report Type Name"), max_length=100)
	slug = models.SlugField(_("Slug"), max_length=100, unique=True)
	description = models.TextField(_("Description"), blank=True)
	created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
	updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
	
	class Meta:
		verbose_name = _("Report Type")
		verbose_name_plural = _("Report Types")
		ordering = ["name"]
	
	def __str__(self):
		return self.name

class Report(models.Model):
	"""
	Represents a generated report.
	
	Attributes:
		project (Project): The project this report is for.
		report_type (ReportType): The type of this report.
		name (str): A name for this report.
		parameters (json): The parameters used to generate this report.
		file (FileField): The generated report file.
		created_by (User): The user who created this report.
		created_at (datetime): The datetime when the report was created.
		updated_at (datetime): The datetime when the report was last updated.
	"""
	STATUS_CHOICES = [
		('pending', _('Pending')),
		('in_progress', _('In Progress')),
		('completed', _('Completed')),
		('failed', _('Failed')),
	]
	
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	project = models.ForeignKey(
		Project,
		on_delete=models.CASCADE,
		related_name="reports",
		verbose_name=_("Project")
	)
	report_type = models.ForeignKey(
		ReportType,
		on_delete=models.PROTECT,
		related_name="reports",
		verbose_name=_("Report Type")
	)
	name = models.CharField(_("Report Name"), max_length=255)
	description = models.TextField(_("Description"), blank=True)
	parameters = models.JSONField(_("Parameters"), default=dict)
	file = models.FileField(_("Report File"), upload_to=report_file_path, blank=True, null=True)
	status = models.CharField(
		_("Status"),
		max_length=20,
		choices=STATUS_CHOICES,
		default='pending'
	)
	error_message = models.TextField(_("Error Message"), blank=True)
	created_by = models.ForeignKey(
		User,
		on_delete=models.SET_NULL,
		null=True,
		related_name="created_reports",
		verbose_name=_("Created By")
	)
	created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
	updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
	
	class Meta:
		verbose_name = _("Report")
		verbose_name_plural = _("Reports")
		ordering = ["-created_at"]
	
	def __str__(self):
		return f"{self.name} ({self.project.name})"
	
	def filename(self):
		"""Return the filename of the report file"""
		if self.file:
			return os.path.basename(self.file.name)
		return None
