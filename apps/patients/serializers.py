from rest_framework import serializers
from django.conf import settings
from apps.core.models import ClientConfiguration
from .models import Patient


class PatientSerializerV1(serializers.ModelSerializer):
    ssn = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = '__all__'

    def get_ssn(self, obj):
        return obj.get_ssn_v1()

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        
        if request and hasattr(request, 'client_type'):
            client_type = request.client_type
            
            if client_type == settings.CLIENT_TYPES['MOBILE_APP']:
                requested_fields = request.query_params.get('fields')
                if requested_fields:
                    allowed = set(requested_fields.split(','))
                    existing = set(fields.keys())
                    for field_name in existing - allowed:
                        fields.pop(field_name)
            
            elif client_type == settings.CLIENT_TYPES['LEGACY_HOSPITAL']:
                for field in ['ssn_number', 'ssn_verified',
                              'ssn_verification_date']:
                    fields.pop(field, None)
        
        return fields

    def validate(self, data):
        request = self.context.get('request')
        
        if request and hasattr(request, 'client_type'):
            if request.method == 'POST':
                client_id = getattr(request, 'client_id', '')
                client_type = request.client_type
                
                config = ClientConfiguration.get_config(client_id, client_type)
                required_fields = config.get('required_fields', [])
                
                for field in required_fields:
                    if not data.get(field):
                        msg = f'This field is required for {client_type}'
                        raise serializers.ValidationError({field: msg})
        
        return data

    def create(self, validated_data):
        ssn_value = validated_data.pop('ssn', None)
        patient = Patient.objects.create(**validated_data)
        
        if ssn_value:
            if isinstance(ssn_value, str):
                patient.set_ssn_from_string(ssn_value)
            elif isinstance(ssn_value, dict):
                patient.set_ssn_from_object(ssn_value)
            patient.save()
        
        return patient


class PatientSerializerV2(serializers.ModelSerializer):
    ssn = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = '__all__'

    def get_ssn(self, obj):
        return obj.get_ssn_v2()

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        
        if request and hasattr(request, 'client_type'):
            client_type = request.client_type
            
            if client_type == settings.CLIENT_TYPES['MOBILE_APP']:
                requested_fields = request.query_params.get('fields')
                if requested_fields:
                    allowed = set(requested_fields.split(','))
                    existing = set(fields.keys())
                    for field_name in existing - allowed:
                        fields.pop(field_name)
        
        for field in ['ssn_legacy', 'ssn_number', 'ssn_verified',
                      'ssn_verification_date']:
            fields.pop(field, None)
        
        return fields

    def validate(self, data):
        request = self.context.get('request')
        
        if request and hasattr(request, 'client_type'):
            if request.method == 'POST':
                client_id = getattr(request, 'client_id', '')
                client_type = request.client_type
                
                config = ClientConfiguration.get_config(client_id, client_type)
                required_fields = config.get('required_fields', [])
                
                for field in required_fields:
                    if not data.get(field):
                        msg = f'This field is required for {client_type}'
                        raise serializers.ValidationError({field: msg})
        
        return data

    def create(self, validated_data):
        ssn_value = validated_data.pop('ssn', None)
        patient = Patient.objects.create(**validated_data)
        
        if ssn_value:
            if isinstance(ssn_value, dict):
                patient.set_ssn_from_object(ssn_value)
            elif isinstance(ssn_value, str):
                patient.set_ssn_from_string(ssn_value)
            patient.save()
        
        return patient