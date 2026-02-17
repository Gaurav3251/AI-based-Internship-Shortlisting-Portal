"""
Teacher views for profile and management
"""
from rest_framework import generics, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsTeacher
from django.db.models import Count, Q
from .models import TeacherProfile
from .serializers import TeacherProfileSerializer
from students.models import Application
from students.serializers import ApplicationSerializer
from internships.models import Internship
import csv
from django.http import HttpResponse


class TeacherProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update teacher profile
    """
    serializer_class = TeacherProfileSerializer
    permission_classes = (IsAuthenticated, IsTeacher)

    def get_object(self):
        profile, _created = TeacherProfile.objects.get_or_create(
            user=self.request.user,
            defaults={
                'full_name': self.request.user.get_full_name() or self.request.user.email.split('@')[0],
                'role': 'Professor',
                'department': 'CSE AIML'
            }
        )
        return profile


class AnalyticsView(views.APIView):
    """
    Analytics dashboard data
    """
    permission_classes = (IsAuthenticated, IsTeacher)

    def get(self, request):
        total_applications = Application.objects.count()
        total_shortlisted = Application.objects.filter(status='shortlisted').count()

        company_wise = Internship.objects.annotate(
            shortlisted_count=Count('applications', filter=Q(applications__status='shortlisted'))
        ).values('company_name', 'shortlisted_count').order_by('-shortlisted_count')[:10]

        year_wise = Application.objects.filter(
            status='shortlisted'
        ).values('student__batch_year').annotate(
            shortlisted_count=Count('id')
        ).order_by('student__batch_year')

        return Response({
            'total_applications': total_applications,
            'total_shortlisted': total_shortlisted,
            'total_under_review': Application.objects.filter(status='under_review').count(),
            'total_not_shortlisted': Application.objects.filter(status='not_shortlisted').count(),
            'company_wise': list(company_wise),
            'year_wise': [
                {'batch_year': item['student__batch_year'], 'shortlisted_count': item['shortlisted_count']}
                for item in year_wise
            ]
        })


class ShortlistedStudentsView(views.APIView):
    """
    List all applications for a given internship (teacher view)
    """
    permission_classes = (IsAuthenticated, IsTeacher)

    def get(self, request, internship_id):
        applications = Application.objects.filter(
            internship_id=internship_id,
            internship__posted_by=request.user
        ).select_related('student', 'internship', 'shortlisting_result')

        serializer = ApplicationSerializer(applications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ApplicationStatusUpdateView(views.APIView):
    """
    Update application status (shortlisted / not_shortlisted / under_review)
    """
    permission_classes = (IsAuthenticated, IsTeacher)

    def patch(self, request, application_id):
        status_value = request.data.get('status')
        allowed = {'under_review', 'shortlisted', 'not_shortlisted'}
        if status_value not in allowed:
            return Response({'error': 'Invalid status.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            application = Application.objects.select_related('internship').get(
                pk=application_id,
                internship__posted_by=request.user
            )
        except Application.DoesNotExist:
            return Response({'error': 'Application not found.'}, status=status.HTTP_404_NOT_FOUND)

        application.status = status_value
        application.save(update_fields=['status'])
        serializer = ApplicationSerializer(application)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ExportShortlistedCSVView(views.APIView):
    """
    Export shortlisted students to CSV
    """
    permission_classes = (IsAuthenticated, IsTeacher)

    def get(self, request, internship_id):
        applications = Application.objects.filter(
            internship_id=internship_id,
            status='shortlisted'
        ).select_related('student', 'shortlisting_result')

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="shortlisted_students_{internship_id}.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'PRN', 'Name', 'Email', 'Phone', 'Batch Year', 'CGPA', 'Percentage',
            'Overall Score', 'CGPA Score', 'Skills Score', 'Experience Score',
            'Projects Score', 'Semantic Score', 'Applied At'
        ])

        for app in applications:
            result = app.shortlisting_result
            writer.writerow([
                app.student.prn_number,
                app.student.full_name,
                app.personal_email,
                app.student.phone_number,
                app.student.batch_year,
                app.submitted_cgpa,
                app.submitted_percentage,
                result.overall_score if result else 'N/A',
                result.cgpa_score if result else 'N/A',
                result.skills_score if result else 'N/A',
                result.experience_score if result else 'N/A',
                result.projects_score if result else 'N/A',
                result.semantic_score if result else 'N/A',
                app.applied_at.strftime('%Y-%m-%d %H:%M:%S')
            ])

        return response
