from django.core.management.base import BaseCommand
from students.models import Application
from ml_models.ml_services import MLService


class Command(BaseCommand):
    help = 'Run ML shortlisting for all applications under review'

    def handle(self, *args, **options):
        service = MLService()
        applications = Application.objects.filter(status='under_review').select_related('internship')
        processed = 0

        for application in applications:
            try:
                service.process_application(application)
                processed += 1
            except Exception as exc:
                self.stderr.write(f'Error processing application {application.id}: {exc}')

        self.stdout.write(self.style.SUCCESS(f'Processed {processed} applications'))
