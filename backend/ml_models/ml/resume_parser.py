"""
Advanced Resume Parser using NLP
Extracts structured information from PDF resumes
Uses: spaCy, pdfplumber, sentence-transformers for semantic understanding
"""

import re
import pdfplumber
import spacy
from spacy.matcher import Matcher
from typing import Dict, List, Optional
from datetime import datetime
from .skill_normalizer import SkillNormalizer


class ResumeParser:
    """
    Advanced resume parser with NLP capabilities
    Extracts: Personal info, Education, Skills, Experience, Projects, Achievements
    """
    
    def __init__(self):
        """Initialize parser with NLP models"""
        # Load spaCy model (use en_core_web_lg for better accuracy)
        try:
            self.nlp = spacy.load("en_core_web_lg")
        except:
            # Fallback to smaller model
            self.nlp = spacy.load("en_core_web_sm")
        
        # Load sentence transformer for semantic similarity
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize matcher for pattern-based extraction
        self.matcher = Matcher(self.nlp.vocab)
        self._setup_patterns()
        
        self.skill_domains = self._load_skill_domains()

    def _load_skill_domains(self) -> Dict[str, List[str]]:
        import json
        from pathlib import Path
        base_dir = Path(__file__).resolve().parent / "skill_taxonomy"
        path = base_dir / "domains.json"
        with path.open("r", encoding="utf-8") as fh:
            raw = json.load(fh)
        domains = {}
        for key, data in raw.items():
            domain_skills = list(set((data.get("required", []) + data.get("bonus", []))))
            domains[key] = domain_skills
        return domains
    
    def _setup_patterns(self):
        """Setup regex and spaCy patterns for information extraction"""
        # Email pattern
        email_pattern = [{"TEXT": {"REGEX": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"}}]
        self.matcher.add("EMAIL", [email_pattern])
        
        # Phone pattern
        phone_pattern = [{"TEXT": {"REGEX": r"[\+\(]?[0-9][0-9 .\-\(\)]{8,}[0-9]"}}]
        self.matcher.add("PHONE", [phone_pattern])
        
        # CGPA pattern
        cgpa_pattern = [
            {"LOWER": {"IN": ["cgpa", "gpa", "cpi"]}},
            {"TEXT": {"REGEX": r"[:/-]?"}},
            {"TEXT": {"REGEX": r"\d+\.\d+"}}
        ]
        self.matcher.add("CGPA", [cgpa_pattern])
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def extract_email(self, text: str) -> Optional[str]:
        """Extract email address"""
        email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else None
    
    def extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number"""
        phone_pattern = r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]'
        phones = re.findall(phone_pattern, text)
        # Clean and return first phone number
        if phones:
            phone = re.sub(r'[^\d+]', '', phones[0])
            return phone if len(phone) >= 10 else None
        return None
    
    def extract_name(self, text: str) -> Optional[str]:
        """Extract candidate name using NER"""
        doc = self.nlp(text[:500])  # Check first 500 chars
        
        # Look for PERSON entities
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                # Basic validation - name should be 2-4 words
                name_parts = ent.text.split()
                if 2 <= len(name_parts) <= 4:
                    return ent.text
        
        # Fallback: First line often contains name
        first_line = text.split('\n')[0].strip()
        if len(first_line.split()) <= 4 and first_line[0].isupper():
            return first_line
        
        return None
    
    def extract_cgpa(self, text: str) -> Optional[float]:
        """Extract CGPA/GPA"""
        # Pattern: CGPA: 8.5, GPA 9.0, CGPA - 7.8, etc.
        cgpa_pattern = r'(?:cgpa|gpa|cpi)[\s:/-]*(\d+\.\d+)'
        matches = re.findall(cgpa_pattern, text.lower())
        
        if matches:
            cgpa = float(matches[0])
            # Validate CGPA range
            if 0 <= cgpa <= 10:
                return cgpa
        
        # Alternative pattern: standalone CGPA values
        standalone_pattern = r'\b(\d\.\d{1,2})\s*(?:cgpa|gpa|/\s*10)\b'
        matches = re.findall(standalone_pattern, text.lower())
        if matches:
            cgpa = float(matches[0])
            if 0 <= cgpa <= 10:
                return cgpa
        
        return None
    
    def extract_percentage(self, text: str, cgpa: Optional[float] = None) -> Optional[float]:
        """Extract or calculate percentage"""
        # Direct percentage pattern
        percentage_pattern = r'(\d{2,3})(?:\.\d+)?%|\b(\d{2,3})(?:\.\d+)?\s*(?:percent|percentage)\b'
        matches = re.findall(percentage_pattern, text.lower())
        
        if matches:
            for match in matches:
                percent = float(match[0] if match[0] else match[1])
                if 0 <= percent <= 100:
                    return percent
        
        # Calculate from CGPA if available
        if cgpa:
            return cgpa * 9.5  # Standard conversion
        
        return None
    
    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract skills and categorize by domain"""
        text_lower = text.lower()
        found_skills = {domain: [] for domain in self.skill_domains.keys()}
        found_skills['other'] = []
        
        # Extract skills by domain
        for domain, skills in self.skill_domains.items():
            for skill in skills:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills[domain].append(skill)
        
        # Extract additional skills from "Skills" section
        skills_section = self._extract_section(text, 'skills|tech skills|key skills|frameworks|languages')
        if skills_section:
            # Split by common delimiters
            skill_tokens = re.split(r'[,â€¢|;:\n]', skills_section)
            for token in skill_tokens:
                token = token.strip()
                if token and len(token.split()) <= 3:  # Likely a skill
                    # Check if already categorized
                    categorized = False
                    for domain_skills in found_skills.values():
                        if token.lower() in [s.lower() for s in domain_skills]:
                            categorized = True
                            break
                    if not categorized and len(token) > 2:
                        found_skills['other'].append(token)
        
        # Remove duplicates and empty lists, normalize
        normalized = {k: list(set(v)) for k, v in found_skills.items() if v}
        return SkillNormalizer.normalize_domains(normalized)
    
    def extract_education(self, text: str) -> List[Dict]:
        """Extract education details"""
        education = []
        
        # Extract education section
        edu_section = self._extract_section(text, 'education')
        if not edu_section:
            return education
        
        # Look for degree patterns
        degree_pattern = r'(?:B\.?Tech|B\.?E\.?|M\.?Tech|M\.?E\.?|Bachelor|Master|PhD|B\.?Sc|M\.?Sc)'
        degrees = re.findall(degree_pattern, edu_section, re.IGNORECASE)
        
        # Look for years
        year_pattern = r'(19|20)\d{2}'
        years = re.findall(year_pattern, edu_section)
        
        # Look for institutions (using NER)
        doc = self.nlp(edu_section)
        institutions = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
        
        # Combine information
        if degrees:
            for i, degree in enumerate(degrees):
                edu_entry = {
                    'degree': degree,
                    'institution': institutions[i] if i < len(institutions) else None,
                    'year': years[i] if i < len(years) else None
                }
                education.append(edu_entry)
        
        return education
    
    def extract_experience(self, text: str) -> List[Dict]:
        """Extract internship/work experience"""
        experiences = []
        
        # Extract experience section
        exp_section = self._extract_section(text, 'experience|internship|work')
        if not exp_section:
            return experiences
        
        # Split by common separators
        exp_blocks = re.split(r'\n\s*\n', exp_section)
        
        for block in exp_blocks:
            if len(block.strip()) < 20:  # Skip very short blocks
                continue
            
            # Extract company/organization
            doc = self.nlp(block[:200])
            companies = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
            
            # Extract dates
            date_pattern = r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}'
            dates = re.findall(date_pattern, block, re.IGNORECASE)
            
            # Extract role/position
            role_pattern = r'^([A-Z][A-Za-z\s]+(?:Intern|Developer|Engineer|Analyst|Manager))'
            role_match = re.search(role_pattern, block, re.MULTILINE)
            
            exp_entry = {
                'role': role_match.group(1).strip() if role_match else None,
                'company': companies[0] if companies else None,
                'duration': f"{dates[0]} - {dates[-1]}" if len(dates) >= 2 else None,
                'description': block.strip()
            }
            
            if exp_entry['role'] or exp_entry['company']:
                experiences.append(exp_entry)
        
        return experiences
    
    def extract_projects(self, text: str) -> List[Dict]:
        """Extract project details"""
        projects = []
        
        # Extract projects section
        proj_section = self._extract_section(text, 'project')
        if not proj_section:
            return projects
        
        # Split by project separators
        proj_blocks = re.split(r'\n\s*\n', proj_section)
        
        for block in proj_blocks:
            if len(block.strip()) < 30:
                continue
            
            # Extract project title (usually first line or bold text)
            lines = block.strip().split('\n')
            title = lines[0].strip() if lines else None
            
            # Extract technologies used
            tech_pattern = r'(?:technologies|tech stack|tools)[\s:]+([^\n]+)'
            tech_match = re.search(tech_pattern, block, re.IGNORECASE)
            technologies = tech_match.group(1).strip() if tech_match else None
            
            proj_entry = {
                'title': title,
                'technologies': technologies,
                'description': block.strip()
            }
            
            projects.append(proj_entry)
        
        return projects
    
    def extract_achievements(self, text: str) -> List[str]:
        """Extract achievements and certifications"""
        achievements = []
        
        # Extract achievements section
        ach_section = self._extract_section(text, 'achievement|certification|award|honor')
        if not ach_section:
            return achievements
        
        # Split by bullet points or newlines
        items = re.split(r'[â€¢\n]', ach_section)
        
        for item in items:
            item = item.strip()
            if len(item) > 10:  # Meaningful achievement
                achievements.append(item)
        
        return achievements
    
    def _extract_section(self, text: str, section_keywords: str) -> Optional[str]:
        """Extract specific section from resume (supports inline headers)"""
        # Capture text after header on same line + following lines until next header
        pattern = rf'(?:^|\n)\s*({section_keywords})[\s:]*([^\n]*)\n(.*?)(?=\n\s*(?:[A-Z][A-Za-z\s]+:|\Z))'

        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            inline = match.group(2).strip()
            body = match.group(3).strip()
            combined = "\n".join([s for s in [inline, body] if s])
            return combined.strip() if combined else None

        return None
    
    def calculate_domain_scores(self, skills: Dict[str, List[str]]) -> Dict[str, float]:
        """Calculate domain expertise scores based on skills"""
        domain_scores = {}
        
        for domain, skill_list in skills.items():
            if domain == 'other':
                continue
            
            # Score based on number of skills in domain
            total_skills = len(self.skill_domains.get(domain, []))
            found_skills = len(skill_list)
            
            if total_skills > 0:
                score = (found_skills / total_skills) * 100
                domain_scores[domain] = min(score, 100)  # Cap at 100
        
        return domain_scores
    
    def parse_resume(self, pdf_path: str) -> Dict:
        """
        Main method to parse resume and extract all information
        
        Args:
            pdf_path: Path to PDF resume file
            
        Returns:
            Dictionary with structured resume data
        """
        try:
            # Extract text
            text = self.extract_text_from_pdf(pdf_path)
            
            # Extract all information
            parsed_data = {
                'personal_info': {
                    'name': self.extract_name(text),
                    'email': self.extract_email(text),
                    'phone': self.extract_phone(text)
                },
                'academic': {
                    'cgpa': self.extract_cgpa(text),
                    'percentage': None,
                    'education': self.extract_education(text)
                },
                'skills': self.extract_skills(text),
                'experience': self.extract_experience(text),
                'projects': self.extract_projects(text),
                'achievements': self.extract_achievements(text),
                'raw_text': text
            }
            
            # Calculate percentage if CGPA available
            if parsed_data['academic']['cgpa']:
                parsed_data['academic']['percentage'] = self.extract_percentage(
                    text, parsed_data['academic']['cgpa']
                )
            else:
                parsed_data['academic']['percentage'] = self.extract_percentage(text)
            
            # Calculate domain expertise scores
            parsed_data['domain_scores'] = self.calculate_domain_scores(
                parsed_data['skills']
            )
            
            # Add metadata
            parsed_data['metadata'] = {
                'parsed_at': datetime.now().isoformat(),
                'parser_version': '1.0'
            }
            
            return parsed_data
            
        except Exception as e:
            raise Exception(f"Error parsing resume: {str(e)}")


