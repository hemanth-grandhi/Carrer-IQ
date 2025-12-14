"""
AI Service Module
Uses FREE-TIER APIs only: Hugging Face Inference API and Google Gemini
Provides fallback logic between providers
"""

import os
import requests
import json
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AIService:
    """AI service using free-tier APIs with fallback support"""
    
    def __init__(self):
        # API Keys from environment variables
        self.hf_api_key = os.getenv("HUGGINGFACE_API_KEY", "")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        
        # Hugging Face API endpoint (free tier)
        self.hf_api_url = "https://api-inference.huggingface.co/models"
        
        # Model preferences (free models)
        self.hf_models = {
            "chat": "mistralai/Mistral-7B-Instruct-v0.2",  # Free inference model
            "fallback_chat": "meta-llama/Llama-2-7b-chat-hf",  # Alternative free model
            "analysis": "mistralai/Mistral-7B-Instruct-v0.2"
        }
        
        # Provider availability
        self.hf_available = bool(self.hf_api_key)
        self.gemini_available = bool(self.gemini_api_key)
        self.ai_enabled = self.hf_available or self.gemini_available
        
        print(f"AI Service initialized - HF: {self.hf_available}, Gemini: {self.gemini_available}, AI Enabled: {self.ai_enabled}")
    
    def analyze_resume(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """
        Analyze resume and provide AI-powered insights
        
        Args:
            resume_text: Full resume text
            job_description: Job description text
        
        Returns:
            Dictionary with AI analysis
        """
        prompt = f"""Analyze this resume against the job description and provide insights.

RESUME:
{resume_text[:2000]}

JOB DESCRIPTION:
{job_description[:2000]}

Provide a JSON response with:
1. overall_assessment: Brief assessment of the match
2. strengths: List of 3-5 key strengths
3. weaknesses: List of 3-5 key weaknesses
4. skill_gaps: List of missing critical skills
5. improvement_suggestions: List of 3-5 actionable suggestions

Format as JSON only, no markdown."""
        
        return self._call_ai(prompt, task="analysis")
    
    def get_role_recommendations(self, resume_text: str, target_role: str = None) -> Dict[str, Any]:
        """
        Get role-based skill recommendations
        
        Args:
            resume_text: Resume text
            target_role: Target role (e.g., "Software Engineer", "Data Scientist")
        
        Returns:
            Role-specific recommendations
        """
        if not target_role:
            # Auto-detect role from resume
            target_role = "Software Engineer"  # Default
        
        prompt = f"""Based on this resume, provide role-specific skill recommendations for a {target_role} position.

RESUME:
{resume_text[:2000]}

Provide JSON response with:
1. recommended_skills: List of 5-7 skills to learn/improve
2. learning_priority: Priority order (high/medium/low) for each skill
3. skill_explanations: Brief explanation why each skill is important
4. learning_resources: Suggested free resources for each skill

Format as JSON only, no markdown."""
        
        return self._call_ai(prompt, task="recommendations")
    
    def generate_learning_roadmap(self, missing_skills: List[str], target_role: str) -> Dict[str, Any]:
        """
        Generate a learning roadmap for missing skills
        
        Args:
            missing_skills: List of missing skills
            target_role: Target role
        
        Returns:
            Learning roadmap with steps and timeline
        """
        skills_str = ", ".join(missing_skills[:10])
        
        prompt = f"""Create a learning roadmap for someone transitioning to {target_role} role.

MISSING SKILLS:
{skills_str}

Provide JSON response with:
1. roadmap_steps: Array of learning steps in order
2. estimated_timeline: Timeline for each step (in weeks)
3. free_resources: Free learning resources for each step
4. practice_projects: Suggested projects to practice each skill
5. milestones: Key milestones to track progress

Format as JSON only, no markdown."""
        
        return self._call_ai(prompt, task="roadmap")
    
    def get_resume_improvement_advice(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """
        Get specific resume improvement advice
        
        Args:
            resume_text: Current resume text
            job_description: Target job description
        
        Returns:
            Detailed improvement advice
        """
        prompt = f"""Provide specific, actionable resume improvement advice.

CURRENT RESUME:
{resume_text[:2000]}

TARGET JOB:
{job_description[:1500]}

Provide JSON response with:
1. summary_suggestions: How to improve the summary/objective
2. experience_improvements: Specific improvements for work experience section
3. skills_section_tips: How to better present skills
4. keyword_optimization: Important keywords to add
5. formatting_tips: Formatting and structure suggestions

Format as JSON only, no markdown."""
        
        return self._call_ai(prompt, task="improvement")
    
    def _call_ai(self, prompt: str, task: str = "chat") -> Dict[str, Any]:
        """
        Call AI service with fallback logic
        
        Args:
            prompt: Input prompt
            task: Task type
        
        Returns:
            AI response as dictionary
        """
        # Try Hugging Face first
        if self.hf_available:
            try:
                result = self._call_huggingface(prompt, task)
                if result:
                    return result
            except Exception as e:
                print(f"Hugging Face API error: {str(e)}, trying fallback...")
        
        # Fallback to Gemini
        if self.gemini_available:
            try:
                result = self._call_gemini(prompt)
                if result:
                    return result
            except Exception as e:
                print(f"Gemini API error: {str(e)}")
        
        # If all fail, return basic response
        return self._get_fallback_response(task)
    
    def _call_huggingface(self, prompt: str, task: str) -> Optional[Dict[str, Any]]:
        """Call Hugging Face Inference API"""
        try:
            model = self.hf_models.get(task, self.hf_models["chat"])
            url = f"{self.hf_api_url}/{model}"
            
            headers = {
                "Authorization": f"Bearer {self.hf_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 1000,
                    "temperature": 0.7,
                    "return_full_text": False
                }
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract text from response
                if isinstance(result, list) and len(result) > 0:
                    text = result[0].get("generated_text", "")
                elif isinstance(result, dict):
                    text = result.get("generated_text", str(result))
                else:
                    text = str(result)
                
                # Try to parse JSON from response
                return self._parse_ai_response(text)
            else:
                print(f"HF API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Hugging Face API exception: {str(e)}")
            return None
    
    def _call_gemini(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Call Google Gemini API (free tier)"""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 1000,
                }
            )
            
            text = response.text
            
            # Try to parse JSON from response
            return self._parse_ai_response(text)
            
        except Exception as e:
            print(f"Gemini API exception: {str(e)}")
            return None
    
    def _parse_ai_response(self, text: str) -> Dict[str, Any]:
        """Parse AI response text and extract JSON"""
        try:
            # Try to find JSON in the response
            text = text.strip()
            
            # Remove markdown code blocks if present
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            # Try to parse as JSON
            return json.loads(text)
            
        except json.JSONDecodeError:
            # If not JSON, return as text response
            return {
                "response": text,
                "parsed": False
            }
    
    def _get_fallback_response(self, task: str) -> Dict[str, Any]:
        """Get fallback response when AI APIs are unavailable"""
        # Return empty dict to indicate no AI analysis available
        # This allows the frontend to hide the section instead of showing fallback messages
        fallback_responses = {
            "analysis": {
                "parsed": False,
                "unavailable": True
            },
            "recommendations": {
                "recommended_skills": [],
                "learning_priority": {},
                "skill_explanations": {},
                "learning_resources": {}
            },
            "roadmap": {
                "roadmap_steps": [],
                "estimated_timeline": {},
                "free_resources": {},
                "practice_projects": {},
                "milestones": []
            },
            "improvement": {
                "summary_suggestions": "Tailor your summary to match the job description",
                "experience_improvements": "Use action verbs and quantify achievements",
                "skills_section_tips": "List skills in order of relevance to the job",
                "keyword_optimization": "Include keywords from the job description",
                "formatting_tips": "Keep formatting clean and consistent"
            }
        }
        
        return fallback_responses.get(task, {"response": "Service unavailable"})


class RoleAnalyzer:
    """Analyze resumes for specific roles and provide targeted recommendations"""
    
    # Role-specific skill mappings
    ROLE_SKILLS = {
        "Software Engineer": {
            "core": ["Programming", "Data Structures", "Algorithms", "Software Design"],
            "languages": ["Python", "Java", "JavaScript", "C++"],
            "tools": ["Git", "Docker", "CI/CD", "Testing"]
        },
        "Data Scientist": {
            "core": ["Statistics", "Machine Learning", "Data Analysis", "Python"],
            "libraries": ["Pandas", "NumPy", "Scikit-learn", "TensorFlow"],
            "tools": ["Jupyter", "SQL", "Data Visualization"]
        },
        "Frontend Developer": {
            "core": ["HTML", "CSS", "JavaScript", "React"],
            "frameworks": ["React", "Vue", "Angular", "Next.js"],
            "tools": ["Webpack", "Git", "Responsive Design"]
        },
        "Backend Developer": {
            "core": ["API Development", "Database Design", "Server Management"],
            "languages": ["Python", "Java", "Node.js", "Go"],
            "tools": ["Docker", "Kubernetes", "AWS", "REST API"]
        },
        "DevOps Engineer": {
            "core": ["CI/CD", "Cloud Platforms", "Containerization", "Infrastructure"],
            "tools": ["Docker", "Kubernetes", "Jenkins", "Terraform", "AWS"],
            "skills": ["Linux", "Scripting", "Monitoring"]
        }
    }
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
    
    def analyze_for_role(self, resume_text: str, target_role: str) -> Dict[str, Any]:
        """
        Analyze resume for a specific role
        
        Args:
            resume_text: Resume text
            target_role: Target role name
        
        Returns:
            Role-specific analysis
        """
        # Get role skills
        role_skills = self.ROLE_SKILLS.get(target_role, self.ROLE_SKILLS["Software Engineer"])
        
        # Get AI recommendations
        ai_recs = self.ai_service.get_role_recommendations(resume_text, target_role)
        
        # Combine with role-specific skills
        return {
            "target_role": target_role,
            "required_skills": role_skills,
            "ai_recommendations": ai_recs,
            "skill_gaps": self._identify_skill_gaps(resume_text, role_skills),
            "learning_path": self._suggest_learning_path(role_skills, ai_recs)
        }
    
    def _identify_skill_gaps(self, resume_text: str, role_skills: Dict) -> List[str]:
        """Identify missing skills for the role"""
        resume_lower = resume_text.lower()
        gaps = []
        
        # Check core skills
        for skill in role_skills.get("core", []):
            if skill.lower() not in resume_lower:
                gaps.append(skill)
        
        # Check languages
        for lang in role_skills.get("languages", []):
            if lang.lower() not in resume_lower:
                gaps.append(lang)
        
        return gaps[:5]  # Top 5 gaps
    
    def _suggest_learning_path(self, role_skills: Dict, ai_recs: Dict) -> List[Dict]:
        """Suggest learning path based on role and AI recommendations"""
        path = []
        
        # Add core skills first
        for skill in role_skills.get("core", [])[:3]:
            path.append({
                "skill": skill,
                "priority": "high",
                "timeline": "2-4 weeks",
                "resources": "Free online courses and documentation"
            })
        
        return path

