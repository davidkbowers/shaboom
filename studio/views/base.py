from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView


class StudioAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to ensure user is a studio owner and has an associated studio profile."""
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_studio_owner
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Make sure studio is always set in the context, even if it's None
        # This prevents template errors when trying to access studio attributes
        context['studio'] = None
        
        # Set the studio profile if it exists
        if hasattr(self.request.user, 'studio_profile') and self.request.user.studio_profile is not None:
            context['studio'] = self.request.user.studio_profile
        return context


class StudioDashboardView(StudioAccessMixin, TemplateView):
    """Main dashboard view for studio owners."""
    template_name = 'studio/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'dashboard'
        return context
