from rest_framework import serializers
from django.conf import settings
from .models import MedicalRecord


class MedicalRecordLegacySerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = ['id', 'patient', 'diagnosis', 'treatment',
                  'notes', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, data):
        required = ['patient', 'diagnosis', 'treatment']
        for field in required:
            if not data.get(field):
                raise serializers.ValidationError(
                    {field: 'This field is required'}
                )
        return data

    def create(self, validated_data):
        validated_data['record_type'] = 'general'
        return super().create(validated_data)


class MedicalRecordFlexibleSerializer(serializers.ModelSerializer):
    data = serializers.JSONField(source='flexible_data', required=False)

    class Meta:
        model = MedicalRecord
        fields = ['id', 'patient', 'record_type', 'diagnosis',
                  'treatment', 'notes', 'data', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, data):
        record_type = data.get('record_type', 'general')
        
        if record_type == 'lab_result':
            flexible_data = data.get('flexible_data', {})
            if not flexible_data.get('test_name'):
                raise serializers.ValidationError(
                    {'data': 'test_name is required for lab results'}
                )
        
        elif record_type == 'prescription':
            flexible_data = data.get('flexible_data', {})
            if not flexible_data.get('medication'):
                raise serializers.ValidationError(
                    {'data': 'medication is required for prescriptions'}
                )
        
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        if request and hasattr(request, 'client_type'):
            client_type = request.client_type
            
            if client_type == settings.CLIENT_TYPES['MODERN_CLINIC']:
                return instance.get_flexible_format()
        
        return super().to_representation(instance)


class MedicalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = '__all__'

    def __new__(cls, *args, **kwargs):
        context = kwargs.get('context', {})
        request = context.get('request')
        
        if request and hasattr(request, 'client_type'):
            client_type = request.client_type
            
            if client_type == settings.CLIENT_TYPES['LEGACY_HOSPITAL']:
                return MedicalRecordLegacySerializer(*args, **kwargs)
            elif client_type == settings.CLIENT_TYPES['MODERN_CLINIC']:
                return MedicalRecordFlexibleSerializer(*args, **kwargs)
        
        return super().__new__(cls)