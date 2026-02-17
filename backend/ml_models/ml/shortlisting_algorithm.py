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
                'cgpa': 0.30,          # 30% weight to CGPA
                'skills': 0.25,        # 25% weight to skills matching
                'experience': 0.20,    # 20% weight to experience
                'projects': 0.15,      # 15% weight to projects
                'semantic': 0.10       # 10% weight to semantic similarity
            },
            'cgpa_threshold_strict': True,  # If True, reject below threshold immediately
            'min_skill_match': 2,           # Minimum matching skills required
            'domain_mismatch_penalty': 0.3  # Penalty for domain mismatch
        }
        
        self.domain_keywords = self._load_domain_keywords()

    def _load_domain_keywords(self) -> Dict[str, Dict[str, List[str]]]:
        base_dir = Path(__file__).resolve().parent / "skill_taxonomy"
        path = base_dir / "domains.json"
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    
    def extract_jd_requirements(self, jd_text: str) -> Dict:
        """
        Extract key requirements from job description
        
        Args:
            jd_text: Job description text
            
        Returns:
            Dictionary with extracted requirements
        """
        jd_lower = jd_text.lower()
        
        # Detect domain/role
        detected_domain = self._detect_domain(jd_text)
        
        # Extract required skills (look for "required", "must have" sections)
        required_skills = self._extract_skills_from_text(jd_text, section_keywords=['required', 'must have'])
        
        # Extract preferred skills
        preferred_skills = self._extract_skills_from_text(jd_text, section_keywords=['preferred', 'nice to have', 'bonus'])
        
        # Extract experience requirements
        experience_years = self._extract_experience_requirement(jd_text)
        
        # Extract education requirements
        education_req = self._extract_education_requirement(jd_text)
        
        return {
            'domain': detected_domain,
            'required_skills': required_skills,
            'preferred_skills': preferred_skills,
            'experience_years': experience_years,
            'education': education_req,
            'full_text': jd_text
        }
    
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
        skills = []
        text_lower = text.lower()
        
        # Look for section with keywords
        for keyword in section_keywords:
            pattern = rf'{keyword}[\s:]+([^\n]+(?:\n[^\n]+)*?)(?=\n\s*\n|\Z)'
            matches = re.findall(pattern, text_lower, re.IGNORECASE | re.DOTALL)
            
            for match in matches:
                # Split by common delimiters
                tokens = re.split(r'[,â€¢|;:\n]', match)
                for token in tokens:
                    token = token.strip()
                    if token and len(token.split()) <= 4:
                        skills.append(token)
        
        # If no section found, extract from entire text
        if not skills:
            # Look for common tech keywords
            common_skills = ['python', 'java', 'javascript', 'c++', 'react', 'angular', 
                           'node', 'django', 'sql', 'aws', 'docker', 'git']
            for skill in common_skills:
                if skill in text_lower:
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
        required_matches = sum(1 for skill in required_skills 
                              if any(skill in cs or cs in skill for cs in all_candidate_skills))
        preferred_matches = sum(1 for skill in preferred_skills 
                               if any(skill in cs or cs in skill for cs in all_candidate_skills))
        
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
            'matched_skills': [s for s in all_candidate_skills 
                              if any(req in s or s in req for req in required_skills + preferred_skills)]
        }
        
        return min(total_score, 100), details
    
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
            
            if relevance_score > 10:  # Threshold for relevance
                relevant_experiences.append(exp)
                total_score += min(relevance_score, 40)
        
        # Normalize score
        if relevant_experiences:
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
            
            if relevance_score > 5:
                relevant_projects.append(project)
                total_score += min(relevance_score, 30)
        
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
            resume_embedding = self.embedding_model.encode(resume_text[:1000])  # First 1000 chars
            jd_embedding = self.embedding_model.encode(jd_text[:1000])
            
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
                               cgpa_requirement: float, percentage_requirement: float) -> Dict:
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
                'cgpa_eligible': False,
                'reason': 'Does not meet minimum CGPA/Percentage requirement',
                'detailed_scores': {
                    'cgpa': cgpa_score,
                    'skills': 0,
                    'experience': 0,
                    'projects': 0,
                    'semantic': 0
                }
            }
        
        # 2. Domain Mismatch Check
        has_mismatch, penalty = self.check_domain_mismatch(
            parsed_resume['skills'],
            jd_requirements['domain']
        )

        # 3. Calculate individual scores (with conditional LLM enrichment)
        semantic_score = self.calculate_semantic_similarity(
            parsed_resume['raw_text'],
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
        
        # 4. Calculate weighted overall score
        weights = self.config['weights']
        
        overall_score = (
            cgpa_score * weights['cgpa'] +
            skill_score * weights['skills'] +
            experience_score * weights['experience'] +
            project_score * weights['projects'] +
            semantic_score * weights['semantic']
        )
        
        # Apply domain mismatch penalty
        if has_mismatch:
            overall_score *= (1 - penalty)
        
        # 5. Determine shortlisting decision
        # Minimum thresholds
        min_skill_matches = skill_details['required_matches'] >= self.config['min_skill_match']
        min_overall_score = overall_score >= 50  # 50% threshold
        
        is_shortlisted = cgpa_eligible and min_skill_matches and min_overall_score
        
        # Generate reason
        if is_shortlisted:
            reason = "Candidate meets all criteria"
        elif not cgpa_eligible and not cgpa_missing:
            reason = "Does not meet CGPA/Percentage requirement"
        elif cgpa_missing:
            reason = "Academic score missing; soft-scored using other criteria"
        elif not min_skill_matches:
            reason = f"Insufficient skill matches (found {skill_details['required_matches']}, need {self.config['min_skill_match']})"
        elif has_mismatch:
            reason = "Severe domain mismatch detected"
        else:
            reason = f"Overall score too low ({overall_score:.1f}%)"
        
        return {
            'overall_score': round(overall_score, 2),
            'is_shortlisted': is_shortlisted,
            'cgpa_eligible': cgpa_eligible,
            'reason': reason,
            'detailed_scores': {
                'cgpa': round(cgpa_score, 2),
                'skills': round(skill_score, 2),
                'experience': round(experience_score, 2),
                'projects': round(project_score, 2),
                'semantic': round(semantic_score, 2)
            },
            'match_details': {
                'skills': skill_details,
                'experience': exp_details,
                'projects': proj_details,
                'domain': jd_requirements['domain'],
                'domain_mismatch': has_mismatch
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


