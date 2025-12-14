"""
Role-Based Skill Advisor Module
Detects target role and generates personalized skill roadmaps using LLM
"""

import re
import json
from typing import Dict, List, Any, Optional
from llm_service import LLMService


class RoleAdvisor:
    """AI-powered role-based skill advisor"""
    
    # Common role keywords for detection
    ROLE_KEYWORDS = {
        "Software Development Engineer": ["sde", "software engineer", "software developer", "developer", "programmer", "coding"],
        "Data Scientist": ["data scientist", "data science", "data analyst", "ml scientist"],
        "ML Engineer": ["ml engineer", "machine learning engineer", "ai engineer", "deep learning engineer"],
        "Frontend Developer": ["frontend", "front-end", "ui developer", "react developer", "angular developer"],
        "Backend Developer": ["backend", "back-end", "api developer", "server developer", "node.js developer"],
        "Full Stack Developer": ["full stack", "fullstack", "full-stack"],
        "DevOps Engineer": ["devops", "sre", "site reliability", "cloud engineer"],
        "QA Engineer": ["qa", "quality assurance", "test engineer", "testing"],
        "Product Manager": ["product manager", "pm", "product owner"],
        "Data Engineer": ["data engineer", "etl", "data pipeline"]
    }
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    def detect_role(self, job_description: str, resume_text: str = "") -> str:
        """
        Detect the target role from job description and resume
        
        Args:
            job_description: Job description text
            resume_text: Optional resume text for context
            
        Returns:
            Detected role name
        """
        combined_text = (job_description + " " + resume_text).lower()
        
        # Count matches for each role
        role_scores = {}
        for role, keywords in self.ROLE_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in combined_text)
            if score > 0:
                role_scores[role] = score
        
        if role_scores:
            # Return role with highest score
            detected_role = max(role_scores, key=role_scores.get)
            return detected_role
        
        # Default to SDE if no clear match
        return "Software Development Engineer"
    
    async def generate_role_skills(self, role: str) -> Dict[str, Any]:
        """
        Generate role-specific required skills using LLM
        
        Args:
            role: Target role name
            
        Returns:
            Dictionary with role skills categorized
        """
        if self.llm_service.is_available():
            prompt = f"""You are a career advisor. For the role of {role}, provide a comprehensive list of required skills.

Format your response as JSON with the following structure:
{{
    "core_skills": ["skill1", "skill2", ...],
    "programming_languages": ["language1", "language2", ...],
    "tools_technologies": ["tool1", "tool2", ...],
    "concepts": ["concept1", "concept2", ...],
    "description": "Brief description of what this role entails"
}}

Focus on beginner-to-job-ready level skills. Return ONLY valid JSON, no additional text."""
            
            try:
                response = await self.llm_service.generate_text(prompt, max_tokens=800)
                # Try to extract JSON from response
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    skills_data = json.loads(json_match.group())
                    return skills_data
            except Exception as e:
                print(f"Error generating role skills with LLM: {str(e)}")
        
        # Fallback to rule-based skills
        return self._get_fallback_role_skills(role)
    
    def _get_fallback_role_skills(self, role: str) -> Dict[str, Any]:
        """Fallback role skills when LLM is not available"""
        role_lower = role.lower()
        
        if "sde" in role_lower or "software" in role_lower or "developer" in role_lower:
            return {
                "core_skills": ["Problem Solving", "Data Structures", "Algorithms", "System Design Basics", "Object-Oriented Programming"],
                "programming_languages": ["Python", "Java", "C++", "JavaScript"],
                "tools_technologies": ["Git", "Linux", "REST APIs", "Databases (SQL)", "Docker"],
                "concepts": ["Time Complexity", "Space Complexity", "Design Patterns", "Version Control"],
                "description": "Software Development Engineer - Build and maintain software applications"
            }
        elif "data scientist" in role_lower:
            return {
                "core_skills": ["Statistics", "Machine Learning", "Data Analysis", "Data Visualization"],
                "programming_languages": ["Python", "R", "SQL"],
                "tools_technologies": ["Pandas", "NumPy", "Scikit-learn", "Jupyter", "TensorFlow"],
                "concepts": ["Supervised Learning", "Unsupervised Learning", "Feature Engineering"],
                "description": "Data Scientist - Extract insights from data using statistical and ML methods"
            }
        elif "ml engineer" in role_lower:
            return {
                "core_skills": ["Machine Learning", "Deep Learning", "MLOps", "Model Deployment"],
                "programming_languages": ["Python", "C++"],
                "tools_technologies": ["TensorFlow", "PyTorch", "Docker", "Kubernetes", "AWS"],
                "concepts": ["Neural Networks", "Model Training", "Model Serving", "A/B Testing"],
                "description": "ML Engineer - Design and deploy machine learning systems at scale"
            }
        elif "frontend" in role_lower:
            return {
                "core_skills": ["HTML", "CSS", "JavaScript", "Responsive Design", "UI/UX"],
                "programming_languages": ["JavaScript", "TypeScript"],
                "tools_technologies": ["React", "Vue.js", "Angular", "Webpack", "npm"],
                "concepts": ["Component Architecture", "State Management", "DOM Manipulation"],
                "description": "Frontend Developer - Build user interfaces and client-side applications"
            }
        elif "backend" in role_lower:
            return {
                "core_skills": ["API Design", "Database Design", "Server Architecture", "Authentication"],
                "programming_languages": ["Python", "Java", "Node.js", "Go"],
                "tools_technologies": ["Django", "Flask", "Express", "PostgreSQL", "Redis"],
                "concepts": ["REST APIs", "GraphQL", "Microservices", "Caching"],
                "description": "Backend Developer - Build server-side applications and APIs"
            }
        else:
            # Generic fallback
            return {
                "core_skills": ["Problem Solving", "Communication", "Technical Skills"],
                "programming_languages": ["Python", "JavaScript"],
                "tools_technologies": ["Git", "Linux"],
                "concepts": ["Best Practices", "Industry Standards"],
                "description": f"{role} - Professional role requiring technical expertise"
            }
    
    async def analyze_skill_gaps(
        self, 
        resume_skills: List[str], 
        role_skills: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze gaps between resume skills and role requirements
        
        Args:
            resume_skills: Skills extracted from resume
            role_skills: Required skills for the role
            
        Returns:
            Categorized skill analysis
        """
        resume_skills_lower = {s.lower() for s in resume_skills}
        
        # Combine all role skills
        all_role_skills = []
        all_role_skills.extend(role_skills.get("core_skills", []))
        all_role_skills.extend(role_skills.get("programming_languages", []))
        all_role_skills.extend(role_skills.get("tools_technologies", []))
        all_role_skills.extend(role_skills.get("concepts", []))
        
        # Categorize skills
        skills_you_have = []
        skills_to_improve = []
        skills_to_learn = []
        
        for skill in all_role_skills:
            skill_lower = skill.lower()
            # Check for exact or partial match
            matched = False
            matched_skill = None
            
            for resume_skill in resume_skills:
                if skill_lower in resume_skill.lower() or resume_skill.lower() in skill_lower:
                    matched = True
                    matched_skill = resume_skill
                    break
            
            if matched:
                # Check if it's a strong match (exact) or weak match (needs improvement)
                if skill_lower == matched_skill.lower():
                    skills_you_have.append(skill)
                else:
                    skills_to_improve.append({
                        "current": matched_skill,
                        "target": skill,
                        "gap": f"Your resume mentions '{matched_skill}' but the role requires stronger '{skill}' skills"
                    })
            else:
                skills_to_learn.append(skill)
        
        return {
            "skills_you_have": skills_you_have,
            "skills_to_improve": skills_to_improve,
            "skills_to_learn": skills_to_learn,
            "total_required": len(all_role_skills),
            "total_you_have": len(skills_you_have),
            "coverage_percentage": round((len(skills_you_have) / len(all_role_skills) * 100) if all_role_skills else 0, 2)
        }
    
    async def generate_roadmap(
        self,
        role: str,
        skill_gaps: Dict[str, Any],
        resume_skills: List[str],
        match_score: float
    ) -> Dict[str, Any]:
        """
        Generate personalized learning roadmap using LLM
        
        Args:
            role: Target role
            skill_gaps: Skill gap analysis
            resume_skills: Current resume skills
            match_score: Current match score
            
        Returns:
            Personalized roadmap
        """
        if self.llm_service.is_available():
            prompt = f"""You are a career advisor helping a fresher/junior developer prepare for the role of {role}.

Current Situation:
- Match Score: {match_score}%
- Skills they have: {', '.join(resume_skills[:10])}
- Skills they need to learn: {', '.join(skill_gaps['skills_to_learn'][:10])}

Generate a practical, step-by-step learning roadmap. Format as JSON:
{{
    "phase1": {{
        "title": "Foundation (Weeks 1-4)",
        "skills": ["skill1", "skill2"],
        "actions": ["action1", "action2"],
        "resources": ["resource1", "resource2"]
    }},
    "phase2": {{
        "title": "Core Skills (Weeks 5-8)",
        "skills": ["skill1", "skill2"],
        "actions": ["action1", "action2"],
        "resources": ["resource1", "resource2"]
    }},
    "phase3": {{
        "title": "Advanced & Practice (Weeks 9-12)",
        "skills": ["skill1", "skill2"],
        "actions": ["action1", "action2"],
        "resources": ["resource1", "resource2"]
    }},
    "final_advice": "Motivational and practical advice for cracking this role"
}}

Make it realistic for a fresher. Return ONLY valid JSON."""
            
            try:
                response = await self.llm_service.generate_text(prompt, max_tokens=1200)
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    roadmap = json.loads(json_match.group())
                    return roadmap
            except Exception as e:
                print(f"Error generating roadmap with LLM: {str(e)}")
        
        # Fallback roadmap
        return self._get_fallback_roadmap(role, skill_gaps, match_score)
    
    def _get_fallback_roadmap(
        self, 
        role: str, 
        skill_gaps: Dict[str, Any], 
        match_score: float
    ) -> Dict[str, Any]:
        """Fallback roadmap when LLM is not available"""
        skills_to_learn = skill_gaps.get("skills_to_learn", [])[:5]
        
        return {
            "phase1": {
                "title": "Foundation (Weeks 1-4)",
                "skills": skills_to_learn[:2] if skills_to_learn else ["Core Programming", "Problem Solving"],
                "actions": [
                    "Master one programming language (Python/Java recommended)",
                    "Practice basic data structures (arrays, lists, dictionaries)",
                    "Solve 50+ coding problems on platforms like LeetCode Easy",
                    "Learn Git basics and create a GitHub profile"
                ],
                "resources": [
                    "freeCodeCamp - Programming Fundamentals",
                    "LeetCode - Easy Problems",
                    "GitHub Learning Lab"
                ]
            },
            "phase2": {
                "title": "Core Skills (Weeks 5-8)",
                "skills": skills_to_learn[2:4] if len(skills_to_learn) > 2 else ["Algorithms", "System Design Basics"],
                "actions": [
                    "Learn algorithms (sorting, searching, dynamic programming)",
                    "Build 2-3 projects showcasing your skills",
                    "Learn about databases and APIs",
                    "Practice system design basics"
                ],
                "resources": [
                    "Grokking Algorithms book",
                    "Build a portfolio project",
                    "System Design Primer (GitHub)"
                ]
            },
            "phase3": {
                "title": "Advanced & Practice (Weeks 9-12)",
                "skills": skills_to_learn[4:] if len(skills_to_learn) > 4 else ["Advanced Concepts", "Best Practices"],
                "actions": [
                    "Solve medium-hard coding problems",
                    "Contribute to open source projects",
                    "Prepare for technical interviews",
                    "Create a strong resume highlighting projects"
                ],
                "resources": [
                    "LeetCode - Medium/Hard Problems",
                    "Cracking the Coding Interview book",
                    "Mock interview platforms"
                ]
            },
            "final_advice": (
                f"Your current match score is {match_score}%. "
                f"Focus on learning the missing skills systematically. "
                f"Build projects to demonstrate your abilities. "
                f"Practice coding problems daily. "
                f"With consistent effort over 2-3 months, you can significantly improve your profile for {role} roles."
            )
        }

