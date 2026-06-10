"""
Internship opportunities models
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


def default_eligible_departments():
    return ['CSE AIML']


class Internship(models.Model):
    """Internship opportunity"""

    company_name = models.CharField(max_length=200)
    internship_role = models.CharField(max_length=200)
    description = models.TextField()
    min_cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
    min_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    eligible_batch_years = models.JSONField(
        default=list,
        blank=True,
        help_text='List of allowed graduation years. Empty means no year restriction.'
    )
    eligible_departments = models.JSONField(
        default=default_eligible_departments,
        blank=True,
        help_text='List of allowed departments. Defaults to CSE AIML.'
    )
    stipend = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True)
    duration = models.CharField(max_length=100, blank=True)
    ppo_conversion = models.BooleanField(default=False)
    deadline = models.DateField()
    is_active = models.BooleanField(default=True)
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posted_internships')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'internships'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.company_name} - {self.internship_role}"

    @property
    def is_open(self):
        return self.is_active and self.deadline >= timezone.localdate()
