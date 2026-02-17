from django.contrib import admin
from .models import ParsedResume, ShortlistingResult


@admin.register(ParsedResume)
class ParsedResumeAdmin(admin.ModelAdmin):
    list_display = ('application', 'created_at')
    search_fields = ('application__student__full_name',)
    ordering = ('-created_at',)


@admin.register(ShortlistingResult)
class ShortlistingResultAdmin(admin.ModelAdmin):
    list_display = ('application', 'overall_score', 'is_shortlisted', 'created_at')
    list_filter = ('is_shortlisted', 'created_at')
    ordering = ('-created_at',)
