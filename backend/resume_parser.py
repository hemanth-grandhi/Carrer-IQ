"""
Enhanced Resume Parser Module
Extracts structured data from PDF and DOCX resume files
"""

import os
import re
from typing import Optional, Dict, List
import PyPDF2
from docx import Document


class ResumeParser:
    """Parse resume files and extract structured information"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.doc']
    
    def parse(self, file_path: str) -> Optional[str]:
        """
        Parse resume file and extract text
        
        Args:
            file_path: Path to the resume file
        
        Returns:
            Extracted text from resume, or None if parsing fails
        """
        if not os.path.exists(file_path):
            return None
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_ext == '.pdf':
                return self._parse_pdf(file_path)
            elif file_ext in ['.docx', '.doc']:
                return self._parse_docx(file_path)
            else:
                return None
        except Exception as e:
            print(f"Error parsing resume: {str(e)}")
            return None
    
    def parse_structured(self, file_path: str) -> Optional[Dict]:
        """
        Parse resume and extract structured data
        
        Args:
            file_path: Path to the resume file
        
        Returns:
            Dictionary with structured resume data
        """
        resume_text = self.parse(file_path)
        if not resume_text:
            return None
        
        return {
            "full_text": resume_text,
            "education": self._extract_education(resume_text),
            "experience": self._extract_experience(resume_text),
            "skills": self._extract_skills_section(resume_text),
            "projects": self._extract_projects(resume_text),
            "contact_info": self._extract_contact_info(resume_text)
        }
    
    def _parse_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error reading PDF: {str(e)}")
            raise
        return text.strip()
    
    def _parse_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        text = ""
        try:
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            print(f"Error reading DOCX: {str(e)}")
            raise
        return text.strip()
    
    def _extract_education(self, text: str) -> List[Dict]:
        """Extract education information"""
        education = []
        lines = text.split('\n')
        
        # Look for education section
        education_keywords = ['education', 'academic', 'qualification', 'degree', 'university', 'college']
        in_education_section = False
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Check if we're entering education section
            if any(keyword in line_lower for keyword in education_keywords) and len(line_lower) < 50:
                in_education_section = True
                continue
            
            # Extract degree/university information
            if in_education_section:
                # Look for degree patterns
                degree_patterns = [
                    r'\b(b\.?s\.?|b\.?a\.?|b\.?e\.?|m\.?s\.?|m\.?a\.?|m\.?e\.?|ph\.?d\.?|bachelor|master|doctorate)\b',
                    r'\b(bs|ba|be|ms|ma|me|phd|bsc|msc|btech|mtech)\b'
                ]
                
                if any(re.search(pattern, line_lower, re.IGNORECASE) for pattern in degree_patterns):
                    # Try to extract degree and institution
                    parts = line.split('|') if '|' in line else [line]
                    for part in parts:
                        part = part.strip()
                        if part and len(part) > 5:
                            education.append({
                                "degree": part,
                                "institution": self._extract_institution(lines, i),
                                "year": self._extract_year(part)
                            })
                            if len(education) >= 3:  # Limit to top 3
                                break
                    if len(education) >= 3:
                        break
        
        return education[:3] if education else [{"degree": "Not specified", "institution": "Not specified"}]
    
    def _extract_experience(self, text: str) -> List[Dict]:
        """Extract work experience"""
        experience = []
        lines = text.split('\n')
        
        # Look for experience section
        exp_keywords = ['experience', 'employment', 'work history', 'career', 'professional']
        in_exp_section = False
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Check if we're entering experience section
            if any(keyword in line_lower for keyword in exp_keywords) and len(line_lower) < 50:
                in_exp_section = True
                continue
            
            # Look for job title patterns
            if in_exp_section:
                job_title_patterns = [
                    r'\b(software engineer|developer|analyst|manager|engineer|consultant|intern|associate)\b',
                    r'\b(sde|swe|qa|devops|data scientist|product manager)\b'
                ]
                
                if any(re.search(pattern, line_lower, re.IGNORECASE) for pattern in job_title_patterns):
                    if len(line.strip()) > 5 and len(line.strip()) < 100:
                        experience.append({
                            "title": line.strip(),
                            "company": self._extract_company(lines, i),
                            "duration": self._extract_duration(line),
                            "description": self._extract_description(lines, i)
                        })
                        if len(experience) >= 5:  # Limit to top 5
                            break
        
        return experience[:5] if experience else [{"title": "Not specified", "company": "Not specified"}]
    
    def _extract_skills_section(self, text: str) -> List[str]:
        """Extract skills from skills section"""
        skills = []
        lines = text.split('\n')
        
        # Look for skills section
        skills_keywords = ['skills', 'technical skills', 'competencies', 'expertise', 'proficiencies']
        in_skills_section = False
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            if any(keyword in line_lower for keyword in skills_keywords) and len(line_lower) < 50:
                in_skills_section = True
                continue
            
            if in_skills_section:
                # Extract skills (comma or pipe separated, or bullet points)
                if line.strip():
                    # Split by common delimiters
                    line_skills = re.split(r'[,|•\-\n]', line)
                    for skill in line_skills:
                        skill = skill.strip()
                        if skill and len(skill) > 2 and len(skill) < 50:
                            skills.append(skill)
                            if len(skills) >= 20:  # Limit
                                break
                if len(skills) >= 20 or (in_skills_section and i > 10):  # Stop after 10 lines
                    break
        
        return skills[:20] if skills else []
    
    def _extract_projects(self, text: str) -> List[Dict]:
        """Extract projects"""
        projects = []
        lines = text.split('\n')
        
        # Look for projects section
        project_keywords = ['projects', 'project', 'portfolio', 'work samples']
        in_project_section = False
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            if any(keyword in line_lower for keyword in project_keywords) and len(line_lower) < 50:
                in_project_section = True
                continue
            
            if in_project_section:
                if line.strip() and len(line.strip()) > 10:
                    # Check if it looks like a project title
                    if not line.strip()[0].isdigit() and len(line.strip()) < 100:
                        projects.append({
                            "name": line.strip(),
                            "description": self._extract_description(lines, i)
                        })
                        if len(projects) >= 5:  # Limit to top 5
                            break
        
        return projects[:5] if projects else []
    
    def _extract_contact_info(self, text: str) -> Dict:
        """Extract contact information"""
        contact = {
            "email": self._extract_email(text),
            "phone": self._extract_phone(text),
            "location": self._extract_location(text)
        }
        return contact
    
    def _extract_email(self, text: str) -> str:
        """Extract email address"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        return matches[0] if matches else "Not found"
    
    def _extract_phone(self, text: str) -> str:
        """Extract phone number"""
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            r'\b\(\d{3}\)\s?\d{3}[-.]?\d{4}\b',
            r'\b\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b'
        ]
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0]
        return "Not found"
    
    def _extract_location(self, text: str) -> str:
        """Extract location"""
        # Simple extraction - look for city, state patterns
        location_pattern = r'\b[A-Z][a-z]+,\s*[A-Z]{2}\b'
        matches = re.findall(location_pattern, text)
        return matches[0] if matches else "Not found"
    
    def _extract_institution(self, lines: List[str], index: int) -> str:
        """Extract institution name from nearby lines"""
        for i in range(max(0, index-2), min(len(lines), index+3)):
            line = lines[i].strip()
            if line and len(line) > 3:
                # Check if it looks like an institution
                if any(word in line.lower() for word in ['university', 'college', 'institute', 'school']):
                    return line
        return "Not specified"
    
    def _extract_company(self, lines: List[str], index: int) -> str:
        """Extract company name from nearby lines"""
        for i in range(max(0, index-1), min(len(lines), index+2)):
            line = lines[i].strip()
            if line and len(line) > 2 and len(line) < 50:
                return line
        return "Not specified"
    
    def _extract_year(self, text: str) -> str:
        """Extract year"""
        year_pattern = r'\b(19|20)\d{2}\b'
        matches = re.findall(year_pattern, text)
        if matches:
            # Get the full year
            full_years = re.findall(r'\b(19|20)\d{2}\b', text)
            return full_years[0] if full_years else "Not specified"
        return "Not specified"
    
    def _extract_duration(self, text: str) -> str:
        """Extract duration/date range"""
        duration_patterns = [
            r'\b\d{4}\s*[-–]\s*\d{4}\b',
            r'\b\d{4}\s*[-–]\s*(present|current|now)\b',
            r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4}\s*[-–]'
        ]
        for pattern in duration_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches[0] if isinstance(matches[0], str) else text[matches[0].span()[0]:matches[0].span()[1]]
        return "Not specified"
    
    def _extract_description(self, lines: List[str], index: int) -> str:
        """Extract description from following lines"""
        description = []
        for i in range(index+1, min(len(lines), index+4)):
            line = lines[i].strip()
            if line and len(line) > 10:
                description.append(line)
                if len(description) >= 2:
                    break
        return " | ".join(description) if description else "Not specified"
