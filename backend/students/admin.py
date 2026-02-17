from django.contrib import admin
from .models import StudentProfile, Application


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('prn_number', 'full_name', 'cgpa', 'batch_year', 'created_at')
    list_filter = ('batch_year', 'gender', 'created_at')
    search_fields = ('prn_number', 'full_name', 'user__email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'internship', 'status', 'submitted_cgpa', 'applied_at')
    list_filter = ('status', 'applied_at', 'internship__company_name')
    search_fields = ('student__full_name', 'student__prn_number', 'internship__company_name')
    ordering = ('-applied_at',)
    readonly_fields = ('applied_at', 'updated_at')

    actions = ['trigger_ml_processing']

    def trigger_ml_processing(self, request, queryset):
        from ml_models.ml_services import MLService
        ml_service = MLService()

        count = 0
        for application in queryset.filter(status='under_review'):
            try:
                ml_service.process_application(application)
                count += 1
            except Exception as e:
                self.message_user(request, f'Error processing {application}: {e}', level='error')

        self.message_user(request, f'Successfully processed {count} applications')

    trigger_ml_processing.short_description = 'Run ML processing on selected applications'
