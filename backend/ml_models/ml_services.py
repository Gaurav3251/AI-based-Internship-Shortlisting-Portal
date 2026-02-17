"""
ML service wrapper
"""
from .ml.resume_parser import ResumeParser
from .ml.shortlisting_algorithm import ShortlistingAlgorithm
from .ml.llm_client import LLMClient
from .models import ParsedResume, ShortlistingResult


class MLService:
    def __init__(self):
        self.parser = ResumeParser()
        self.llm_client = LLMClient()
        self.algorithm = ShortlistingAlgorithm(llm_client=self.llm_client)

    def parse_resume(self, pdf_path: str) -> dict:
        return self.parser.parse_resume(pdf_path)

    def evaluate_candidate(self, parsed_data: dict, jd_text: str, min_cgpa: float, min_percentage: float) -> dict:
        jd_data = {'description': jd_text}
        return self.algorithm.calculate_overall_score(parsed_data, jd_data, min_cgpa, min_percentage)

    def process_application(self, application):
        parsed_data = self.parse_resume(application.resume.path)

        # Use application-submitted academic values as authoritative inputs
        parsed_data.setdefault('academic', {})
        if application.submitted_cgpa is not None:
            parsed_data['academic']['cgpa'] = float(application.submitted_cgpa)
        if application.submitted_percentage is not None:
            parsed_data['academic']['percentage'] = float(application.submitted_percentage)

        parsed_resume, _ = ParsedResume.objects.update_or_create(
            application=application,
            defaults={'raw_text': parsed_data.get('raw_text', ''), 'parsed_data': parsed_data}
        )

        result = self.evaluate_candidate(
            parsed_data=parsed_data,
            jd_text=application.internship.description,
            min_cgpa=float(application.internship.min_cgpa),
            min_percentage=float(application.internship.min_percentage)
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
                'reason': result.get('reason', ''),
                'details': result
            }
        )

        application.status = 'shortlisted' if shortlisting_result.is_shortlisted else 'not_shortlisted'
        application.save(update_fields=['status'])

        return parsed_resume, shortlisting_result
