"""
ML serializers
"""
from rest_framework import serializers
from .models import ParsedResume, ShortlistingResult


class ParsedResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParsedResume
        fields = ('id', 'application', 'raw_text', 'parsed_data', 'created_at')
        read_only_fields = ('id', 'created_at')


class ShortlistingResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShortlistingResult
        fields = (
            'id', 'application', 'overall_score', 'is_shortlisted', 'cgpa_score', 'skills_score',
            'experience_score', 'projects_score', 'semantic_score', 'reason', 'details', 'created_at'
        )
        read_only_fields = ('id', 'created_at')
