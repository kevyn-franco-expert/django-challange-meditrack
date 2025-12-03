from django.conf import settings


class ClientTypeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        client_id = request.headers.get('X-Client-ID', '')
        
        if 'hospital' in client_id.lower() or 'legacy' in client_id.lower():
            request.client_type = settings.CLIENT_TYPES['LEGACY_HOSPITAL']
        elif 'mobile' in client_id.lower() or 'app' in client_id.lower():
            request.client_type = settings.CLIENT_TYPES['MOBILE_APP']
        else:
            request.client_type = settings.CLIENT_TYPES['MODERN_CLINIC']
        
        request.client_id = client_id
        
        response = self.get_response(request)
        return response