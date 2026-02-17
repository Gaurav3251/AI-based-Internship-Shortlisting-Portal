from django.contrib import admin
from .models import TeacherProfile


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'role', 'department', 'user', 'created_at')
    list_filter = ('department', 'role')
    search_fields = ('full_name', 'user__email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
