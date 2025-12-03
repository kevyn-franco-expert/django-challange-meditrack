from django.db import models
from apps.patients.models import Patient


class MedicalRecord(models.Model):
    RECORD_TYPES = [
        ('general', 'General'),
        ('lab_result', 'Lab Result'),
        ('prescription', 'Prescription'),
        ('note', 'Note'),
    ]

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='records'
    )
    record_type = models.CharField(
        max_length=20,
        choices=RECORD_TYPES,
        default='general'
    )
    
    diagnosis = models.TextField(blank=True)
    treatment = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    flexible_data = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'medical_records'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient', 'record_type']),
            models.Index(fields=['created_at']),
        ]

    def get_legacy_format(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'diagnosis': self.diagnosis,
            'treatment': self.treatment,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
        }

    def get_flexible_format(self):
        base = {
            'id': self.id,
            'patient_id': self.patient_id,
            'record_type': self.record_type,
            'created_at': self.created_at.isoformat(),
        }
        
        if self.record_type == 'general':
            base.update({
                'diagnosis': self.diagnosis,
                'treatment': self.treatment,
                'notes': self.notes,
            })
        
        base.update(self.flexible_data)
        return base