from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.urls import reverse


class StudioAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to ensure user is a studio owner and has an associated studio profile."""
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_studio_owner
    
    def dispatch(self, request, *args, **kwargs):
        # First, ensure user is authenticated and passes the test_func
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if not self.test_func():
            return self.handle_no_permission()
        
        # Check if user has a studio profile
        if not hasattr(request.user, 'studio_profile') or request.user.studio_profile is None:
            # Redirect to profile setup with a message
            return redirect(reverse('studio_profile_setup'))
            
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # At this point, we're sure studio profile exists due to dispatch check
        context['studio'] = self.request.user.studio_profile
        return context


class StudioDashboardView(StudioAccessMixin, TemplateView):
    """Main dashboard view for studio owners."""
    template_name = 'studio/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'dashboard'
        return context
