"""
Smart Suggestions Generator
Provides actionable, specific suggestions (not generic advice)
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from ai_service import AIService


class SmartSuggestionGenerator:
    """Generate smart, actionable suggestions"""
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
    
    def generate_suggestions(
        self,
        analysis: Dict[str, Any],
        target_role: str,
        experience_level: str,
        missing_skills: List[str]
    ) -> Dict[str, Any]:
        """Generate comprehensive smart suggestions"""
        
        suggestions = {
            "skills_to_add": self._suggest_skills_to_add(missing_skills, target_role, experience_level),
            "projects_to_build": self._suggest_projects(target_role, experience_level, missing_skills),
            "topics_to_learn": self._suggest_topics(target_role, missing_skills),
            "certifications": self._suggest_certifications(target_role, experience_level),
            "resume_improvements": self._suggest_resume_improvements(analysis),
            "actionable_steps": self._generate_actionable_steps(analysis, target_role)
        }
        
        # Enhance with AI if available
        if self.ai_service and self.ai_service.ai_enabled:
            ai_suggestions = self._get_ai_suggestions(analysis, target_role)
            suggestions["ai_enhanced"] = ai_suggestions
        
        return suggestions
    
    def _suggest_skills_to_add(
        self, 
        missing_skills: List[str], 
        target_role: str,
        experience_level: str
    ) -> List[Dict[str, Any]]:
        """Suggest specific skills to add"""
        suggestions = []
        
        # Role-specific skill priorities
        role_skill_map = {
            "Software Engineer": {
                "high": ["System Design", "DSA", "OOP", "Git"],
                "medium": ["REST APIs", "Database Design", "Testing"],
                "low": ["Docker", "CI/CD", "Cloud Basics"]
            },
            "Backend Developer": {
                "high": ["REST/GraphQL APIs", "Database Optimization", "Authentication"],
                "medium": ["Microservices", "Caching", "Message Queues"],
                "low": ["Kubernetes", "Monitoring", "API Security"]
            },
            "Frontend Developer": {
                "high": ["React/Vue/Angular", "JavaScript ES6+", "State Management"],
                "medium": ["Responsive Design", "Web Performance", "Build Tools"],
                "low": ["PWA", "WebAssembly", "Testing Frameworks"]
            },
            "Data Scientist": {
                "high": ["Pandas", "NumPy", "Scikit-learn", "SQL"],
                "medium": ["TensorFlow/PyTorch", "Data Visualization", "Statistics"],
                "low": ["MLOps", "Big Data Tools", "Cloud ML"]
            }
        }
        
        role_skills = role_skill_map.get(target_role, role_skill_map["Software Engineer"])
        
        # Prioritize missing skills
        for priority in ["high", "medium", "low"]:
            for skill in role_skills.get(priority, []):
                if skill not in missing_skills:
                    continue
                
                suggestions.append({
                    "skill": skill,
                    "priority": priority,
                    "action": self._get_skill_action(skill, experience_level),
                    "timeline": self._get_skill_timeline(skill, experience_level),
                    "resources": self._get_skill_resources(skill)
                })
        
        return suggestions[:10]  # Top 10
    
    def _suggest_projects(
        self,
        target_role: str,
        experience_level: str,
        missing_skills: List[str]
    ) -> List[Dict[str, Any]]:
        """Suggest specific projects to build"""
        
        project_templates = {
            "Software Engineer": [
                {
                    "name": "REST API Backend",
                    "description": "Build a REST API with authentication and database",
                    "skills": ["REST APIs", "Authentication", "Database"],
                    "complexity": "medium",
                    "timeline": "2-3 weeks"
                },
                {
                    "name": "Full-Stack Web App",
                    "description": "Create a full-stack application with frontend and backend",
                    "skills": ["Frontend", "Backend", "Database"],
                    "complexity": "high",
                    "timeline": "4-6 weeks"
                },
                {
                    "name": "System Design Project",
                    "description": "Design and implement a scalable system (e.g., URL shortener)",
                    "skills": ["System Design", "Scalability", "Architecture"],
                    "complexity": "high",
                    "timeline": "3-4 weeks"
                }
            ],
            "Backend Developer": [
                {
                    "name": "Microservices API",
                    "description": "Build a microservices architecture with 2-3 services",
                    "skills": ["Microservices", "API Design", "Docker"],
                    "complexity": "high",
                    "timeline": "3-4 weeks"
                },
                {
                    "name": "Authentication Service",
                    "description": "Implement JWT-based authentication with refresh tokens",
                    "skills": ["Authentication", "Security", "JWT"],
                    "complexity": "medium",
                    "timeline": "2 weeks"
                }
            ],
            "Frontend Developer": [
                {
                    "name": "React Dashboard",
                    "description": "Build a responsive dashboard with charts and data visualization",
                    "skills": ["React", "State Management", "API Integration"],
                    "complexity": "medium",
                    "timeline": "2-3 weeks"
                },
                {
                    "name": "E-commerce Frontend",
                    "description": "Create a modern e-commerce UI with cart and checkout",
                    "skills": ["React/Vue", "State Management", "Responsive Design"],
                    "complexity": "high",
                    "timeline": "3-4 weeks"
                }
            ],
            "Data Scientist": [
                {
                    "name": "ML Prediction Model",
                    "description": "Build and deploy a machine learning prediction model",
                    "skills": ["Machine Learning", "Python", "Model Deployment"],
                    "complexity": "medium",
                    "timeline": "3 weeks"
                },
                {
                    "name": "Data Analysis Dashboard",
                    "description": "Analyze a dataset and create visualizations",
                    "skills": ["Data Analysis", "Visualization", "Pandas"],
                    "complexity": "medium",
                    "timeline": "2 weeks"
                }
            ]
        }
        
        projects = project_templates.get(target_role, project_templates["Software Engineer"])
        
        # Filter by experience level
        if experience_level == "fresher":
            projects = [p for p in projects if p["complexity"] != "high"]
        elif experience_level == "junior":
            projects = [p for p in projects if p["complexity"] in ["medium", "low"]]
        
        # Add specific project suggestions based on missing skills
        custom_projects = []
        if "REST APIs" in missing_skills:
            custom_projects.append({
                "name": "REST API Project",
                "description": "Build 1 backend project using REST APIs and authentication",
                "skills": ["REST APIs", "Authentication"],
                "complexity": "medium",
                "timeline": "2 weeks",
                "specific": True
            })
        
        if "System Design" in missing_skills:
            custom_projects.append({
                "name": "System Design Practice",
                "description": "Design and document a scalable system (e.g., Twitter clone)",
                "skills": ["System Design", "Architecture"],
                "complexity": "high",
                "timeline": "2-3 weeks",
                "specific": True
            })
        
        return (custom_projects + projects)[:5]
    
    def _suggest_topics(self, target_role: str, missing_skills: List[str]) -> List[Dict[str, Any]]:
        """Suggest specific topics to learn"""
        
        topic_map = {
            "Software Engineer": [
                {"topic": "Data Structures & Algorithms", "priority": "high", "resources": "LeetCode, GeeksforGeeks"},
                {"topic": "System Design Fundamentals", "priority": "high", "resources": "System Design Primer, Grokking"},
                {"topic": "OOP Principles", "priority": "medium", "resources": "FreeCodeCamp, MDN"},
                {"topic": "Database Design", "priority": "medium", "resources": "SQL Tutorial, Database Design Course"}
            ],
            "Backend Developer": [
                {"topic": "API Design Best Practices", "priority": "high", "resources": "REST API Tutorial"},
                {"topic": "Database Optimization", "priority": "high", "resources": "SQL Performance Guide"},
                {"topic": "Microservices Architecture", "priority": "medium", "resources": "Microservices Patterns"},
                {"topic": "Authentication & Security", "priority": "medium", "resources": "OWASP Guidelines"}
            ],
            "Frontend Developer": [
                {"topic": "JavaScript ES6+ Features", "priority": "high", "resources": "MDN Web Docs, JavaScript.info"},
                {"topic": "React/Vue State Management", "priority": "high", "resources": "Official Docs"},
                {"topic": "Web Performance Optimization", "priority": "medium", "resources": "Web.dev Performance"},
                {"topic": "Responsive Design Patterns", "priority": "medium", "resources": "CSS-Tricks, MDN"}
            ],
            "Data Scientist": [
                {"topic": "Statistics Fundamentals", "priority": "high", "resources": "Khan Academy, Coursera"},
                {"topic": "Machine Learning Basics", "priority": "high", "resources": "Andrew Ng's Course"},
                {"topic": "Data Visualization", "priority": "medium", "resources": "Matplotlib, Seaborn Docs"},
                {"topic": "Feature Engineering", "priority": "medium", "resources": "Kaggle Learn"}
            ]
        }
        
        topics = topic_map.get(target_role, topic_map["Software Engineer"])
        
        # Add missing skill topics
        for skill in missing_skills[:5]:
            if not any(t["topic"].lower() in skill.lower() for t in topics):
                topics.append({
                    "topic": skill,
                    "priority": "medium",
                    "resources": "Online courses and documentation"
                })
        
        return topics[:8]
    
    def _suggest_certifications(
        self, 
        target_role: str, 
        experience_level: str
    ) -> List[Dict[str, Any]]:
        """Suggest relevant certifications (optional)"""
        
        certs = {
            "Software Engineer": [
                {"name": "AWS Certified Solutions Architect", "optional": True, "cost": "Paid"},
                {"name": "Google Cloud Professional", "optional": True, "cost": "Paid"},
                {"name": "FreeCodeCamp Certifications", "optional": True, "cost": "Free"}
            ],
            "Backend Developer": [
                {"name": "REST API Design", "optional": True, "cost": "Free (Coursera)"},
                {"name": "Database Design", "optional": True, "cost": "Free (edX)"}
            ],
            "Data Scientist": [
                {"name": "Google Data Analytics Certificate", "optional": True, "cost": "Paid (Coursera)"},
                {"name": "Kaggle Micro-Courses", "optional": True, "cost": "Free"}
            ]
        }
        
        return certs.get(target_role, [])[:3]
    
    def _suggest_resume_improvements(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest specific resume improvements"""
        improvements = []
        
        structure = analysis.get("resume_structure", {})
        
        if not structure.get("sections_present", {}).get("summary"):
            improvements.append({
                "section": "Summary",
                "action": "Add a 2-3 line professional summary highlighting your key strengths",
                "example": "Experienced software engineer with expertise in..."
            })
        
        if structure.get("score", 0) < 70:
            improvements.append({
                "section": "Structure",
                "action": "Ensure all sections are present: Summary, Experience, Education, Skills, Projects",
                "example": "Organize resume into clear sections"
            })
        
        # Check for quantified achievements
        if not analysis.get("strengths", {}).get("experience_highlights"):
            improvements.append({
                "section": "Experience",
                "action": "Add measurable impact instead of responsibilities. Use numbers and metrics.",
                "example": "Improved performance by 30%' instead of 'Worked on performance optimization'"
            })
        
        return improvements
    
    def _generate_actionable_steps(
        self, 
        analysis: Dict[str, Any],
        target_role: str
    ) -> List[Dict[str, Any]]:
        """Generate immediate actionable steps"""
        steps = []
        
        missing_fundamentals = analysis.get("missing_fundamentals", [])
        high_priority = [m for m in missing_fundamentals if m.get("priority") == "high"][:3]
        
        for i, fundamental in enumerate(high_priority, 1):
            steps.append({
                "step": i,
                "action": f"Learn {fundamental.get('skill')}",
                "why": fundamental.get("why_important", ""),
                "timeline": "2-3 weeks",
                "resources": self._get_skill_resources(fundamental.get("skill"))
            })
        
        # Add resume improvement step
        if analysis.get("resume_structure", {}).get("score", 100) < 80:
            steps.append({
                "step": len(steps) + 1,
                "action": "Improve resume structure",
                "why": "Better structure increases readability and ATS compatibility",
                "timeline": "1 week",
                "resources": "Resume templates and guides"
            })
        
        return steps[:5]
    
    def _get_skill_action(self, skill: str, experience_level: str) -> str:
        """Get specific action for learning a skill"""
        actions = {
            "System Design": "Study system design patterns and practice designing 2-3 systems",
            "DSA": "Solve 50+ LeetCode problems focusing on arrays, strings, and trees",
            "REST APIs": "Build 1 backend project using REST APIs and authentication",
            "React": "Complete React official tutorial and build 2-3 projects",
            "Machine Learning": "Complete Andrew Ng's ML course and build 2 prediction models"
        }
        
        for key, action in actions.items():
            if key.lower() in skill.lower():
                return action
        
        return f"Take an online course on {skill} and build a small project"
    
    def _get_skill_timeline(self, skill: str, experience_level: str) -> str:
        """Get estimated timeline for learning a skill"""
        if experience_level == "fresher":
            return "3-4 weeks"
        elif experience_level == "junior":
            return "2-3 weeks"
        else:
            return "1-2 weeks"
    
    def _get_skill_resources(self, skill: str) -> str:
        """Get learning resources for a skill"""
        resources = {
            "System Design": "System Design Primer, Grokking System Design",
            "DSA": "LeetCode, GeeksforGeeks, HackerRank",
            "REST APIs": "REST API Tutorial, Postman Learning Center",
            "React": "React Official Docs, FreeCodeCamp",
            "Machine Learning": "Coursera ML Course, Fast.ai, Kaggle Learn"
        }
        
        for key, resource in resources.items():
            if key.lower() in skill.lower():
                return resource
        
        return "Online courses, official documentation, and practice projects"
    
    def _get_ai_suggestions(
        self, 
        analysis: Dict[str, Any],
        target_role: str
    ) -> Dict[str, Any]:
        """Get AI-enhanced suggestions"""
        if not self.ai_service or not self.ai_service.ai_enabled:
            return {}
        
        prompt = f"""Based on this resume analysis for {target_role} role, provide 3-5 specific, actionable suggestions.

ANALYSIS SUMMARY:
- Experience Level: {analysis.get('experience_level', {}).get('level', 'unknown')}
- Missing Fundamentals: {len(analysis.get('missing_fundamentals', []))}
- Role Readiness: {analysis.get('role_readiness_score', {}).get('score', 0)}%

Provide JSON with:
1. top_3_priorities: Most important things to focus on
2. quick_wins: Things that can be improved quickly (1-2 weeks)
3. long_term: Long-term improvements (1-3 months)

Format as JSON only."""
        
        try:
            return self.ai_service._call_ai(prompt, task="suggestions")
        except:
            return {}

