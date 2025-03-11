from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class Client(models.Model):
	"""
	Client model to represent organizations that own projects.
	
	Stores basic client information, contact details, and metadata.
	"""
	name = models.CharField(
		_("Client Name"),
		max_length=255,
		help_text=_("The name of the client organization")
	)
	industry = models.CharField(
		_("Industry"),
		max_length=100,
		blank=True,
		help_text=_("The industry sector of the client")
	)
	primary_contact_name = models.CharField(
		_("Primary Contact Name"),
		max_length=255,
		blank=True,
		help_text=_("Name of the primary contact person")
	)
	primary_contact_email = models.EmailField(
		_("Primary Contact Email"),
		blank=True,
		help_text=_("Email of the primary contact person")
	)
	primary_contact_phone = models.CharField(
		_("Primary Contact Phone"),
		max_length=20,
		blank=True,
		help_text=_("Phone number of the primary contact person")
	)
	secondary_contact_name = models.CharField(
		_("Secondary Contact Name"),
		max_length=255,
		blank=True,
		help_text=_("Name of the secondary contact person")
	)
	secondary_contact_email = models.EmailField(
		_("Secondary Contact Email"),
		blank=True,
		help_text=_("Email of the secondary contact person")
	)
	secondary_contact_phone = models.CharField(
		_("Secondary Contact Phone"),
		max_length=20,
		blank=True,
		help_text=_("Phone number of the secondary contact person")
	)
	website = models.URLField(
		_("Website"),
		blank=True,
		help_text=_("Client's official website")
	)
	notes = models.TextField(
		_("Notes"),
		blank=True,
		help_text=_("Additional notes about the client")
	)
	
	# Standard fields
	created_at = models.DateTimeField(
		_("Created At"),
		auto_now_add=True,
		help_text=_("Date and time when the client was created")
	)
	updated_at = models.DateTimeField(
		_("Updated At"),
		auto_now=True,
		help_text=_("Date and time when the client was last updated")
	)
	created_by = models.ForeignKey(
		User,
		on_delete=models.SET_NULL,
		null=True,
		related_name="created_clients",
		verbose_name=_("Created By"),
		help_text=_("User who created this client")
	)
	
	class Meta:
		"""Meta options for Client model."""
		verbose_name = _("Client")
		verbose_name_plural = _("Clients")
		ordering = ["name", "-created_at"]
		indexes = [
			models.Index(fields=["name"]),
		]
	
	def __str__(self) -> str:
		"""Return string representation of Client."""
		return self.name
