from django.urls import path
from .views import InternshipListView, InternshipDetailView, TeacherInternshipListCreateView, TeacherInternshipUpdateView

app_name = 'internships'

urlpatterns = [
    path('', InternshipListView.as_view(), name='list'),
    path('<int:pk>/', InternshipDetailView.as_view(), name='detail'),
    path('teacher/', TeacherInternshipListCreateView.as_view(), name='teacher-list-create'),
    path('teacher/<int:pk>/', TeacherInternshipUpdateView.as_view(), name='teacher-update'),
]
