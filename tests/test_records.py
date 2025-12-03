from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from apps.patients.models import Patient
from apps.records.models import MedicalRecord


class LegacyHospitalRecordTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='doctor',
            password='test123'
        )
        self.client.force_authenticate(user=self.user)
        self.patient = Patient.objects.create(
            email='patient@hospital.com',
            first_name='John',
            last_name='Doe'
        )

    def test_create_record_requires_rigid_structure(self):
        data = {
            'patient': self.patient.id,
            'diagnosis': 'Common Cold',
            'treatment': 'Rest and fluids'
        }
        response = self.client.post(
            '/api/records/',
            data,
            HTTP_X_CLIENT_ID='legacy_hospital_1'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['diagnosis'], 'Common Cold')

    def test_create_record_missing_required_fields(self):
        data = {
            'patient': self.patient.id,
            'diagnosis': 'Flu'
        }
        response = self.client.post(
            '/api/records/',
            data,
            HTTP_X_CLIENT_ID='legacy_hospital_1'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_record_legacy_format(self):
        record = MedicalRecord.objects.create(
            patient=self.patient,
            diagnosis='Hypertension',
            treatment='Medication',
            notes='Monitor blood pressure'
        )
        response = self.client.get(
            f'/api/records/{record.id}/',
            HTTP_X_CLIENT_ID='legacy_hospital_1'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('diagnosis', response.data)
        self.assertIn('treatment', response.data)


class ModernClinicRecordTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='clinicuser',
            password='test123'
        )
        self.client.force_authenticate(user=self.user)
        self.patient = Patient.objects.create(
            email='patient@clinic.com'
        )

    def test_create_lab_result_with_flexible_schema(self):
        data = {
            'patient': self.patient.id,
            'record_type': 'lab_result',
            'data': {
                'test_name': 'Blood Test',
                'results': {
                    'hemoglobin': '14.5 g/dL',
                    'white_blood_cells': '7000/μL'
                },
                'lab_technician': 'Jane Smith'
            }
        }
        response = self.client.post(
            '/api/records/',
            data,
            format='json',
            HTTP_X_CLIENT_ID='modern_clinic_1'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_prescription_with_flexible_schema(self):
        data = {
            'patient': self.patient.id,
            'record_type': 'prescription',
            'data': {
                'medication': 'Amoxicillin',
                'dosage': '500mg',
                'frequency': 'Three times daily',
                'duration': '7 days'
            }
        }
        response = self.client.post(
            '/api/records/',
            data,
            format='json',
            HTTP_X_CLIENT_ID='modern_clinic_1'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_note_with_flexible_schema(self):
        data = {
            'patient': self.patient.id,
            'record_type': 'note',
            'data': {
                'content': 'Patient reports feeling better',
                'author': 'Dr. Smith',
                'tags': ['follow-up', 'improvement']
            }
        }
        response = self.client.post(
            '/api/records/',
            data,
            format='json',
            HTTP_X_CLIENT_ID='modern_clinic_1'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_lab_result_requires_test_name(self):
        data = {
            'patient': self.patient.id,
            'record_type': 'lab_result',
            'data': {
                'results': {'value': '100'}
            }
        }
        response = self.client.post(
            '/api/records/',
            data,
            format='json',
            HTTP_X_CLIENT_ID='modern_clinic_1'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RecordBackwardCompatibilityTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='test123'
        )
        self.client.force_authenticate(user=self.user)
        self.patient = Patient.objects.create(
            email='test@example.com'
        )

    def test_legacy_client_cannot_see_flexible_data(self):
        record = MedicalRecord.objects.create(
            patient=self.patient,
            record_type='lab_result',
            diagnosis='Test',
            treatment='Test',
            flexible_data={'test_name': 'Blood Test', 'value': '100'}
        )
        response = self.client.get(
            f'/api/records/{record.id}/',
            HTTP_X_CLIENT_ID='legacy_hospital_1'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('flexible_data', response.data)
        self.assertNotIn('data', response.data)

    def test_modern_client_can_see_legacy_records(self):
        record = MedicalRecord.objects.create(
            patient=self.patient,
            diagnosis='Diabetes',
            treatment='Insulin',
            notes='Regular monitoring required'
        )
        response = self.client.get(
            f'/api/records/{record.id}/',
            HTTP_X_CLIENT_ID='modern_clinic_1'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)