from django.shortcuts import render
from django.views.generic import TemplateView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.urls import reverse_lazy
from .models import Report

# Create your views here.

class ReportIndexView(LoginRequiredMixin, TemplateView):
    """Landing page for the reports app."""
    
    template_name = 'reports/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get reports statistics
        context['total_reports'] = Report.objects.count()
        context['reports_by_status'] = (
            Report.objects.values('status')
            .annotate(count=Count('id'))
            .order_by('status')
        )
        
        # Get recent reports
        context['recent_reports'] = (
            Report.objects.select_related('project', 'created_by')
            .order_by('-created_at')[:5]
        )
        
        return context

class ReportCreateView(LoginRequiredMixin, CreateView):
    """Create a new report."""
    model = Report
    template_name = 'reports/report_form.html'
    fields = ['project', 'title', 'content']
    success_url = reverse_lazy('reports:index')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class ReportDetailView(LoginRequiredMixin, DetailView):
    """Display report details."""
    model = Report
    template_name = 'reports/report_detail.html'
    context_object_name = 'report'
