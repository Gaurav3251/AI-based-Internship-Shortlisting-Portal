from django.urls import path
from .views import (
    TeacherProfileView, AnalyticsView, ExportShortlistedCSVView,
    ShortlistedStudentsView, ApplicationStatusUpdateView, InternshipRankingView
)

app_name = 'teachers'

urlpatterns = [
    path('profile/', TeacherProfileView.as_view(), name='profile'),
    path('analytics/', AnalyticsView.as_view(), name='analytics'),
    path('internships/<int:internship_id>/shortlisted/', ShortlistedStudentsView.as_view(), name='shortlisted'),
    path('internships/<int:internship_id>/ranking/', InternshipRankingView.as_view(), name='ranking'),
    path('internships/<int:internship_id>/export-csv/', ExportShortlistedCSVView.as_view(), name='export-csv'),
    path('applications/<int:application_id>/status/', ApplicationStatusUpdateView.as_view(), name='application-status'),
]
