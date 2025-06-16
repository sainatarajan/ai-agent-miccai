from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import Agent, Query, QueryResult, MCPTool
from .config_models import SystemConfiguration
from .admin_site import admin_site

# Re-register UserAdmin with our custom admin site
admin_site.register(User, UserAdmin)
admin_site.register(Group)

@admin.register(SystemConfiguration, site=admin_site)
class SystemConfigurationAdmin(admin.ModelAdmin):
    list_display = ('parameter_name_display', 'masked_value', 'description_short', 'last_modified')
    list_filter = ('parameter_name',)
    search_fields = ('parameter_name', 'description')
    readonly_fields = ('last_modified',)
    fieldsets = (
        (None, {
            'fields': ('parameter_name', 'parameter_value', 'description', 'last_modified'),
            'description': 'Configure system-wide parameters for the NCBI Multi-Agent System'
        }),
    )
    
    def parameter_name_display(self, obj):
        return obj.get_parameter_name_display()
    parameter_name_display.short_description = 'Parameter'
    
    def masked_value(self, obj):
        if obj.parameter_name == SystemConfiguration.NCBI_API_KEY and obj.parameter_value:
            return '********' + obj.parameter_value[-4:]
        return obj.parameter_value
    masked_value.short_description = 'Value'
    
    def description_short(self, obj):
        return format_html('<span title="{}">{}</span>', 
                         obj.description, 
                         obj.description[:50] + '...' if len(obj.description) > 50 else obj.description)
    description_short.short_description = 'Description'
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of configuration parameters
        return False
    
    def has_add_permission(self, request):
        # Only allow adding if parameter doesn't exist
        existing_params = set(SystemConfiguration.objects.values_list('parameter_name', flat=True))
        all_params = set(dict(SystemConfiguration.PARAMETER_CHOICES).keys())
        return bool(all_params - existing_params)

@admin.register(Agent, site=admin_site)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('name', 'agent_type', 'status', 'last_heartbeat')
    list_filter = ('agent_type', 'status')
    search_fields = ('name',)

@admin.register(Query, site=admin_site)
class QueryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'query_type', 'status', 'timestamp', 'execution_time')
    list_filter = ('status', 'query_type')
    search_fields = ('query_text', 'user__username')
    date_hierarchy = 'timestamp'

@admin.register(QueryResult, site=admin_site)
class QueryResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'query', 'source_database', 'agent', 'relevance_score')
    list_filter = ('source_database', 'agent')
    search_fields = ('query__query_text',)

@admin.register(MCPTool, site=admin_site)
class MCPToolAdmin(admin.ModelAdmin):
    list_display = ('name', 'agent', 'status', 'execution_count', 'average_execution_time')
    list_filter = ('status', 'agent')
    search_fields = ('name', 'description')
