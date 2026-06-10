"""
Internship serializers
"""
from rest_framework import serializers
from .models import Internship
from accounts.serializers import UserSerializer


class InternshipSerializer(serializers.ModelSerializer):
    posted_by = UserSerializer(read_only=True)
    is_open = serializers.SerializerMethodField()

    def get_is_open(self, obj):
        return obj.is_open

    class Meta:
        model = Internship
        fields = (
            'id', 'company_name', 'internship_role', 'description', 'min_cgpa', 'min_percentage',
            'eligible_batch_years', 'eligible_departments',
            'stipend', 'location', 'duration', 'ppo_conversion', 'deadline', 'is_active',
            'is_open', 'posted_by', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'posted_by', 'created_at', 'updated_at')
