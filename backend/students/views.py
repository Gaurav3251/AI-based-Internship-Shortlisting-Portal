"""
Student views for profile and applications
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsStudent
from .models import StudentProfile, Application
from .serializers import StudentProfileSerializer, ApplicationSerializer, ApplicationCreateSerializer
from ml_models.ml_services import MLService


class StudentProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update student profile
    """
    serializer_class = StudentProfileSerializer
    permission_classes = (IsAuthenticated, IsStudent)

    def get_object(self):
        profile, _created = StudentProfile.objects.get_or_create(
            user=self.request.user,
            defaults={
                'full_name': self.request.user.get_full_name() or self.request.user.email.split('@')[0],
                'prn_number': f'TEMP_{self.request.user.id}',
                'gender': 'other',
                'date_of_birth': '2000-01-01',
                'phone_number': '+910000000000',
                'personal_email': self.request.user.email,
                'batch_year': 2025,
                'cgpa': 0.0,
                'percentage': 0.0
            }
        )
        return profile


class ApplicationListCreateView(generics.ListCreateAPIView):
    """
    List student's applications or create new application
    """
    permission_classes = (IsAuthenticated, IsStudent)

    def get_queryset(self):
        return Application.objects.filter(
            student=self.request.user.student_profile
        ).select_related('internship', 'student')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ApplicationCreateSerializer
        return ApplicationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application = serializer.save()

        # Run ML processing synchronously for real-time shortlisting
        try:
            MLService().process_application(application)
        except Exception:
            pass

        return Response({
            'message': 'Application submitted successfully',
            'application_id': application.id,
            'status': application.status
        }, status=status.HTTP_201_CREATED)


class ApplicationDetailView(generics.RetrieveAPIView):
    """
    Get application details
    """
    serializer_class = ApplicationSerializer
    permission_classes = (IsAuthenticated, IsStudent)

    def get_queryset(self):
        return Application.objects.filter(student=self.request.user.student_profile)
