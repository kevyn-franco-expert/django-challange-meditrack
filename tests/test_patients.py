from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.patients.models import Patient


class LegacyHospitalPatientTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_patient_requires_all_fields(self):
        response = self.client.post(
            '/api/patients/',
            {'email': 'test@example.com'},
            HTTP_X_CLIENT_ID='legacy_hospital_1',
            HTTP_ACCEPT='application/json; version=v1'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_patient_with_all_fields(self):
        data = {
            'email': 'patient@hospital.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'date_of_birth': '1980-01-01',
            'phone': '555-0100',
            'ssn': '123-45-6789'
        }
        response = self.client.post(
            '/api/patients/',
            data,
            HTTP_X_CLIENT_ID='legacy_hospital_1',
            HTTP_ACCEPT='application/json; version=v1'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['ssn'], '123-45-6789')

    def test_get_patient_returns_all_fields(self):
        patient = Patient.objects.create(
            email='test@hospital.com',
            first_name='Jane',
            last_name='Smith',
            ssn_legacy='987-65-4321'
        )
        response = self.client.get(
            f'/api/patients/{patient.id}/',
            HTTP_X_CLIENT_ID='legacy_hospital_1',
            HTTP_ACCEPT='application/json; version=v1'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('ssn', response.data)
        self.assertEqual(response.data['ssn'], '987-65-4321')


class ModernClinicPatientTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_patient_with_email_only(self):
        response = self.client.post(
            '/api/patients/',
            {'email': 'patient@clinic.com'},
            HTTP_X_CLIENT_ID='modern_clinic_1',
            HTTP_ACCEPT='application/json; version=v1'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], 'patient@clinic.com')

    def test_create_patient_with_new_ssn_format(self):
        data = {
            'email': 'patient2@clinic.com',
            'ssn': {
                'number': '111-22-3333',
                'verified': True,
                'verification_date': '2024-01-15'
            }
        }
        response = self.client.post(
            '/api/patients/',
            data,
            format='json',
            HTTP_X_CLIENT_ID='modern_clinic_1',
            HTTP_ACCEPT='application/json; version=v2'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_patient_with_new_ssn_format(self):
        patient = Patient.objects.create(
            email='test@clinic.com',
            ssn_number='444-55-6666',
            ssn_verified=True
        )
        response = self.client.get(
            f'/api/patients/{patient.id}/',
            HTTP_X_CLIENT_ID='modern_clinic_1',
            HTTP_ACCEPT='application/json; version=v2'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data['ssn'], dict)
        self.assertEqual(response.data['ssn']['number'], '444-55-6666')
        self.assertTrue(response.data['ssn']['verified'])


class MobileAppPatientTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_patient_with_field_selection(self):
        patient = Patient.objects.create(
            email='mobile@example.com',
            first_name='Mobile',
            last_name='User',
            phone='555-0200',
            address='123 Main St',
            blood_type='O+',
            allergies='None'
        )
        url = (
            f'/api/patients/{patient.id}/'
            '?fields=id,email,first_name,last_name,phone'
        )
        response = self.client.get(
            url,
            HTTP_X_CLIENT_ID='mobile_app_1',
            HTTP_ACCEPT='application/json; version=v1'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('email', response.data)
        self.assertIn('first_name', response.data)
        self.assertNotIn('address', response.data)
        self.assertNotIn('blood_type', response.data)

    def test_create_patient_progressive_data(self):
        response = self.client.post(
            '/api/patients/',
            {'email': 'progressive@mobile.com'},
            HTTP_X_CLIENT_ID='mobile_app_1',
            HTTP_ACCEPT='application/json; version=v1'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class BackwardCompatibilityTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_legacy_client_still_works_with_old_ssn(self):
        patient = Patient.objects.create(
            email='legacy@test.com',
            first_name='Legacy',
            last_name='Patient',
            ssn_legacy='555-66-7777'
        )
        response = self.client.get(
            f'/api/patients/{patient.id}/',
            HTTP_X_CLIENT_ID='legacy_hospital_1',
            HTTP_ACCEPT='application/json; version=v1'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ssn'], '555-66-7777')

    def test_new_client_can_read_legacy_ssn(self):
        patient = Patient.objects.create(
            email='transition@test.com',
            ssn_legacy='888-99-0000'
        )
        response = self.client.get(
            f'/api/patients/{patient.id}/',
            HTTP_X_CLIENT_ID='modern_clinic_1',
            HTTP_ACCEPT='application/json; version=v2'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data['ssn'], dict)
        self.assertEqual(response.data['ssn']['number'], '888-99-0000')
        self.assertFalse(response.data['ssn']['verified'])