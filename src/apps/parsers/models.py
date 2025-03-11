from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.projects.models import Project
import os
import uuid

def device_file_path(instance, filename):
	"""
	Function to generate a unique path for uploaded device configuration files.
	
	Args:
		instance: The DeviceFile instance being saved
		filename: The original filename
	
	Returns:
		str: The path where the file should be saved
	"""
	ext = filename.split('.')[-1]
	new_filename = f"{uuid.uuid4()}.{ext}"
	return os.path.join('device_files', str(instance.project.id), new_filename)

class DeviceType(models.Model):
	"""
	Represents a type of network device (e.g., Cisco Router, Juniper Switch).
	
	Attributes:
		name (str): The name of the device type.
		slug (str): A URL-friendly slug for the device type.
		description (str): A detailed description of the device type.
		created_at (datetime): The datetime when the device type was created.
		updated_at (datetime): The datetime when the device type was last updated.
	"""
	name = models.CharField(_("Device Type Name"), max_length=100)
	slug = models.SlugField(_("Slug"), max_length=100, unique=True)
	description = models.TextField(_("Description"), blank=True)
	created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
	updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
	
	class Meta:
		verbose_name = _("Device Type")
		verbose_name_plural = _("Device Types")
		ordering = ["name"]
	
	def __str__(self):
		return self.name

class DeviceFile(models.Model):
	"""
	Represents an uploaded device configuration file.
	
	Attributes:
		project (Project): The project this device file belongs to.
		device_type (DeviceType): The type of device this configuration is for.
		file (FileField): The uploaded configuration file.
		name (str): A friendly name for the device configuration.
		parsed (bool): Whether the file has been successfully parsed.
		parse_errors (str): Any errors encountered during parsing.
		created_at (datetime): The datetime when the file was uploaded.
		updated_at (datetime): The datetime when the file was last updated.
	"""
	project = models.ForeignKey(
		Project,
		on_delete=models.CASCADE,
		related_name="device_files",
		verbose_name=_("Project")
	)
	device_type = models.ForeignKey(
		DeviceType,
		on_delete=models.PROTECT,
		related_name="device_files",
		verbose_name=_("Device Type")
	)
	file = models.FileField(_("Configuration File"), upload_to=device_file_path)
	name = models.CharField(_("Device Name"), max_length=255)
	parsed = models.BooleanField(_("Parsed"), default=False)
	parse_errors = models.TextField(_("Parse Errors"), blank=True)
	notes = models.TextField(_("Notes"), blank=True)
	created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
	updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
	
	class Meta:
		verbose_name = _("Device File")
		verbose_name_plural = _("Device Files")
		ordering = ["-created_at"]
	
	def __str__(self):
		return f"{self.name} ({self.device_type.name})"
	
	def filename(self):
		"""Return the filename of the uploaded file"""
		return os.path.basename(self.file.name)
