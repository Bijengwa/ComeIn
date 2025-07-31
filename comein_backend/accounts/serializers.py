from rest_framework import serializers
from .models import CustomUser

# Serializer used for registering users and validating passwords
class UserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)  # Only required at creation time

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'full_name', 'phone_number', 'password', 'confirm_password', 'is_active']
        extra_kwargs = {
            'password': {'write_only': True}  # Prevent password from being exposed in responses
        }

    # Custom validation to ensure password and confirm_password match
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    # Create method to hash password and remove confirm_password
    def create(self, validated_data):
        validated_data.pop('confirm_password')  # Not needed when saving to DB
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            phone_number=validated_data['phone_number'],
            password=validated_data['password']  # Automatically hashed by create_user
        )
        return user
