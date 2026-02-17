from django.contrib import admin
from .models import Internship


@admin.register(Internship)
class InternshipAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'internship_role', 'min_cgpa', 'deadline', 'is_active', 'created_at')
    list_filter = ('is_active', 'deadline', 'created_at')
    search_fields = ('company_name', 'internship_role', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
