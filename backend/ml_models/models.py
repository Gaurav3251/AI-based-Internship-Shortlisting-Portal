"""
ML Models: ParsedResume and ShortlistingResult
"""
from django.db import models
from students.models import Application


class ParsedResume(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='parsed_resume')
    raw_text = models.TextField()
    parsed_data = models.JSONField(default=dict)
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
    reason = models.CharField(max_length=255, blank=True)
    details = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'shortlisting_results'
        ordering = ['-created_at']

    def __str__(self):
        return f"ShortlistingResult(app_id={self.application_id}, score={self.overall_score})"
