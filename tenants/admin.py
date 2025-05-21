from django.contrib import admin
from django_tenants.admin import TenantAdminMixin
from .models import Client, Domain

@admin.register(Client)
class ClientAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'business_name', 'schema_name', 'paid_until', 'on_trial')
    list_filter = ('on_trial', 'created_on')
    search_fields = ('name', 'business_name', 'schema_name')
    ordering = ('name',)

@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('domain', 'tenant', 'is_primary')
    list_filter = ('is_primary',)
    search_fields = ('domain', 'tenant__name')
    raw_id_fields = ('tenant',)
