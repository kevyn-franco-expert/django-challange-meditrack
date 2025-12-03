from django.db import models
from django.core.cache import cache


class ClientConfiguration(models.Model):
    client_id = models.CharField(max_length=100, unique=True)
    client_type = models.CharField(max_length=50)
    config = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'client_configurations'
        ordering = ['client_id']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(f'client_config_{self.client_id}')

    @classmethod
    def get_config(cls, client_id, client_type):
        cache_key = f'client_config_{client_id}'
        config = cache.get(cache_key)
        
        if config is None:
            try:
                client_config = cls.objects.get(
                    client_id=client_id,
                    is_active=True
                )
                config = client_config.config
            except cls.DoesNotExist:
                config = cls._get_default_config(client_type)
            
            cache.set(cache_key, config, 3600)
        
        return config

    @staticmethod
    def _get_default_config(client_type):
        from django.conf import settings
        return settings.CLIENT_FIELD_CONFIGS.get(
            client_type,
            settings.CLIENT_FIELD_CONFIGS.get('modern_clinic', {
                'required_fields': ['email'],
                'audit_enabled': False,
                'rate_limit': 5000,
                'allow_field_selection': True,
            })
        )