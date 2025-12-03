from rest_framework import permissions
from django.conf import settings


class RoleBasedPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        user_role = request.META.get('HTTP_X_USER_ROLE', 'doctor')
        department = request.META.get('HTTP_X_DEPARTMENT', None)
        client_type = getattr(request, 'client_type', '')
        
        if client_type == settings.CLIENT_TYPES['LEGACY_HOSPITAL']:
            if user_role == 'nurse':
                return view.action in ['list', 'retrieve']
            return True
        
        if client_type == settings.CLIENT_TYPES['MODERN_CLINIC']:
            if department:
                return self._check_department_access(obj, department)
            return True
        
        if client_type == settings.CLIENT_TYPES['MOBILE_APP']:
            consent_header = 'HTTP_X_PATIENT_CONSENT'
            patient_consent = request.META.get(consent_header, 'true')
            return patient_consent.lower() == 'true'
        
        return True

    def _check_department_access(self, obj, department):
        return True