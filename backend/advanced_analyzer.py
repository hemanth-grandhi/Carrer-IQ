"""
Advanced Resume Analyzer
Performs deep resume understanding beyond keyword matching
Uses multi-model AI strategy for intelligent analysis
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from ai_service import AIService


class AdvancedResumeAnalyzer:
    """Advanced resume analysis with deep understanding"""
    
    # Industry-standard role requirements
    ROLE_REQUIREMENTS = {
        "Software Engineer": {
            "fundamentals": {
                "high": ["Data Structures", "Algorithms", "OOP", "System Design"],
                "medium": ["Database Design", "Operating Systems", "Computer Networks"],
                "low": ["Software Testing", "Version Control", "CI/CD"]
            },
            "skills": {
                "high": ["Programming Languages", "Problem Solving", "Code Quality"],
                "medium": ["API Development", "Database Management", "Git"],
                "low": ["Documentation", "Code Review", "Agile"]
            },
            "experience_indicators": {
                "fresher": ["internship", "project", "academic", "course"],
                "junior": ["1-2 years", "entry level", "associate"],
                "mid": ["3-5 years", "mid-level", "experienced"],
                "senior": ["5+ years", "senior", "lead", "architect"]
            }
        },
        "Backend Developer": {
            "fundamentals": {
                "high": ["API Design", "Database Systems", "System Architecture", "Security"],
                "medium": ["Microservices", "Caching", "Message Queues", "REST/GraphQL"],
                "low": ["DevOps Basics", "Monitoring", "Logging"]
            },
            "skills": {
                "high": ["Backend Frameworks", "Database Optimization", "API Development"],
                "medium": ["Authentication", "Authorization", "API Security"],
                "low": ["Documentation", "Testing", "Performance Tuning"]
            }
        },
        "Frontend Developer": {
            "fundamentals": {
                "high": ["JavaScript", "HTML/CSS", "React/Vue/Angular", "Responsive Design"],
                "medium": ["State Management", "Web Performance", "Browser APIs"],
                "low": ["Testing", "Accessibility", "SEO"]
            },
            "skills": {
                "high": ["Frontend Frameworks", "UI/UX", "JavaScript ES6+"],
                "medium": ["Build Tools", "Package Managers", "CSS Preprocessors"],
                "low": ["Progressive Web Apps", "WebAssembly", "Design Systems"]
            }
        },
        "Data Scientist": {
            "fundamentals": {
                "high": ["Statistics", "Machine Learning", "Data Analysis", "Python/R"],
                "medium": ["Data Visualization", "SQL", "Data Cleaning", "Feature Engineering"],
                "low": ["Big Data Tools", "Cloud Platforms", "MLOps"]
            },
            "skills": {
                "high": ["Pandas", "NumPy", "Scikit-learn", "Jupyter"],
                "medium": ["TensorFlow/PyTorch", "Data Visualization", "SQL"],
                "low": ["Spark", "Docker", "Kubernetes"]
            }
        },
        "ML Engineer": {
            "fundamentals": {
                "high": ["Machine Learning", "Deep Learning", "Model Deployment", "Python"],
                "medium": ["MLOps", "Model Optimization", "Data Pipelines"],
                "low": ["Cloud ML Services", "Containerization", "Monitoring"]
            },
            "skills": {
                "high": ["TensorFlow", "PyTorch", "Model Training", "Feature Engineering"],
                "medium": ["Model Deployment", "MLOps", "Data Processing"],
                "low": ["Kubernetes", "Monitoring", "A/B Testing"]
            }
        }
    }
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
    
    def analyze_resume(
        self, 
        resume_text: str, 
        job_description: str,
        resume_skills: List[str],
        job_skills: List[str]
    ) -> Dict[str, Any]:
        """
        Perform deep resume analysis
        
        Returns comprehensive analysis with:
        - Role intent detection
        - Experience level assessment
        - Strength areas
        - Weak areas
        - Missing fundamentals
        - Resume structure quality
        """
        # Detect target role
        target_role = self._detect_role(job_description)
        
        # Assess experience level
        experience_level = self._assess_experience_level(resume_text, target_role)
        
        # Analyze strengths
        strengths = self._analyze_strengths(resume_text, resume_skills, target_role)
        
        # Analyze weaknesses
        weaknesses = self._analyze_weaknesses(resume_text, resume_skills, target_role, job_skills)
        
        # Identify missing fundamentals
        missing_fundamentals = self._identify_missing_fundamentals(
            resume_text, resume_skills, target_role
        )
        
        # Assess resume structure quality
        structure_quality = self._assess_resume_structure(resume_text)
        
        # Get AI-powered deep analysis
        ai_insights = self._get_ai_insights(resume_text, job_description, target_role)
        
        # Calculate role readiness score
        role_readiness = self._calculate_role_readiness(
            strengths, weaknesses, missing_fundamentals, target_role
        )
        
        return {
            "target_role": target_role,
            "experience_level": experience_level,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "missing_fundamentals": missing_fundamentals,
            "resume_structure": structure_quality,
            "role_readiness_score": role_readiness,
            "ai_insights": ai_insights,
            "confidence": self._calculate_confidence(resume_text, job_description)
        }
    
    def _detect_role(self, job_description: str) -> str:
        """Detect target role from job description"""
        job_lower = job_description.lower()
        
        role_patterns = {
            "Backend Developer": [
                "backend", "back-end", "server", "api developer", 
                "rest api", "microservices", "database"
            ],
            "Frontend Developer": [
                "frontend", "front-end", "react", "vue", "angular",
                "ui developer", "javascript developer"
            ],
            "Data Scientist": [
                "data scientist", "data science", "machine learning",
                "data analysis", "statistics"
            ],
            "ML Engineer": [
                "ml engineer", "machine learning engineer", "deep learning",
                "model deployment", "mlops"
            ],
            "Software Engineer": [
                "software engineer", "sde", "swe", "software developer",
                "full stack", "fullstack"
            ]
        }
        
        for role, patterns in role_patterns.items():
            if any(pattern in job_lower for pattern in patterns):
                return role
        
        return "Software Engineer"  # Default
    
    def _assess_experience_level(
        self, 
        resume_text: str, 
        target_role: str
    ) -> Dict[str, Any]:
        """Assess candidate's experience level"""
        resume_lower = resume_text.lower()
        
        # Check for years of experience
        years_pattern = r'(\d+)\+?\s*(?:years?|yrs?|yr)'
        years_matches = re.findall(years_pattern, resume_lower)
        total_years = 0
        if years_matches:
            total_years = max([int(y) for y in years_matches])
        
        # Check for experience indicators
        level_indicators = {
            "fresher": ["intern", "internship", "student", "graduate", "fresher", "entry level"],
            "junior": ["junior", "associate", "1 year", "2 years"],
            "mid": ["mid-level", "3 years", "4 years", "5 years", "experienced"],
            "senior": ["senior", "lead", "architect", "principal", "6+ years", "7+ years"]
        }
        
        detected_level = "mid"  # Default
        for level, indicators in level_indicators.items():
            if any(indicator in resume_lower for indicator in indicators):
                detected_level = level
                break
        
        # Override with years if available
        if total_years == 0:
            detected_level = "fresher"
        elif total_years <= 2:
            detected_level = "junior"
        elif total_years <= 5:
            detected_level = "mid"
        else:
            detected_level = "senior"
        
        return {
            "level": detected_level,
            "years_experience": total_years,
            "description": self._get_experience_description(detected_level)
        }
    
    def _get_experience_description(self, level: str) -> str:
        descriptions = {
            "fresher": "Entry-level candidate with limited professional experience",
            "junior": "Early-career professional with 1-2 years of experience",
            "mid": "Mid-level professional with 3-5 years of experience",
            "senior": "Experienced professional with 5+ years of expertise"
        }
        return descriptions.get(level, "Professional candidate")
    
    def _analyze_strengths(
        self, 
        resume_text: str, 
        resume_skills: List[str],
        target_role: str
    ) -> Dict[str, Any]:
        """Analyze candidate's strengths"""
        role_reqs = self.ROLE_REQUIREMENTS.get(target_role, self.ROLE_REQUIREMENTS["Software Engineer"])
        resume_lower = resume_text.lower()
        
        strengths = {
            "technical_skills": [],
            "fundamentals": [],
            "experience_highlights": [],
            "projects": []
        }
        
        # Check for required fundamentals
        for priority in ["high", "medium", "low"]:
            for fundamental in role_reqs["fundamentals"].get(priority, []):
                if fundamental.lower() in resume_lower:
                    strengths["fundamentals"].append({
                        "skill": fundamental,
                        "priority": priority,
                        "evidence": self._find_evidence(resume_text, fundamental)
                    })
        
        # Check for required skills
        for priority in ["high", "medium", "low"]:
            for skill in role_reqs["skills"].get(priority, []):
                if any(s.lower() in resume_lower for s in [skill] + resume_skills):
                    strengths["technical_skills"].append({
                        "skill": skill,
                        "priority": priority
                    })
        
        # Extract experience highlights
        strengths["experience_highlights"] = self._extract_experience_highlights(resume_text)
        
        # Extract projects
        strengths["projects"] = self._extract_projects(resume_text)
        
        return strengths
    
    def _analyze_weaknesses(
        self,
        resume_text: str,
        resume_skills: List[str],
        target_role: str,
        job_skills: List[str]
    ) -> Dict[str, Any]:
        """Analyze candidate's weaknesses and gaps"""
        role_reqs = self.ROLE_REQUIREMENTS.get(target_role, self.ROLE_REQUIREMENTS["Software Engineer"])
        resume_lower = resume_text.lower()
        
        weaknesses = {
            "missing_fundamentals": [],
            "missing_skills": [],
            "skill_gaps": [],
            "improvement_areas": []
        }
        
        # Check missing fundamentals
        for priority in ["high", "medium", "low"]:
            for fundamental in role_reqs["fundamentals"].get(priority, []):
                if fundamental.lower() not in resume_lower:
                    weaknesses["missing_fundamentals"].append({
                        "skill": fundamental,
                        "priority": priority,
                        "importance": "Critical" if priority == "high" else "Important" if priority == "medium" else "Nice to have"
                    })
        
        # Check missing job-specific skills
        resume_skills_lower = {s.lower() for s in resume_skills}
        for job_skill in job_skills:
            if job_skill.lower() not in resume_skills_lower:
                weaknesses["missing_skills"].append({
                    "skill": job_skill,
                    "priority": "high" if job_skill.lower() in str(role_reqs).lower() else "medium"
                })
        
        # Identify improvement areas
        weaknesses["improvement_areas"] = self._identify_improvement_areas(resume_text, target_role)
        
        return weaknesses
    
    def _identify_missing_fundamentals(
        self,
        resume_text: str,
        resume_skills: List[str],
        target_role: str
    ) -> List[Dict[str, Any]]:
        """Identify missing fundamental skills"""
        role_reqs = self.ROLE_REQUIREMENTS.get(target_role, self.ROLE_REQUIREMENTS["Software Engineer"])
        resume_lower = resume_text.lower()
        
        missing = []
        for priority in ["high", "medium", "low"]:
            for fundamental in role_reqs["fundamentals"].get(priority, []):
                if fundamental.lower() not in resume_lower:
                    missing.append({
                        "skill": fundamental,
                        "priority": priority,
                        "impact": "High" if priority == "high" else "Medium" if priority == "medium" else "Low",
                        "why_important": self._get_why_important(fundamental, target_role)
                    })
        
        return missing
    
    def _get_why_important(self, skill: str, role: str) -> str:
        """Explain why a skill is important"""
        explanations = {
            "Data Structures": "Essential for solving coding problems efficiently",
            "Algorithms": "Core requirement for technical interviews and problem-solving",
            "System Design": "Critical for designing scalable systems",
            "OOP": "Fundamental programming paradigm used in all modern languages",
            "API Design": "Core skill for backend development",
            "Database Systems": "Essential for data persistence and management",
            "JavaScript": "Foundation of modern web development",
            "React/Vue/Angular": "Industry-standard frontend frameworks",
            "Machine Learning": "Core requirement for ML roles",
            "Python": "Primary language for data science and ML"
        }
        return explanations.get(skill, f"Important skill for {role} role")
    
    def _assess_resume_structure(self, resume_text: str) -> Dict[str, Any]:
        """Assess resume structure quality"""
        sections = {
            "summary": bool(re.search(r'(summary|objective|profile)', resume_text, re.IGNORECASE)),
            "experience": bool(re.search(r'(experience|work history|employment)', resume_text, re.IGNORECASE)),
            "education": bool(re.search(r'(education|academic|qualification)', resume_text, re.IGNORECASE)),
            "skills": bool(re.search(r'(skills?|technical skills?|competencies)', resume_text, re.IGNORECASE)),
            "projects": bool(re.search(r'(projects?|portfolio)', resume_text, re.IGNORECASE))
        }
        
        score = sum(sections.values()) / len(sections) * 100
        
        issues = []
        if not sections["summary"]:
            issues.append("Missing summary/objective section")
        if not sections["skills"]:
            issues.append("Missing dedicated skills section")
        if not sections["projects"]:
            issues.append("No projects section found")
        
        return {
            "score": round(score, 1),
            "sections_present": sections,
            "issues": issues,
            "quality": "Excellent" if score >= 80 else "Good" if score >= 60 else "Needs Improvement"
        }
    
    def _get_ai_insights(
        self, 
        resume_text: str, 
        job_description: str,
        target_role: str
    ) -> Dict[str, Any]:
        """Get AI-powered deep insights"""
        if not self.ai_service:
            return {}
        
        # Check if AI is enabled
        ai_enabled = getattr(self.ai_service, 'ai_enabled', False) or (
            getattr(self.ai_service, 'hf_available', False) or 
            getattr(self.ai_service, 'gemini_available', False)
        )
        
        if not ai_enabled:
            return {}
        
        prompt = f"""Analyze this resume for a {target_role} position and provide deep insights.

RESUME:
{resume_text[:2500]}

JOB DESCRIPTION:
{job_description[:2000]}

Provide JSON response with:
1. role_fit: How well the candidate fits the role (1-10 scale)
2. key_strengths: Top 3-5 unique strengths
3. critical_gaps: Top 3-5 critical skill gaps
4. experience_assessment: Assessment of experience level and quality
5. resume_quality_score: Resume structure and presentation quality (1-10)
6. specific_recommendations: 3-5 specific, actionable recommendations

Format as JSON only, no markdown."""
        
        try:
            ai_response = self.ai_service._call_ai(prompt, task="analysis")
            return ai_response if isinstance(ai_response, dict) else {}
        except:
            return {}
    
    def _calculate_role_readiness(
        self,
        strengths: Dict,
        weaknesses: Dict,
        missing_fundamentals: List,
        target_role: str
    ) -> Dict[str, Any]:
        """Calculate role readiness score"""
        # Base score
        base_score = 50
        
        # Add points for strengths
        strength_bonus = min(len(strengths.get("fundamentals", [])) * 5, 25)
        skill_bonus = min(len(strengths.get("technical_skills", [])) * 3, 15)
        
        # Subtract points for critical gaps
        critical_penalty = len([m for m in missing_fundamentals if m.get("priority") == "high"]) * 10
        medium_penalty = len([m for m in missing_fundamentals if m.get("priority") == "medium"]) * 5
        
        score = base_score + strength_bonus + skill_bonus - critical_penalty - medium_penalty
        score = max(0, min(100, score))
        
        return {
            "score": round(score, 1),
            "level": self._get_readiness_level(score),
            "breakdown": {
                "base": base_score,
                "strength_bonus": strength_bonus,
                "skill_bonus": skill_bonus,
                "critical_penalty": -critical_penalty,
                "medium_penalty": -medium_penalty
            }
        }
    
    def _get_readiness_level(self, score: float) -> str:
        """Get readiness level description"""
        if score >= 80:
            return "Highly Ready"
        elif score >= 60:
            return "Ready with Minor Gaps"
        elif score >= 40:
            return "Needs Improvement"
        else:
            return "Significant Gaps"
    
    def _calculate_confidence(self, resume_text: str, job_description: str) -> float:
        """Calculate confidence in analysis"""
        # More text = higher confidence
        text_length_score = min(len(resume_text) / 1000, 1.0) * 30
        job_length_score = min(len(job_description) / 500, 1.0) * 20
        
        # AI service availability
        ai_score = 50 if (self.ai_service and self.ai_service.ai_enabled) else 30
        
        return min(100, text_length_score + job_length_score + ai_score)
    
    def _find_evidence(self, resume_text: str, skill: str) -> str:
        """Find evidence of skill in resume"""
        lines = resume_text.split('\n')
        for i, line in enumerate(lines):
            if skill.lower() in line.lower():
                # Get context
                context = ' '.join(lines[max(0, i-1):min(len(lines), i+2)])
                return context[:100] + "..."
        return "Mentioned in resume"
    
    def _extract_experience_highlights(self, resume_text: str) -> List[str]:
        """Extract experience highlights"""
        highlights = []
        # Look for quantified achievements
        pattern = r'(?:increased|improved|reduced|built|developed|managed|led).*?(?:\d+%|\d+\s*(?:users|projects|team))'
        matches = re.findall(pattern, resume_text, re.IGNORECASE)
        return matches[:5]
    
    def _extract_projects(self, resume_text: str) -> List[Dict]:
        """Extract project information"""
        projects = []
        # Simple extraction - can be enhanced
        project_section = re.search(r'projects?[:\n](.*?)(?:\n\n|\n[A-Z])', resume_text, re.IGNORECASE | re.DOTALL)
        if project_section:
            project_text = project_section.group(1)
            # Split by lines
            for line in project_text.split('\n')[:5]:
                if line.strip() and len(line.strip()) > 10:
                    projects.append({"name": line.strip(), "description": ""})
        return projects
    
    def _identify_improvement_areas(self, resume_text: str, target_role: str) -> List[str]:
        """Identify areas for improvement"""
        areas = []
        resume_lower = resume_text.lower()
        
        # Check for common issues
        if not re.search(r'\d+%|\d+\s*(?:users|projects)', resume_lower):
            areas.append("Add quantified achievements (metrics, numbers)")
        
        if len(resume_text.split()) < 200:
            areas.append("Resume is too short - add more detail")
        
        if not re.search(r'(github|git|portfolio)', resume_lower):
            areas.append("Add links to GitHub or portfolio")
        
        return areas

