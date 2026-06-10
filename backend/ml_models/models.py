"""
ML Models: ParsedResume and ShortlistingResult
"""
from django.db import models
from django.conf import settings
from students.models import Application


class ParsedResume(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='parsed_resume')
    raw_text = models.TextField()
    parsed_data = models.JSONField(default=dict)
    parse_confidence = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'parsed_resumes'
        ordering = ['-created_at']

    def __str__(self):
        return f"ParsedResume(app_id={self.application_id})"


class ShortlistingResult(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='shortlisting_result')
    overall_score = models.FloatField(default=0.0)
    is_shortlisted = models.BooleanField(default=False)
    cgpa_score = models.FloatField(default=0.0)
    skills_score = models.FloatField(default=0.0)
    experience_score = models.FloatField(default=0.0)
    projects_score = models.FloatField(default=0.0)
    semantic_score = models.FloatField(default=0.0)
    domain_alignment_score = models.FloatField(default=0.0)
    certification_score = models.FloatField(default=0.0)
    parser_confidence = models.FloatField(default=0.0)
    reason = models.CharField(max_length=255, blank=True)
    details = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'shortlisting_results'
        ordering = ['-created_at']

    def __str__(self):
        return f"ShortlistingResult(app_id={self.application_id}, score={self.overall_score})"


class FairnessAuditLog(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='fairness_audit_logs')
    evaluator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fairness_audit_logs'
    )
    overall_score = models.FloatField(default=0.0)
    recommended_status = models.CharField(max_length=20, blank=True)
    final_status = models.CharField(max_length=20, blank=True)
    protected_attributes = models.JSONField(default=dict)
    audit_payload = models.JSONField(default=dict)
    identifiers_sanitized = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fairness_audit_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"FairnessAuditLog(app_id={self.application_id}, status={self.final_status})"
