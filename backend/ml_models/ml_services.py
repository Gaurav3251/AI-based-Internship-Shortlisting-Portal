"""
ML service wrapper
"""
import re
from .ml.resume_parser import ResumeParser
from .ml.shortlisting_algorithm import ShortlistingAlgorithm
from .ml.llm_client import LLMClient
from .models import ParsedResume, ShortlistingResult, FairnessAuditLog


class MLService:
    def __init__(self):
        self.parser = ResumeParser()
        self.llm_client = LLMClient()
        self.algorithm = ShortlistingAlgorithm(llm_client=self.llm_client)

    def parse_resume(self, pdf_path: str) -> dict:
        return self.parser.parse_resume(pdf_path)

    def sanitize_resume_text(self, parsed_data: dict) -> str:
        """
        Remove direct identifiers before semantic scoring to reduce bias risk.
        """
        text = parsed_data.get('raw_text', '') or ''

        # Remove emails
        text = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', ' ', text)
        # Remove phone-like patterns
        text = re.sub(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', ' ', text)

        name = (((parsed_data.get('personal_info') or {}).get('name')) or '').strip()
        if name:
            text = re.sub(re.escape(name), ' ', text, flags=re.IGNORECASE)

        return re.sub(r'\s+', ' ', text).strip()

    def evaluate_candidate(self, parsed_data: dict, jd_text: str, min_cgpa: float, min_percentage: float,
                           candidate_profile: dict, internship_constraints: dict) -> dict:
        jd_data = {'description': jd_text}
        return self.algorithm.calculate_overall_score(
            parsed_data, jd_data, min_cgpa, min_percentage,
            candidate_profile=candidate_profile,
            internship_constraints=internship_constraints
        )

    def process_application(self, application):
        parsed_data = self.parse_resume(application.resume.path)
        parsed_data['sanitized_text'] = self.sanitize_resume_text(parsed_data)
        parse_confidence = float(parsed_data.get('parse_confidence', 0.0) or 0.0)

        # Use application-submitted academic values as authoritative inputs
        parsed_data.setdefault('academic', {})
        if application.submitted_cgpa is not None:
            parsed_data['academic']['cgpa'] = float(application.submitted_cgpa)
        if application.submitted_percentage is not None:
            parsed_data['academic']['percentage'] = float(application.submitted_percentage)

        parsed_resume, _ = ParsedResume.objects.update_or_create(
            application=application,
            defaults={
                'raw_text': parsed_data.get('raw_text', ''),
                'parsed_data': parsed_data,
                'parse_confidence': parse_confidence
            }
        )

        candidate_profile = {
            'batch_year': application.student.batch_year,
            'gender': application.student.gender
        }
        internship_constraints = {
            'eligible_batch_years': application.internship.eligible_batch_years
        }
        result = self.evaluate_candidate(
            parsed_data=parsed_data,
            jd_text=application.internship.description,
            min_cgpa=float(application.internship.min_cgpa),
            min_percentage=float(application.internship.min_percentage),
            candidate_profile=candidate_profile,
            internship_constraints=internship_constraints
        )

        shortlisting_result, _ = ShortlistingResult.objects.update_or_create(
            application=application,
            defaults={
                'overall_score': result.get('overall_score', 0),
                'is_shortlisted': result.get('is_shortlisted', False),
                'cgpa_score': result.get('detailed_scores', {}).get('cgpa', 0),
                'skills_score': result.get('detailed_scores', {}).get('skills', 0),
                'experience_score': result.get('detailed_scores', {}).get('experience', 0),
                'projects_score': result.get('detailed_scores', {}).get('projects', 0),
                'semantic_score': result.get('detailed_scores', {}).get('semantic', 0),
                'domain_alignment_score': result.get('detailed_scores', {}).get('domain_alignment', 0),
                'certification_score': result.get('detailed_scores', {}).get('certification', 0),
                'parser_confidence': parse_confidence,
                'reason': result.get('reason', ''),
                'details': result
            }
        )

        final_status = result.get('recommended_status', 'shortlisted' if shortlisting_result.is_shortlisted else 'not_shortlisted')
        application.status = final_status
        application.save(update_fields=['status'])

        FairnessAuditLog.objects.create(
            application=application,
            overall_score=result.get('overall_score', 0.0),
            recommended_status=result.get('recommended_status', ''),
            final_status=final_status,
            protected_attributes={
                'gender': application.student.gender,
                'batch_year': application.student.batch_year
            },
            audit_payload={
                'cgpa_eligible': result.get('cgpa_eligible', False),
                'parser_confidence': parse_confidence,
                'domain_mismatch': result.get('match_details', {}).get('domain_mismatch', False),
                'used_features': ['academic', 'skills', 'experience', 'projects', 'semantic', 'domain_alignment', 'certification'],
                'excluded_features': ['name', 'email', 'phone']
            },
            identifiers_sanitized=True
        )

        return parsed_resume, shortlisting_result
