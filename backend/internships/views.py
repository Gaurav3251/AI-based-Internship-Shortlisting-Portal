"""
Internship views
"""
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsTeacher
from .models import Internship
from .serializers import InternshipSerializer


class InternshipListView(generics.ListCreateAPIView):
    """
    List internships (students see active only) or create (teachers only)
    """
    serializer_class = InternshipSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsTeacher()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = Internship.objects.all()
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            return qs.filter(is_active=is_active.lower() == 'true')
        return qs

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)


class InternshipDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = InternshipSerializer
    queryset = Internship.objects.all()

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsTeacher()]
        return [IsAuthenticated()]

    def get_queryset(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return Internship.objects.filter(posted_by=self.request.user)
        return super().get_queryset()


class TeacherInternshipListCreateView(generics.ListCreateAPIView):
    """
    Teacher creates and lists their internships (legacy endpoint)
    """
    serializer_class = InternshipSerializer
    permission_classes = (IsAuthenticated, IsTeacher)

    def get_queryset(self):
        return Internship.objects.filter(posted_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)


class TeacherInternshipUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = InternshipSerializer
    permission_classes = (IsAuthenticated, IsTeacher)

    def get_queryset(self):
        return Internship.objects.filter(posted_by=self.request.user)
