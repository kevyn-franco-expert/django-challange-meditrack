from django.conf import settings
from apps.core.models import ClientConfiguration
from .models import AuditLog


class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        client_id = getattr(request, 'client_id', '')
        client_type = getattr(request, 'client_type', '')
        
        if self._should_audit(client_id, client_type):
            self._log_request(request, response)
        
        return response

    def _should_audit(self, client_id, client_type):
        if client_id in settings.AUDIT_ENABLED_CLIENTS:
            return True
        
        config = ClientConfiguration.get_config(client_id, client_type)
        return config.get('audit_enabled', False)

    def _log_request(self, request, response):
        if request.method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
            action_map = {
                'GET': 'read',
                'POST': 'create',
                'PUT': 'update',
                'PATCH': 'update',
                'DELETE': 'delete',
            }
            
            try:
                user = request.user if request.user.is_authenticated else None
                AuditLog.objects.create(
                    user=user,
                    action=action_map.get(request.method, 'read'),
                    resource_type=self._extract_resource_type(request.path),
                    resource_id=self._extract_resource_id(request.path),
                    client_id=getattr(request, 'client_id', ''),
                    ip_address=self._get_client_ip(request),
                    metadata={
                        'path': request.path,
                        'method': request.method,
                        'status_code': response.status_code,
                    }
                )
            except Exception:
                pass

    def _extract_resource_type(self, path):
        parts = path.strip('/').split('/')
        if len(parts) >= 2:
            return parts[1]
        return 'unknown'

    def _extract_resource_id(self, path):
        parts = path.strip('/').split('/')
        for part in parts:
            if part.isdigit():
                return int(part)
        return 0

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')