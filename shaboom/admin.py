from django.contrib.admin import AdminSite

class TenantAdminSite(AdminSite):
    site_header = 'Tenant Administration'
    site_title = 'Tenant Admin Portal'
    index_title = 'Tenant Admin'
    
tenant_admin_site = TenantAdminSite(name='tenant_admin')
