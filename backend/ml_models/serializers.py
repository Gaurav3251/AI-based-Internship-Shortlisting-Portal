"""
ML serializers
"""
from rest_framework import serializers
from .models import ParsedResume, ShortlistingResult, FairnessAuditLog


class ParsedResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParsedResume
        fields = ('id', 'application', 'raw_text', 'parsed_data', 'parse_confidence', 'created_at')
        read_only_fields = ('id', 'created_at')


class ShortlistingResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShortlistingResult
        fields = (
            'id', 'application', 'overall_score', 'is_shortlisted', 'cgpa_score', 'skills_score',
            'experience_score', 'projects_score', 'semantic_score', 'domain_alignment_score',
            'certification_score', 'parser_confidence', 'reason', 'details', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class FairnessAuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = FairnessAuditLog
        fields = (
            'id', 'application', 'evaluator', 'overall_score', 'recommended_status', 'final_status',
            'protected_attributes', 'audit_payload', 'identifiers_sanitized', 'created_at'
        )
        read_only_fields = ('id', 'created_at')
