from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re

CustomUser = get_user_model()

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
        trim_whitespace=False
    )
    phone = serializers.CharField(
        max_length=17,
        trim_whitespace=True
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'first_name', 'last_name', 'phone', 'username']
        extra_kwargs = {
            'email': {'required': True, 'allow_blank': False},
            'first_name': {'required': True, 'allow_blank': False},
            'last_name': {'required': True, 'allow_blank': False},
            'username': {'required': True, 'allow_blank': False},
            'phone': {'required': True, 'allow_blank': False}
        }

    def validate_email(self, value):
        value = value.lower().strip()
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Enter a valid email address.")
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_phone(self, value):
        value = value.strip()
        if not re.match(r'^\+?[1-9]\d{9,14}$', value):
            raise serializers.ValidationError(
                "Enter a valid phone number (e.g. +1234567890). 10-15 digits allowed."
            )
        if CustomUser.objects.filter(phone=value).exists():
            raise serializers.ValidationError("This phone number is already in use.")
        return value

    def validate_username(self, value):
        value = value.strip()
        if len(value) < 4:
            raise serializers.ValidationError("Username must be at least 4 characters long.")
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError(
                "Username can only contain letters, numbers and underscores."
            )
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def create(self, validated_data):
        try:
            user = CustomUser.objects.create_user(
                email=validated_data['email'],
                password=validated_data['password'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                phone=validated_data['phone'],
                username=validated_data['username'],
                is_active=False  # Assuming you'll activate via email
            )
            return user
        except Exception as e:
            raise serializers.ValidationError(str(e))
