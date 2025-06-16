from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _

class NCBIAdminSite(AdminSite):
    site_title = _('NCBI Agent Admin')
    site_header = _('NCBI Multi-Agent Research System Administration')
    index_title = _('System Administration')

# Create the admin site instance
admin_site = NCBIAdminSite(name='ncbi_admin')

# Make sure to export the admin_site
__all__ = ['admin_site']
