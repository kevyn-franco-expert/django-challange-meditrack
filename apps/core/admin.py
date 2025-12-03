from django.contrib import admin
from .models import ClientConfiguration


@admin.register(ClientConfiguration)
class ClientConfigurationAdmin(admin.ModelAdmin):
    list_display = [
        'client_id',
        'client_type',
        'is_active',
        'updated_at'
    ]
    list_filter = ['client_type', 'is_active']
    search_fields = ['client_id']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('client_id', 'client_type', 'is_active')
        }),
        ('Configuration', {
            'fields': ('config',),
            'description': 'JSON configuration for this client'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )