from django.contrib import admin
from .models import StudioProfile, StudioMembership


@admin.register(StudioProfile)
class StudioProfileAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'website', 'created_at', 'updated_at')
    search_fields = ('owner__email', 'owner__first_name', 'owner__last_name', 'website')
    list_filter = ('created_at', 'updated_at')
    raw_id_fields = ('owner',)
    readonly_fields = ('created_at', 'updated_at', 'public_id')


@admin.register(StudioMembership)
class StudioMembershipAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'status', 'joined_at', 'updated_at')
    list_filter = ('status', 'joined_at', 'updated_at')
    search_fields = ('member__email', 'studio__owner__email')
    raw_id_fields = ('member', 'studio')
    readonly_fields = ('joined_at', 'updated_at')
