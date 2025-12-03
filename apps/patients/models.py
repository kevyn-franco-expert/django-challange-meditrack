from django.db import models


class Patient(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    
    ssn_legacy = models.CharField(max_length=20, blank=True, db_column='ssn')
    ssn_number = models.CharField(max_length=20, blank=True)
    ssn_verified = models.BooleanField(default=False)
    ssn_verification_date = models.DateField(null=True, blank=True)
    
    blood_type = models.CharField(max_length=5, blank=True)
    allergies = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    emergency_phone = models.CharField(max_length=20, blank=True)
    insurance_provider = models.CharField(max_length=100, blank=True)
    insurance_number = models.CharField(max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'patients'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['ssn_legacy']),
            models.Index(fields=['ssn_number']),
        ]

    def get_ssn_v1(self):
        return self.ssn_legacy or self.ssn_number

    def get_ssn_v2(self):
        if self.ssn_number:
            return {
                'number': self.ssn_number,
                'verified': self.ssn_verified,
                'verification_date': (
                    self.ssn_verification_date.isoformat()
                    if self.ssn_verification_date else None
                )
            }
        elif self.ssn_legacy:
            return {
                'number': self.ssn_legacy,
                'verified': False,
                'verification_date': None
            }
        return None

    def set_ssn_from_string(self, ssn_value):
        if self.ssn_number:
            return
        self.ssn_legacy = ssn_value

    def set_ssn_from_object(self, ssn_data):
        self.ssn_number = ssn_data.get('number', '')
        self.ssn_verified = ssn_data.get('verified', False)
        verification_date = ssn_data.get('verification_date')
        if verification_date:
            from dateutil import parser
            self.ssn_verification_date = parser.parse(verification_date).date()