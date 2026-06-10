"""
Advanced Shortlisting Algorithm
Rule-based + Semantic Matching Hybrid Approach
Uses: CGPA filtering, keyword matching, semantic similarity, domain relevance
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from .skill_normalizer import SkillNormalizer


class ShortlistingAlgorithm:
    """
    Advanced shortlisting algorithm for candidate-JD matching
    
    Features:
    - Primary CGPA/Percentage filtering
    - Keyword matching with domain relevance
    - Semantic similarity using embeddings
    - Experience and project relevance scoring
    - Multi-criteria scoring with configurable weights
    """
    
    def __init__(self, config: Optional[Dict] = None, llm_client=None):
        """
        Initialize shortlisting algorithm
        
        Args:
            config: Configuration dictionary with scoring weights
        """
        # Load embedding model for semantic similarity
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        self.llm_client = llm_client
        
        # Default configuration
        self.config = config or {
            'weights': {
                'cgpa': 0.25,
                'skills': 0.22,
                'experience': 0.15,
                'projects': 0.10,
                'semantic': 0.08,
                'domain_alignment': 0.12,
                'certification': 0.08
            },
            'cgpa_threshold_strict': True,  # If True, reject below threshold immediately
            'min_skill_match': 2,           # Minimum matching skills required
            'domain_mismatch_penalty': 0.3,  # Penalty for domain mismatch
            'parser_confidence_threshold': 55.0,
            'auto_shortlist_score': 60.0,
            'high_signal_shortlist_score': 55.0,
            'under_review_min_score': 45.0
        }
        
        self.domain_keywords = self._load_domain_keywords()

    def _load_domain_keywords(self) -> Dict[str, Dict[str, List[str]]]:
        base_dir = Path(__file__).resolve().parent / "skill_taxonomy"
        path = base_dir / "domains.json"
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def _all_known_skills(self) -> List[str]:
        items = []
        for _, data in self.domain_keywords.items():
            items.extend(data.get('required', []))
            items.extend(data.get('bonus', []))
        return SkillNormalizer.normalize_list(items)

    def _extract_jd_section(self, text: str, headings: List[str]) -> str:
        """
        Extract a JD section by heading names like 'Tech Stack', 'Eligibility', etc.
        Returns section content (possibly empty string).
        """
        if not text:
            return ''
        lines = text.splitlines()
        start = None
        heading_pattern = re.compile(
            r'^\s*(?:' + '|'.join(re.escape(h) for h in headings) + r')\s*:?\s*$',
            re.IGNORECASE
        )
        any_heading_pattern = re.compile(
            r'^\s*(tech stack|skills?|requirements?|key responsibilities|responsibilities|eligibility|'
            r'good to have|preferred|nice to have|about role|overview)\s*:?\s*$',
            re.IGNORECASE
        )
        for i, line in enumerate(lines):
            if heading_pattern.match((line or '').strip()):
                start = i
                break
        if start is None:
            return ''
        chunk: List[str] = []
        for line in lines[start + 1:]:
            stripped = (line or '').strip()
            if any_heading_pattern.match(stripped):
                break
            chunk.append(line)
        return '\n'.join(chunk).strip()

    def _detect_resume_branch(self, resume_text: str) -> str:
        text = (resume_text or "").lower()
        patterns = {
            'mechanical': ['mechanical engineering', 'mech engineering', 'thermodynamics', 'manufacturing', 'cad'],
            'civil': ['civil engineering', 'structural engineering', 'geotechnical', 'construction management', 'autocad civil'],
            'electrical': ['electrical engineering', 'power systems', 'circuits', 'embedded systems', 'vlsi'],
            'electronics': ['electronics engineering', 'ece', 'microcontrollers', 'signal processing'],
            'cs_it': ['computer science', 'information technology', 'software engineering', 'cse', 'it branch']
        }
        for branch, keys in patterns.items():
            if any(k in text for k in keys):
                return branch
        return 'unknown'

    def _is_tech_domain(self, jd_domain: str) -> bool:
        return jd_domain in {
            'web_development', 'backend', 'data_science', 'ai_ml', 'cloud_devops',
            'mobile_development', 'data_analytics', 'qa_testing'
        }

    def _should_direct_reject_by_branch(self, resume_text: str, jd_domain: str, skill_details: Dict) -> bool:
        branch = self._detect_resume_branch(resume_text)
        if branch in {'mechanical', 'civil'} and self._is_tech_domain(jd_domain):
            # Allow borderline manual review only if there is meaningful direct skill evidence.
            if skill_details.get('required_matches', 0) < 1:
                return True
        return False

    def _decide_status(self, cgpa_eligible: bool, cgpa_missing: bool, has_mismatch: bool, overall_score: float,
                       skill_details: Dict, resume_text: str, jd_domain: str,
                       detailed_scores: Dict[str, float], parse_confidence: float) -> Tuple[str, str]:
        min_skill_matches = skill_details['required_matches'] >= self.config['min_skill_match']
        skill_score = float(detailed_scores.get('skills', 0.0) or 0.0)
        experience_score = float(detailed_scores.get('experience', 0.0) or 0.0)
        project_score = float(detailed_scores.get('projects', 0.0) or 0.0)
        domain_alignment_score = float(detailed_scores.get('domain_alignment', 0.0) or 0.0)
        certification_score = float(detailed_scores.get('certification', 0.0) or 0.0)

        if self._should_direct_reject_by_branch(resume_text, jd_domain, skill_details):
            return 'not_shortlisted', 'Severe branch-role mismatch for tech role'

        if not cgpa_eligible and not cgpa_missing:
            return 'not_shortlisted', 'Does not meet CGPA/Percentage requirement'

        if has_mismatch and overall_score < 45:
            return 'not_shortlisted', 'Domain mismatch with low confidence score'

        strong_signal = (
            min_skill_matches and
            (skill_score >= 60 or domain_alignment_score >= 55) and
            (experience_score >= 45 or project_score >= 45 or certification_score >= 50)
        )

        if cgpa_eligible and min_skill_matches and overall_score >= self.config['auto_shortlist_score']:
            if parse_confidence >= self.config['parser_confidence_threshold']:
                return 'shortlisted', 'Candidate meets all criteria'
            return 'under_review', f'Good match but low parser confidence ({parse_confidence:.1f}%)'

        if (
            cgpa_eligible and
            strong_signal and
            overall_score >= self.config['high_signal_shortlist_score'] and
            not has_mismatch
        ):
            if parse_confidence >= self.config['parser_confidence_threshold']:
                return 'shortlisted', 'Strong skills/experience evidence for role'
            return 'under_review', f'Strong profile but low parser confidence ({parse_confidence:.1f}%)'

        if cgpa_eligible and overall_score >= self.config['under_review_min_score']:
            return 'under_review', f'Borderline match ({overall_score:.1f}%), requires faculty review'

        if cgpa_missing and overall_score >= self.config['under_review_min_score']:
            return 'under_review', 'Academic score missing; routed for faculty review'

        return 'not_shortlisted', f'Overall score too low ({overall_score:.1f}%)'
    
    def extract_jd_requirements(self, jd_text: str) -> Dict:
        """
        Extract key requirements from job description
        
        Args:
            jd_text: Job description text
            
        Returns:
            Dictionary with extracted requirements
        """
        # Detect domain/role
        detected_domain = self._detect_domain(jd_text)

        tech_stack_text = self._extract_jd_section(jd_text, ['Tech Stack', 'Skills', 'Technical Skills'])
        responsibilities_text = self._extract_jd_section(jd_text, ['Key Responsibilities', 'Responsibilities'])
        eligibility_text = self._extract_jd_section(jd_text, ['Eligibility', 'Requirements', 'Must Have'])
        preferred_text = self._extract_jd_section(jd_text, ['Good to Have', 'Nice to Have', 'Preferred', 'Bonus'])

        # Extract required skills from high-signal sections for internship JDs.
        required_skills = SkillNormalizer.normalize_list(
            self._extract_skills_from_text(tech_stack_text, section_keywords=['stack', 'skills']) +
            self._extract_skills_from_text(responsibilities_text, section_keywords=['responsibilities']) +
            self._extract_skills_from_text(eligibility_text, section_keywords=['eligibility', 'requirements', 'must have']) +
            self._extract_skills_from_text(jd_text, section_keywords=['required', 'must have'])
        )

        # Preferred skills from explicit preferred sections + cloud/tool extras.
        preferred_skills = SkillNormalizer.normalize_list(
            self._extract_skills_from_text(preferred_text, section_keywords=['preferred', 'nice to have', 'bonus', 'good to have']) +
            self._extract_skills_from_text(jd_text, section_keywords=['preferred', 'nice to have', 'bonus', 'good to have'])
        )

        # If extraction is sparse, backfill from domain taxonomy keywords present in JD text.
        if len(required_skills) < 4:
            jd_lower = jd_text.lower()
            domain_data = self.domain_keywords.get(detected_domain, {})
            inferred_required = [k for k in domain_data.get('required', []) if k in jd_lower]
            required_skills = SkillNormalizer.normalize_list(required_skills + inferred_required)
        if len(preferred_skills) < 3:
            jd_lower = jd_text.lower()
            domain_data = self.domain_keywords.get(detected_domain, {})
            inferred_bonus = [k for k in domain_data.get('bonus', []) if k in jd_lower]
            preferred_skills = SkillNormalizer.normalize_list(preferred_skills + inferred_bonus)

        # Keep required/preferred distinct where possible.
        preferred_skills = [s for s in preferred_skills if s not in set(required_skills)]
        
        # Extract experience requirements
        experience_years = self._extract_experience_requirement(jd_text)
        
        # Extract education requirements
        education_req = self._extract_education_requirement(jd_text)
        
        return {
            'domain': detected_domain,
            'required_skills': required_skills,
            'preferred_skills': preferred_skills,
            'eligible_batch_years': self._extract_batch_years(jd_text),
            'experience_years': experience_years,
            'education': education_req,
            'full_text': jd_text
        }

    def _extract_batch_years(self, text: str) -> List[int]:
        # Examples: "Batch 2026", "2025/2026 batch", "graduating in 2026"
        years = re.findall(r'\b(20\d{2})\b', text)
        parsed = sorted({int(y) for y in years if 2000 <= int(y) <= 2100})
        return parsed

    def _detect_domain(self, text: str) -> str:
        """Detect domain/category of job role"""
        text_lower = text.lower()
        domain_scores = {}
        
        for domain, keywords in self.domain_keywords.items():
            score = 0
            all_keywords = keywords['required'] + keywords['bonus']
            
            for keyword in all_keywords:
                if keyword in text_lower:
                    score += 1
            
            domain_scores[domain] = score
        
        # Return domain with highest score
        if domain_scores:
            return max(domain_scores, key=domain_scores.get)
        return 'general'
    
    def _extract_skills_from_text(self, text: str, section_keywords: List[str]) -> List[str]:
        """Extract skills from specific sections of text"""
        skills: List[str] = []
        if not text:
            return skills
        text_lower = text.lower()
        
        # Look for section with keywords
        for keyword in section_keywords:
            pattern = rf'{keyword}[\s:]+([^\n]+(?:\n[^\n]+)*?)(?=\n\s*\n|\Z)'
            matches = re.findall(pattern, text_lower, re.IGNORECASE | re.DOTALL)
            
            for match in matches:
                # Split by common delimiters
                tokens = re.split(r'[,|;:\n\u2022\-()]', match)
                for token in tokens:
                    token = token.strip()
                    if token and len(token.split()) <= 4:
                        skills.append(token)

        # Backfill by scanning taxonomy skills in the passed text.
        for skill in self._all_known_skills():
            if skill and skill in text_lower:
                skills.append(skill)
        
        return SkillNormalizer.normalize_list(list(set(skills)))

    def _apply_llm_enrichment(self, parsed_resume: Dict, jd_requirements: Dict) -> None:
        if not self.llm_client:
            return
        llm_data = self.llm_client.extract_skills(
            parsed_resume.get('raw_text', ''),
            jd_requirements.get('full_text', '')
        )
        if not llm_data:
            return
        resume_skills = llm_data.get('resume_skills', [])
        jd_required = llm_data.get('jd_required', [])
        jd_preferred = llm_data.get('jd_preferred', [])
        synonyms = llm_data.get('synonyms', [])

        if resume_skills:
            parsed_resume['skills'] = SkillNormalizer.merge_into_other(
                parsed_resume.get('skills', {}),
                resume_skills
            )

        if jd_required:
            jd_requirements['required_skills'] = SkillNormalizer.normalize_list(
                jd_requirements.get('required_skills', []) + jd_required
            )
        if jd_preferred:
            jd_requirements['preferred_skills'] = SkillNormalizer.normalize_list(
                jd_requirements.get('preferred_skills', []) + jd_preferred
            )
        if synonyms:
            jd_requirements['preferred_skills'] = SkillNormalizer.normalize_list(
                jd_requirements.get('preferred_skills', []) + synonyms
            )

    def _count_candidate_skills(self, candidate_skills: Dict[str, List[str]]) -> int:
        total = 0
        for skills in candidate_skills.values():
            total += len(skills)
        return total
    
    def _extract_experience_requirement(self, text: str) -> float:
        """Extract required years of experience"""
        # Pattern: "X years", "X+ years", "X-Y years"
        pattern = r'(\d+)(?:\s*-\s*(\d+))?\s*(?:\+)?\s*years?\s+(?:of\s+)?experience'
        matches = re.findall(pattern, text.lower())
        
        if matches:
            # Take minimum years if range given
            return float(matches[0][0])
        
        # Check for "fresher" or "entry level"
        if re.search(r'fresher|entry level|no experience', text.lower()):
            return 0.0
        
        return 0.0  # Default to fresher-friendly
    
    def _extract_education_requirement(self, text: str) -> str:
        """Extract education requirements"""
        if re.search(r'b\.?tech|b\.?e\.?|bachelor', text.lower()):
            return 'BTech/BE'
        elif re.search(r'm\.?tech|m\.?e\.?|master', text.lower()):
            return 'MTech/ME'
        return 'BTech/BE'  # Default

    def evaluate_policy_eligibility(self, candidate_batch_year: Optional[int],
                                    jd_requirements: Dict, internship_constraints: Optional[Dict]) -> Tuple[bool, str]:
        """
        Enforce batch-year policy checks.
        """
        constraints = internship_constraints or {}
        allowed_batches = constraints.get('eligible_batch_years') or []
        if isinstance(allowed_batches, str):
            allowed_batches = [
                int(v.strip()) for v in allowed_batches.split(',')
                if v.strip().isdigit()
            ]
        if allowed_batches and candidate_batch_year is not None and candidate_batch_year not in allowed_batches:
            return False, 'Batch year not eligible for internship constraints'

        jd_batches = jd_requirements.get('eligible_batch_years') or []
        if jd_batches and candidate_batch_year is not None and candidate_batch_year not in jd_batches:
            return False, 'Batch year does not match JD batch criteria'

        return True, 'Eligible'
    
    def check_cgpa_eligibility(self, candidate_cgpa: float, candidate_percentage: float,
                               min_cgpa: float, min_percentage: float) -> Tuple[bool, float]:
        """
        Check if candidate meets CGPA/Percentage criteria
        
        Args:
            candidate_cgpa: Candidate's CGPA
            candidate_percentage: Candidate's percentage
            min_cgpa: Minimum required CGPA
            min_percentage: Minimum required percentage
            
        Returns:
            Tuple of (is_eligible, normalized_score)
        """
        # If both missing, allow soft scoring
        if not candidate_cgpa and not candidate_percentage:
            return True, 50.0

        # Check CGPA
        cgpa_eligible = candidate_cgpa >= min_cgpa if candidate_cgpa else False

        # Check percentage
        percentage_eligible = candidate_percentage >= min_percentage if candidate_percentage else False

        # Candidate is eligible if either criteria is met
        is_eligible = cgpa_eligible or percentage_eligible
        
        # Calculate normalized score (0-100)
        if candidate_cgpa:
            cgpa_score = (candidate_cgpa / 10.0) * 100
        elif candidate_percentage:
            cgpa_score = candidate_percentage
        else:
            cgpa_score = 0
        
        return is_eligible, min(cgpa_score, 100)
    
    def calculate_skill_match_score(self, candidate_skills: Dict[str, List[str]], 
                                    jd_requirements: Dict) -> Tuple[float, Dict]:
        """
        Calculate skill matching score
        
        Returns:
            Tuple of (score, details_dict)
        """
        jd_domain = jd_requirements['domain']
        required_skills = SkillNormalizer.normalize_list(jd_requirements['required_skills'])
        preferred_skills = SkillNormalizer.normalize_list(jd_requirements['preferred_skills'])
        
        # Flatten candidate skills
        all_candidate_skills = []
        for domain, skills in candidate_skills.items():
            all_candidate_skills.extend(SkillNormalizer.normalize_list(skills))
        
        # Count matches
        matched_required_skills = [
            skill for skill in required_skills
            if any(skill in cs or cs in skill for cs in all_candidate_skills)
        ]
        matched_preferred_skills = [
            skill for skill in preferred_skills
            if any(skill in cs or cs in skill for cs in all_candidate_skills)
        ]
        required_matches = len(matched_required_skills)
        preferred_matches = len(matched_preferred_skills)
        
        # Calculate domain relevance
        domain_score = 0
        if jd_domain in candidate_skills:
            domain_score = len(candidate_skills[jd_domain]) * 5  # Bonus for domain match
        
        # Check related domains
        related_domains = self.domain_keywords.get(jd_domain, {}).get('related_domains', [])
        for rel_domain in related_domains:
            if rel_domain in candidate_skills:
                domain_score += len(candidate_skills[rel_domain]) * 2
        
        # Calculate final score
        total_required = max(len(required_skills), 1)
        total_preferred = max(len(preferred_skills), 1)
        
        required_score = (required_matches / total_required) * 60  # 60% for required
        preferred_score = (preferred_matches / total_preferred) * 20  # 20% for preferred
        domain_bonus = min(domain_score, 20)  # 20% for domain relevance
        
        total_score = required_score + preferred_score + domain_bonus
        
        details = {
            'required_matches': required_matches,
            'total_required': total_required,
            'preferred_matches': preferred_matches,
            'total_preferred': total_preferred,
            'domain_relevance': domain_bonus,
            'required_skills': required_skills,
            'preferred_skills': preferred_skills,
            'matched_required_skills': matched_required_skills,
            'missing_required_skills': [s for s in required_skills if s not in matched_required_skills],
            'matched_skills': [s for s in all_candidate_skills
                               if any(req in s or s in req for req in required_skills + preferred_skills)]
        }

        return min(total_score, 100), details

    def calculate_domain_alignment_score(self, candidate_skills: Dict[str, List[str]], jd_requirements: Dict) -> float:
        jd_domain = jd_requirements.get('domain', 'general')
        if not candidate_skills:
            return 0.0

        domain_keywords = self.domain_keywords.get(jd_domain, {})
        # Use JD-specific focus first; fallback to domain required list.
        focus_keywords = SkillNormalizer.normalize_list(
            (jd_requirements.get('required_skills') or []) +
            (jd_requirements.get('preferred_skills') or []) +
            domain_keywords.get('required', [])
        )
        if not focus_keywords:
            return 50.0

        all_candidate_skills = []
        for _, skills in candidate_skills.items():
            all_candidate_skills.extend(SkillNormalizer.normalize_list(skills))

        matches = sum(1 for k in focus_keywords if any(k in s or s in k for s in all_candidate_skills))
        # Smooth denominator to avoid harsh penalties when JD has very long keyword lists.
        denom = max(min(len(focus_keywords), 16), 4)
        return round(min((matches / denom) * 100.0, 100.0), 2)

    def calculate_certification_score(self, achievements: List[str], jd_requirements: Dict) -> Tuple[float, Dict]:
        if not achievements:
            return 0.0, {'matched_certifications': [], 'total_achievements': 0}

        all_text = ' '.join(achievements).lower()
        cert_keywords = [
            'certified', 'certification', 'aws', 'azure', 'gcp', 'oracle', 'coursera',
            'udemy', 'nptel', 'tensorflow', 'kubernetes', 'data science', 'machine learning'
        ]
        matched = [kw for kw in cert_keywords if kw in all_text]
        jd_skills = SkillNormalizer.normalize_list(jd_requirements.get('required_skills', []) + jd_requirements.get('preferred_skills', []))
        jd_overlap = [skill for skill in jd_skills if skill in all_text]

        base_score = min(len(matched) * 12, 70)
        overlap_bonus = min(len(jd_overlap) * 10, 30)
        return min(float(base_score + overlap_bonus), 100.0), {
            'matched_certifications': matched,
            'jd_overlap': jd_overlap,
            'total_achievements': len(achievements)
        }
    
    def calculate_experience_score(self, candidate_experience: List[Dict], 
                                   jd_requirements: Dict) -> Tuple[float, Dict]:
        """
        Calculate experience relevance score
        
        Returns:
            Tuple of (score, details_dict)
        """
        if not candidate_experience:
            # Freshers get partial score if JD allows
            if jd_requirements['experience_years'] == 0:
                return 50, {'type': 'fresher_eligible', 'relevant_experience': []}
            return 20, {'type': 'no_experience', 'relevant_experience': []}
        
        jd_domain = jd_requirements['domain']
        jd_text = jd_requirements['full_text'].lower()
        
        relevant_experiences = []
        total_score = 0
        
        for exp in candidate_experience:
            exp_text = exp.get('description', '').lower()
            role = exp.get('role', '').lower() if exp.get('role') else ''
            
            # Check domain relevance
            relevance_score = 0
            
            # Check if role matches
            domain_keywords = self.domain_keywords.get(jd_domain, {})
            for keyword in domain_keywords.get('required', []) + domain_keywords.get('bonus', []):
                if keyword in exp_text or keyword in role:
                    relevance_score += 5
            
            # Check skill overlap
            jd_skills = jd_requirements['required_skills'] + jd_requirements['preferred_skills']
            for skill in jd_skills:
                if skill.lower() in exp_text or skill.lower() in role:
                    relevance_score += 3
            
            if relevance_score > 6:  # Lowered for student internship-style experience sections
                relevant_experiences.append(exp)
                total_score += min(relevance_score, 40)
        
        # Normalize score
        if relevant_experiences:
            if jd_requirements.get('experience_years', 0) == 0:
                # For intern/fresher JDs, a relevant experience mention should not be under-scored.
                final_score = max(min(total_score, 100), 45)
            else:
                final_score = min(total_score, 100)
        else:
            # Has experience but not relevant
            final_score = 30
        
        details = {
            'relevant_count': len(relevant_experiences),
            'total_count': len(candidate_experience),
            'relevant_experience': relevant_experiences
        }
        
        return final_score, details
    
    def calculate_project_score(self, candidate_projects: List[Dict], 
                                jd_requirements: Dict) -> Tuple[float, Dict]:
        """
        Calculate project relevance score
        
        Returns:
            Tuple of (score, details_dict)
        """
        if not candidate_projects:
            return 20, {'relevant_count': 0, 'total_count': 0}
        
        jd_domain = jd_requirements['domain']
        domain_keywords = self.domain_keywords.get(jd_domain, {})
        jd_skills = jd_requirements['required_skills'] + jd_requirements['preferred_skills']
        
        relevant_projects = []
        total_score = 0
        
        for project in candidate_projects:
            proj_text = project.get('description', '').lower()
            title = project.get('title', '').lower() if project.get('title') else ''
            technologies = project.get('technologies', '').lower() if project.get('technologies') else ''
            
            relevance_score = 0
            
            # Check domain keywords
            for keyword in domain_keywords.get('required', []) + domain_keywords.get('bonus', []):
                if keyword in proj_text or keyword in title or keyword in technologies:
                    relevance_score += 4
            
            # Check skill matches
            for skill in jd_skills:
                if skill.lower() in proj_text or skill.lower() in title or skill.lower() in technologies:
                    relevance_score += 3
            
            if relevance_score > 4:
                relevant_projects.append(project)
                total_score += min(relevance_score, 30)

        if relevant_projects:
            # Avoid under-scoring strong but compact project descriptions common in student resumes.
            final_score = max(min(total_score, 100), 45)
        else:
            final_score = min(total_score, 100)
        
        details = {
            'relevant_count': len(relevant_projects),
            'total_count': len(candidate_projects),
            'relevant_projects': relevant_projects
        }
        
        return final_score, details
    
    def calculate_semantic_similarity(self, resume_text: str, jd_text: str) -> float:
        """
        Calculate semantic similarity between resume and JD using embeddings
        
        Returns:
            Similarity score (0-100)
        """
        try:
            # Generate embeddings
            # Use larger windows so key skills/experience farther in resume still influence similarity.
            resume_embedding = self.embedding_model.encode((resume_text or '')[:3000])
            jd_embedding = self.embedding_model.encode((jd_text or '')[:1800])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(
                resume_embedding.reshape(1, -1),
                jd_embedding.reshape(1, -1)
            )[0][0]
            
            # Convert to 0-100 scale
            return float(similarity * 100)
        
        except Exception as e:
            print(f"Error calculating semantic similarity: {e}")
            return 50  # Neutral score on error
    
    def check_domain_mismatch(self, candidate_skills: Dict[str, List[str]], 
                             jd_domain: str) -> Tuple[bool, float]:
        """
        Check for severe domain mismatch (e.g., mechanical student for data science)
        
        Returns:
            Tuple of (has_severe_mismatch, penalty_factor)
        """
        # Get candidate's primary domain
        candidate_domains = {domain: len(skills) 
                           for domain, skills in candidate_skills.items() 
                           if skills}
        
        if not candidate_domains:
            return False, 0  # No skills detected, no penalty
        
        primary_domain = max(candidate_domains, key=candidate_domains.get)
        
        # Check if completely unrelated
        domain_keywords = self.domain_keywords.get(jd_domain, {})
        related_domains = domain_keywords.get('related_domains', []) + [jd_domain]
        
        if primary_domain not in related_domains:
            # Check if it's a severe mismatch
            if jd_domain == 'project_management' and primary_domain in ['web_development', 'data_science', 'ai_ml']:
                return True, self.config['domain_mismatch_penalty']
            elif jd_domain in ['data_science', 'ai_ml'] and primary_domain == 'project_management':
                return True, self.config['domain_mismatch_penalty']
        
        return False, 0
    
    def calculate_overall_score(self, parsed_resume: Dict, jd_data: Dict,
                               cgpa_requirement: float, percentage_requirement: float,
                               candidate_profile: Optional[Dict] = None,
                               internship_constraints: Optional[Dict] = None) -> Dict:
        """
        Calculate overall matching score for candidate
        
        Args:
            parsed_resume: Parsed resume data from ResumeParser
            jd_data: Job description data
            cgpa_requirement: Minimum CGPA required
            percentage_requirement: Minimum percentage required
            
        Returns:
            Dictionary with comprehensive scoring results
        """
        # Extract JD requirements
        jd_requirements = self.extract_jd_requirements(jd_data['description'])
        candidate_profile = candidate_profile or {}
        candidate_batch_year = candidate_profile.get('batch_year')

        policy_eligible, policy_reason = self.evaluate_policy_eligibility(
            candidate_batch_year=candidate_batch_year,
            jd_requirements=jd_requirements,
            internship_constraints=internship_constraints
        )
        if not policy_eligible:
            return {
                'overall_score': 0.0,
                'is_shortlisted': False,
                'recommended_status': 'not_shortlisted',
                'cgpa_eligible': False,
                'reason': policy_reason,
                'detailed_scores': {
                    'cgpa': 0.0,
                    'skills': 0.0,
                    'experience': 0.0,
                    'projects': 0.0,
                    'semantic': 0.0,
                    'domain_alignment': 0.0,
                    'certification': 0.0
                },
                'match_details': {
                    'domain': jd_requirements['domain'],
                    'policy_eligible': False,
                    'policy_reason': policy_reason
                }
            }
        
        # 1. CGPA Eligibility Check (PRIMARY CRITERIA)
        candidate_cgpa = parsed_resume['academic'].get('cgpa', 0)
        candidate_percentage = parsed_resume['academic'].get('percentage', 0)
        cgpa_missing = not candidate_cgpa and not candidate_percentage
        
        cgpa_eligible, cgpa_score = self.check_cgpa_eligibility(
            candidate_cgpa, candidate_percentage,
            cgpa_requirement, percentage_requirement
        )
        
        # If strict mode and not eligible, return immediately
        if self.config['cgpa_threshold_strict'] and not cgpa_eligible and not cgpa_missing:
            return {
                'overall_score': 0,
                'is_shortlisted': False,
                'recommended_status': 'not_shortlisted',
                'cgpa_eligible': False,
                'reason': 'Does not meet minimum CGPA/Percentage requirement',
                'detailed_scores': {
                    'cgpa': cgpa_score,
                    'skills': 0,
                    'experience': 0,
                    'projects': 0,
                    'semantic': 0,
                    'domain_alignment': 0,
                    'certification': 0
                }
            }
        
        # 2. Domain Mismatch Check
        has_mismatch, penalty = self.check_domain_mismatch(
            parsed_resume['skills'],
            jd_requirements['domain']
        )

        # 3. Calculate individual scores (with conditional LLM enrichment)
        semantic_input = parsed_resume.get('sanitized_text') or parsed_resume.get('raw_text', '')
        semantic_score = self.calculate_semantic_similarity(
            semantic_input,
            jd_requirements['full_text']
        )
        skill_score, skill_details = self.calculate_skill_match_score(
            parsed_resume['skills'],
            jd_requirements
        )
        should_use_llm = (
            self.llm_client is not None and (
                semantic_score < 40
                or self._count_candidate_skills(parsed_resume.get('skills', {})) < 5
                or skill_details['required_matches'] == 0
                or len(parsed_resume.get('experience', [])) == 0
                or len(parsed_resume.get('projects', [])) == 0
            )
        )
        if should_use_llm:
            self._apply_llm_enrichment(parsed_resume, jd_requirements)
            skill_score, skill_details = self.calculate_skill_match_score(
                parsed_resume['skills'],
                jd_requirements
            )
        
        experience_score, exp_details = self.calculate_experience_score(
            parsed_resume['experience'],
            jd_requirements
        )

        project_score, proj_details = self.calculate_project_score(
            parsed_resume['projects'],
            jd_requirements
        )
        domain_alignment_score = self.calculate_domain_alignment_score(parsed_resume['skills'], jd_requirements)
        certification_score, cert_details = self.calculate_certification_score(
            parsed_resume.get('achievements', []),
            jd_requirements
        )

        # 4. Calculate weighted overall score
        weights = self.config['weights']

        overall_score = (
            cgpa_score * weights['cgpa'] +
            skill_score * weights['skills'] +
            experience_score * weights['experience'] +
            project_score * weights['projects'] +
            semantic_score * weights['semantic'] +
            domain_alignment_score * weights['domain_alignment'] +
            certification_score * weights['certification']
        )
        
        # Apply domain mismatch penalty
        if has_mismatch:
            overall_score *= (1 - penalty)
        
        # 5. Determine final status
        detailed_scores = {
            'cgpa': round(cgpa_score, 2),
            'skills': round(skill_score, 2),
            'experience': round(experience_score, 2),
            'projects': round(project_score, 2),
            'semantic': round(semantic_score, 2),
            'domain_alignment': round(domain_alignment_score, 2),
            'certification': round(certification_score, 2)
        }
        parse_confidence = float(parsed_resume.get('parse_confidence', 0.0) or 0.0)
        final_status, reason = self._decide_status(
            cgpa_eligible=cgpa_eligible,
            cgpa_missing=cgpa_missing,
            has_mismatch=has_mismatch,
            overall_score=overall_score,
            skill_details=skill_details,
            resume_text=semantic_input,
            jd_domain=jd_requirements['domain'],
            detailed_scores=detailed_scores,
            parse_confidence=parse_confidence
        )

        is_shortlisted = final_status == 'shortlisted'
        
        return {
            'overall_score': round(overall_score, 2),
            'is_shortlisted': is_shortlisted,
            'recommended_status': final_status,
            'cgpa_eligible': cgpa_eligible,
            'reason': reason,
            'detailed_scores': detailed_scores,
            'match_details': {
                'skills': skill_details,
                'experience': exp_details,
                'projects': proj_details,
                'certifications': cert_details,
                'domain': jd_requirements['domain'],
                'domain_mismatch': has_mismatch,
                'policy_eligible': policy_eligible,
                'policy_reason': policy_reason,
                'candidate_batch_year': candidate_batch_year
            }
        }
    
    def batch_shortlist(self, candidates: List[Dict], jd_data: Dict,
                       cgpa_requirement: float, percentage_requirement: float) -> List[Dict]:
        """
        Shortlist multiple candidates for a job
        
        Args:
            candidates: List of parsed resume dictionaries
            jd_data: Job description data
            cgpa_requirement: Minimum CGPA
            percentage_requirement: Minimum percentage
            
        Returns:
            List of candidates with scores, sorted by overall_score
        """
        results = []
        
        for candidate in candidates:
            try:
                score_result = self.calculate_overall_score(
                    candidate,
                    jd_data,
                    cgpa_requirement,
                    percentage_requirement
                )
                
                # Add candidate info
                score_result['candidate_name'] = candidate['personal_info'].get('name')
                score_result['candidate_email'] = candidate['personal_info'].get('email')
                score_result['candidate_cgpa'] = candidate['academic'].get('cgpa')
                
                results.append(score_result)
                
            except Exception as e:
                print(f"Error processing candidate {candidate.get('personal_info', {}).get('name')}: {e}")
                continue
        
        # Sort by overall score (descending)
        results.sort(key=lambda x: x['overall_score'], reverse=True)
        
        return results


