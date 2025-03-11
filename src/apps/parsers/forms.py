from django import forms
from django.utils.translation import gettext_lazy as _
from .models import DeviceFile

class DeviceFileForm(forms.ModelForm):
	"""Form for creating and updating DeviceFile instances."""
	
	class Meta:
		model = DeviceFile
		fields = [
			'project',
			'device_type',
			'file',
			'name',
			'notes'
		]
		widgets = {
			'notes': forms.Textarea(attrs={'rows': 4}),
		}
	
	def __init__(self, *args, **kwargs):
		"""Initialize form and set up help text."""
		super().__init__(*args, **kwargs)
		
		# Add help text for file field
		self.fields['file'].help_text = _(
			'Upload a device configuration file. Supported formats depend on the device type.'
		)
		
		# Add help text for name field
		self.fields['name'].help_text = _(
			'A friendly name for this device configuration (e.g., "Core Router 1").'
		)
	
	def clean_file(self):
		"""Validate the uploaded file."""
		file = self.cleaned_data.get('file')
		if file:
			# Check file size (max 10MB)
			if file.size > 10 * 1024 * 1024:
				raise forms.ValidationError(_('File size cannot exceed 10MB.'))
			
			# Check file extension
			ext = file.name.split('.')[-1].lower()
			if ext not in ['txt', 'conf', 'cfg']:
				raise forms.ValidationError(_('Only .txt, .conf, and .cfg files are allowed.'))
		
		return file 