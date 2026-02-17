from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from students.views import StudentProfileView, ApplicationListCreateView
from teachers.views import AnalyticsView, ExportShortlistedCSVView, ShortlistedStudentsView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/students/', include('students.urls')),
    path('api/teachers/', include('teachers.urls')),
    path('api/internships/', include('internships.urls')),
    path('api/ml/', include('ml_models.urls')),

    # Aliases for frontend contract
    path('api/student/profile/', StudentProfileView.as_view(), name='student-profile-alias'),
    path('api/applications/', ApplicationListCreateView.as_view(), name='applications-alias'),
    path('api/applications/my/', ApplicationListCreateView.as_view(), name='applications-my-alias'),
    path('api/analytics/', AnalyticsView.as_view(), name='analytics-alias'),
    path('api/internships/<int:internship_id>/shortlisted/', ShortlistedStudentsView.as_view(), name='shortlisted-alias'),
    path('api/export/shortlisted/<int:internship_id>/', ExportShortlistedCSVView.as_view(), name='export-shortlisted-alias'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
