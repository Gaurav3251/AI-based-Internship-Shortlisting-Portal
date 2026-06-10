"""
Teacher views for profile and management
"""
from rest_framework import generics, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsTeacher
from django.db.models import Count, Q
from collections import Counter
from .models import TeacherProfile
from .serializers import TeacherProfileSerializer
from students.models import Application
from students.serializers import ApplicationSerializer
from internships.models import Internship
from ml_models.models import FairnessAuditLog
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

    def _build_skill_gap(self):
        counter = Counter()
        apps = Application.objects.filter(
            status__in=['under_review', 'not_shortlisted'],
            shortlisting_result__isnull=False
        ).select_related('shortlisting_result')
        for app in apps:
            details = (app.shortlisting_result.details or {})
            missing = (
                details.get('match_details', {})
                .get('skills', {})
                .get('missing_required_skills', [])
            )
            for skill in missing:
                if skill:
                    counter[skill] += 1
        return [{'skill': skill, 'count': count} for skill, count in counter.most_common(10)]

    def _build_domain_trends(self):
        apps = Application.objects.filter(shortlisting_result__isnull=False).select_related('shortlisting_result')
        domain_totals = Counter()
        domain_shortlisted = Counter()
        for app in apps:
            details = app.shortlisting_result.details or {}
            domain = details.get('match_details', {}).get('domain') or 'general'
            domain_totals[domain] += 1
            if app.status == 'shortlisted':
                domain_shortlisted[domain] += 1
        trends = []
        for domain, total in domain_totals.items():
            shortlisted = domain_shortlisted.get(domain, 0)
            trends.append({
                'domain': domain,
                'applications': total,
                'shortlisted': shortlisted,
                'shortlist_rate': round((shortlisted / total) * 100, 2) if total else 0.0
            })
        trends.sort(key=lambda x: x['applications'], reverse=True)
        return trends

    def _build_fairness_summary(self):
        apps = Application.objects.select_related('student')
        # Group-wise rates by gender
        gender_groups = {}
        batch_groups = {}
        for app in apps:
            gender = app.student.gender or 'unknown'
            batch = str(app.student.batch_year or 'unknown')
            gender_groups.setdefault(gender, {'total': 0, 'shortlisted': 0})
            batch_groups.setdefault(batch, {'total': 0, 'shortlisted': 0})
            gender_groups[gender]['total'] += 1
            batch_groups[batch]['total'] += 1
            if app.status == 'shortlisted':
                gender_groups[gender]['shortlisted'] += 1
                batch_groups[batch]['shortlisted'] += 1

        def _format(groups):
            rows = []
            rates = []
            for key, val in groups.items():
                total = val['total']
                shortlisted = val['shortlisted']
                rate = (shortlisted / total) * 100 if total else 0
                rates.append(rate)
                rows.append({
                    'group': key,
                    'total': total,
                    'shortlisted': shortlisted,
                    'shortlist_rate': round(rate, 2)
                })
            adverse_impact_ratio = 1.0
            non_zero = [r for r in rates if r > 0]
            if len(non_zero) >= 2:
                adverse_impact_ratio = round(min(non_zero) / max(non_zero), 4)
            return rows, adverse_impact_ratio

        gender_rows, gender_air = _format(gender_groups)
        batch_rows, batch_air = _format(batch_groups)

        return {
            'gender_outcomes': gender_rows,
            'batch_outcomes': batch_rows,
            'gender_adverse_impact_ratio': gender_air,
            'batch_adverse_impact_ratio': batch_air
        }

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
            ],
            'skill_gap': self._build_skill_gap(),
            'domain_trends': self._build_domain_trends(),
            'fairness': self._build_fairness_summary()
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


class InternshipRankingView(views.APIView):
    """
    Ranking list per internship with explicit Top-N policy recommendation.
    """
    permission_classes = (IsAuthenticated, IsTeacher)

    def get(self, request, internship_id):
        try:
            top_n = int(request.query_params.get('top_n', 20))
        except ValueError:
            top_n = 20
        top_n = max(1, min(top_n, 500))

        applications = list(
            Application.objects.filter(
                internship_id=internship_id,
                internship__posted_by=request.user
            ).select_related('student', 'internship', 'shortlisting_result')
        )

        applications.sort(
            key=lambda app: (
                (app.shortlisting_result.overall_score if getattr(app, 'shortlisting_result', None) else 0.0),
                app.id
            ),
            reverse=True
        )

        rows = []
        for idx, app in enumerate(applications, start=1):
            serialized = ApplicationSerializer(app).data
            details = (serialized.get('shortlisting_result') or {}).get('details') or {}
            cgpa_eligible = details.get('cgpa_eligible', False)
            serialized['rank'] = idx
            serialized['top_n_policy_recommended'] = bool(idx <= top_n and cgpa_eligible)
            rows.append(serialized)

        return Response(
            {
                'internship_id': internship_id,
                'top_n': top_n,
                'count': len(rows),
                'results': rows
            },
            status=status.HTTP_200_OK
        )


class ApplicationStatusUpdateView(views.APIView):
    """
    Update application status (shortlisted / not_shortlisted / under_review)
    """
    permission_classes = (IsAuthenticated, IsTeacher)

    def patch(self, request, application_id):
        status_value = request.data.get('status')
        feedback_note = request.data.get('feedback_note', '')
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

        previous_status = application.status
        application.status = status_value
        application.save(update_fields=['status'])

        FairnessAuditLog.objects.create(
            application=application,
            evaluator=request.user,
            overall_score=getattr(getattr(application, 'shortlisting_result', None), 'overall_score', 0.0),
            recommended_status=(
                (getattr(getattr(application, 'shortlisting_result', None), 'details', {}) or {}).get('recommended_status', '')
            ),
            final_status=status_value,
            protected_attributes={
                'gender': application.student.gender,
                'batch_year': application.student.batch_year
            },
            audit_payload={
                'override': True,
                'previous_status': previous_status,
                'feedback_note': feedback_note
            },
            identifiers_sanitized=True
        )
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
            'Projects Score', 'Semantic Score', 'Domain Alignment Score',
            'Certification Score', 'Parser Confidence', 'Applied At'
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
                result.domain_alignment_score if result else 'N/A',
                result.certification_score if result else 'N/A',
                result.parser_confidence if result else 'N/A',
                app.applied_at.strftime('%Y-%m-%d %H:%M:%S')
            ])

        return response
