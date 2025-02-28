from rest_framework import serializers
from .models import Request

class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = '__all__'  # Includes all model fields
        read_only_fields = ['request_id', 'status', 'created_at', 'updated_at']  # Prevent these from being edited
