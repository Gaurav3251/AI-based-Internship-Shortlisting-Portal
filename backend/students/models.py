"""
Student profile and application models
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from internships.models import Internship


class StudentProfile(models.Model):
    """Student profile with academic and personal information"""

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    prn_number = models.CharField(max_length=20, unique=True, verbose_name='PRN Number')
    full_name = models.CharField(max_length=200)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=15)
    personal_email = models.EmailField(blank=True, default='', verbose_name='Personal Email')
    batch_year = models.IntegerField(help_text='Year of graduation')
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(10)])
    percentage = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'student_profiles'
        verbose_name = 'Student Profile'
        verbose_name_plural = 'Student Profiles'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} ({self.prn_number})"


class Application(models.Model):
    """Student application for internship"""

    STATUS_CHOICES = [
        ('under_review', 'Under Review'),
        ('shortlisted', 'Shortlisted'),
        ('not_shortlisted', 'Not Shortlisted'),
    ]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='applications')
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE, related_name='applications')
    personal_email = models.EmailField(verbose_name='Personal Email')
    submitted_cgpa = models.DecimalField(max_digits=4, decimal_places=2)
    submitted_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    resume = models.FileField(
        upload_to='resumes/%Y/%m/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        help_text='Upload resume in PDF format (max 5MB)'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='under_review')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'applications'
        verbose_name = 'Application'
        verbose_name_plural = 'Applications'
        ordering = ['-applied_at']
        unique_together = ['student', 'internship']

    def __str__(self):
        return f"{self.student.full_name} - {self.internship.company_name}"

    def save(self, *args, **kwargs):
        if self.resume and self.resume.size > settings.MAX_UPLOAD_SIZE:
            raise ValueError(f'Resume size should not exceed {settings.MAX_UPLOAD_SIZE / (1024*1024)}MB')
        super().save(*args, **kwargs)
