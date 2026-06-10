from django.contrib import admin
from .models import ParsedResume, ShortlistingResult, FairnessAuditLog


@admin.register(ParsedResume)
class ParsedResumeAdmin(admin.ModelAdmin):
    list_display = ('application', 'parse_confidence', 'created_at')
    search_fields = ('application__student__full_name',)
    ordering = ('-created_at',)


@admin.register(ShortlistingResult)
class ShortlistingResultAdmin(admin.ModelAdmin):
    list_display = (
        'application', 'overall_score', 'domain_alignment_score',
        'certification_score', 'is_shortlisted', 'created_at'
    )
    list_filter = ('is_shortlisted', 'created_at')
    ordering = ('-created_at',)


@admin.register(FairnessAuditLog)
class FairnessAuditLogAdmin(admin.ModelAdmin):
    list_display = ('application', 'overall_score', 'recommended_status', 'final_status', 'created_at')
    list_filter = ('recommended_status', 'final_status', 'identifiers_sanitized', 'created_at')
    ordering = ('-created_at',)
