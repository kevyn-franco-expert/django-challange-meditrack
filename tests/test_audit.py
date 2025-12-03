from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from apps.patients.models import Patient
from apps.audit.models import AuditLog


class AuditLoggingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='premiumuser',
            password='test123'
        )
        self.client.force_authenticate(user=self.user)

    def test_premium_client_creates_audit_log(self):
        initial_count = AuditLog.objects.count()
        
        response = self.client.post(
            '/api/patients/',
            {'email': 'audit@test.com'},
            HTTP_X_CLIENT_ID='premium_clinic_1'
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(AuditLog.objects.count(), initial_count + 1)
        
        log = AuditLog.objects.latest('timestamp')
        self.assertEqual(log.action, 'create')
        self.assertEqual(log.resource_type, 'patients')
        self.assertEqual(log.client_id, 'premium_clinic_1')

    def test_non_premium_client_no_audit_log(self):
        initial_count = AuditLog.objects.count()
        
        response = self.client.post(
            '/api/patients/',
            {'email': 'noaudit@test.com'},
            HTTP_X_CLIENT_ID='regular_clinic_1'
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(AuditLog.objects.count(), initial_count)

    def test_audit_log_captures_read_action(self):
        patient = Patient.objects.create(email='read@test.com')
        initial_count = AuditLog.objects.count()
        
        response = self.client.get(
            f'/api/patients/{patient.id}/',
            HTTP_X_CLIENT_ID='premium_clinic_1'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(AuditLog.objects.count(), initial_count + 1)
        
        log = AuditLog.objects.latest('timestamp')
        self.assertEqual(log.action, 'read')
        self.assertEqual(log.resource_id, patient.id)