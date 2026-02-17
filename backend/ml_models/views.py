"""
ML API views
"""
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsTeacher
from students.models import Application
from .ml_services import MLService
from .serializers import ShortlistingResultSerializer


class RunShortlistingView(views.APIView):
    """
    Trigger shortlisting for a specific application (teacher/admin)
    """
    permission_classes = (IsAuthenticated, IsTeacher)

    def post(self, request, application_id):
        try:
            application = Application.objects.select_related('internship').get(pk=application_id)
        except Application.DoesNotExist:
            return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)

        service = MLService()
        _parsed, result = service.process_application(application)

        serializer = ShortlistingResultSerializer(result)
        return Response(serializer.data, status=status.HTTP_200_OK)
