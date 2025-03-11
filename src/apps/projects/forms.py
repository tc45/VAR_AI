from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Project

class ProjectForm(forms.ModelForm):
	"""Form for creating and updating Project instances."""
	
	class Meta:
		model = Project
		fields = [
			'client',
			'name',
			'intent',
			'status',
			'start_date',
			'end_date',
			'is_split_off',
			'parent_project',
			'notes'
		]
		widgets = {
			'start_date': forms.DateInput(attrs={'type': 'date'}),
			'end_date': forms.DateInput(attrs={'type': 'date'}),
			'intent': forms.Textarea(attrs={'rows': 4}),
			'notes': forms.Textarea(attrs={'rows': 4}),
		}
	
	def __init__(self, *args, **kwargs):
		"""Initialize form and set up parent project choices."""
		super().__init__(*args, **kwargs)
		instance = kwargs.get('instance')
		
		# Filter parent project choices to exclude self and child projects
		if instance:
			self.fields['parent_project'].queryset = Project.objects.exclude(
				pk__in=[instance.pk] + list(instance.child_projects.values_list('pk', flat=True))
			)
		
		# Make parent_project field optional
		self.fields['parent_project'].required = False
		
		# Add help text for intent field
		self.fields['intent'].help_text = _(
			'Describe the project goals and requirements. This will be used for AI-assisted reporting.'
		)
	
	def clean(self):
		"""Validate form data."""
		cleaned_data = super().clean()
		start_date = cleaned_data.get('start_date')
		end_date = cleaned_data.get('end_date')
		is_split_off = cleaned_data.get('is_split_off')
		parent_project = cleaned_data.get('parent_project')
		
		# Validate date range
		if start_date and end_date and end_date < start_date:
			raise forms.ValidationError({
				'end_date': _('End date cannot be earlier than start date.')
			})
		
		# Validate parent project selection
		if is_split_off and not parent_project:
			raise forms.ValidationError({
				'parent_project': _('Parent project is required for split-off projects.')
			})
		elif not is_split_off and parent_project:
			raise forms.ValidationError({
				'is_split_off': _('Project must be marked as split-off to have a parent project.')
			})
		
		return cleaned_data 