from django.urls import path
from .views.base import StudioDashboardView

app_name = 'studio'

urlpatterns = [
    path('', StudioDashboardView.as_view(), name='dashboard'),
    # Add more studio-specific URLs here
]
