from django.urls import path
from .views import StudentProfileView, ApplicationListCreateView, ApplicationDetailView

app_name = 'students'

urlpatterns = [
    path('profile/', StudentProfileView.as_view(), name='profile'),
    path('applications/', ApplicationListCreateView.as_view(), name='applications'),
    path('applications/my/', ApplicationListCreateView.as_view(), name='applications-my'),
    path('applications/<int:pk>/', ApplicationDetailView.as_view(), name='application-detail'),
]
