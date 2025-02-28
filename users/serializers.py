from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import CustomUser

# User Data Serializer (For returning user info)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'email', 'organization_name', 'organization_type', 'role', 'created_at']

# Registration Serializer (For Signup)
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['name', 'email', 'password', 'organization_name', 'organization_type', 'role']

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])  # Hash password before saving
        return super().create(validated_data)

# Login Serializer (For Login)
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

