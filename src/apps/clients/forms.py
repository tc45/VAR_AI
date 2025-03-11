from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Client

class ClientForm(forms.ModelForm):
	"""Form for creating and updating Client instances."""
	
	class Meta:
		model = Client
		fields = [
			'name',
			'industry',
			'primary_contact_name',
			'primary_contact_email',
			'primary_contact_phone',
			'secondary_contact_name',
			'secondary_contact_email',
			'secondary_contact_phone',
			'website',
			'notes'
		]
		widgets = {
			'notes': forms.Textarea(attrs={'rows': 4}),
		}
	
	def clean_primary_contact_email(self):
		"""Validate primary contact email."""
		email = self.cleaned_data.get('primary_contact_email')
		if email and Client.objects.filter(primary_contact_email=email).exclude(pk=self.instance.pk).exists():
			raise forms.ValidationError(_('This email is already registered with another client.'))
		return email 