from django.urls import path
from .views import RunShortlistingView

app_name = 'ml_models'

urlpatterns = [
    path('applications/<int:application_id>/run/', RunShortlistingView.as_view(), name='run-shortlisting'),
]
