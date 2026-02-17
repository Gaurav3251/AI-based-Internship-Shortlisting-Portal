"""
Teacher profile model
"""
from django.db import models
from django.conf import settings


class TeacherProfile(models.Model):
    """Teacher/Admin profile"""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teacher_profile')
    full_name = models.CharField(max_length=200)
    role = models.CharField(max_length=100, default='Professor', help_text='e.g., Professor, HOD, Assistant Professor')
    department = models.CharField(max_length=100, default='CSE AIML')
    phone_number = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'teacher_profiles'
        verbose_name = 'Teacher Profile'
        verbose_name_plural = 'Teacher Profiles'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.role}"
