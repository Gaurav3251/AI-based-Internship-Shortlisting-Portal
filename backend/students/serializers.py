"""
Student serializers for API
"""
from rest_framework import serializers
from django.utils import timezone
from .models import StudentProfile, Application
from internships.serializers import InternshipSerializer
from ml_models.serializers import ShortlistingResultSerializer


class StudentProfileSerializer(serializers.ModelSerializer):
    """Student profile serializer"""
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = StudentProfile
        fields = (
            'id', 'user', 'email', 'prn_number', 'full_name', 'gender',
            'date_of_birth', 'phone_number', 'personal_email', 'batch_year', 'cgpa', 'percentage',
            'profile_picture', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')


class ApplicationSerializer(serializers.ModelSerializer):
    """Application serializer"""
    internship_details = InternshipSerializer(source='internship', read_only=True)
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    shortlisting_result = ShortlistingResultSerializer(read_only=True)

    class Meta:
        model = Application
        fields = (
            'id', 'student', 'student_name', 'internship', 'internship_details',
            'personal_email', 'submitted_cgpa', 'submitted_percentage', 'resume',
            'status', 'applied_at', 'updated_at', 'shortlisting_result'
        )
        read_only_fields = ('id', 'student', 'status', 'applied_at', 'updated_at')

    def validate_resume(self, value):
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError('Resume file size should not exceed 5MB')
        return value


class ApplicationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating applications"""

    class Meta:
        model = Application
        fields = ('internship', 'personal_email', 'submitted_cgpa', 'submitted_percentage', 'resume')
        extra_kwargs = {
            'personal_email': {'required': False, 'allow_blank': True},
            'submitted_cgpa': {'required': False},
            'submitted_percentage': {'required': False},
        }

    def validate(self, attrs):
        student = self.context['request'].user.student_profile
        internship = attrs['internship']

        if Application.objects.filter(student=student, internship=internship).exists():
            raise serializers.ValidationError('You have already applied for this internship')

        if not internship.is_active:
            raise serializers.ValidationError('This internship is no longer active.')

        if internship.deadline < timezone.localdate():
            raise serializers.ValidationError('The deadline for this internship has passed.')

        # Internship-specific batch year constraints.
        eligible_batch_years = internship.eligible_batch_years or []
        if eligible_batch_years and student.batch_year not in eligible_batch_years:
            raise serializers.ValidationError('Your batch year is not eligible for this internship.')

        attrs.setdefault('personal_email', student.personal_email or student.user.email)
        attrs.setdefault('submitted_cgpa', student.cgpa)
        attrs.setdefault('submitted_percentage', student.percentage)

        if not attrs.get('personal_email'):
            raise serializers.ValidationError('Personal email is required. Please update your profile.')

        return attrs

    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user.student_profile
        validated_data['status'] = 'under_review'
        return super().create(validated_data)
