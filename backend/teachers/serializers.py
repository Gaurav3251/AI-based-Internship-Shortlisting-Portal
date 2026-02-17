"""
Teacher serializers
"""
from rest_framework import serializers
from .models import TeacherProfile


class TeacherProfileSerializer(serializers.ModelSerializer):
    """Teacher profile serializer"""
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = TeacherProfile
        fields = ('id', 'user', 'email', 'full_name', 'role', 'department', 'phone_number', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')
