"""
Personalized Learning Roadmap Generator
Creates 30/60/90 day learning plans
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from ai_service import AIService


class LearningRoadmapGenerator:
    """Generate personalized learning roadmaps"""
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
    
    def generate_roadmap(
        self,
        target_role: str,
        experience_level: str,
        missing_skills: List[str],
        missing_fundamentals: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate personalized learning roadmap"""
        
        # Generate roadmaps for different timeframes
        roadmap_30 = self._generate_30_day_plan(target_role, experience_level, missing_skills, missing_fundamentals)
        roadmap_60 = self._generate_60_day_plan(target_role, experience_level, missing_skills, missing_fundamentals)
        roadmap_90 = self._generate_90_day_plan(target_role, experience_level, missing_skills, missing_fundamentals)
        
        # Get AI-enhanced roadmap if available
        ai_roadmap = {}
        if self.ai_service and self.ai_service.ai_enabled:
            ai_roadmap = self._get_ai_roadmap(target_role, missing_skills)
        
        return {
            "30_day": roadmap_30,
            "60_day": roadmap_60,
            "90_day": roadmap_90,
            "ai_enhanced": ai_roadmap,
            "target_role": target_role,
            "experience_level": experience_level
        }
    
    def _generate_30_day_plan(
        self,
        target_role: str,
        experience_level: str,
        missing_skills: List[str],
        missing_fundamentals: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate 30-day learning plan"""
        
        # Prioritize high-priority fundamentals
        high_priority = [m for m in missing_fundamentals if m.get("priority") == "high"][:2]
        medium_priority = [m for m in missing_fundamentals if m.get("priority") == "medium"][:1]
        
        weeks = []
        
        # Week 1: Foundation
        week1_skills = [h["skill"] for h in high_priority[:1]]
        weeks.append({
            "week": 1,
            "focus": "Foundation Building",
            "skills": week1_skills,
            "tasks": [
                f"Learn basics of {week1_skills[0] if week1_skills else 'core skills'}",
                "Complete online course or tutorial",
                "Practice with small exercises"
            ],
            "projects": [],
            "milestone": f"Understand fundamentals of {week1_skills[0] if week1_skills else 'core concepts'}"
        })
        
        # Week 2: Practice
        weeks.append({
            "week": 2,
            "focus": "Hands-on Practice",
            "skills": week1_skills,
            "tasks": [
                "Build small practice projects",
                "Solve coding problems related to skills",
                "Review and reinforce concepts"
            ],
            "projects": [f"Build 1 small project using {week1_skills[0] if week1_skills else 'learned skills'}"],
            "milestone": "Complete first project"
        })
        
        # Week 3: Advanced Topics
        week3_skills = [h["skill"] for h in high_priority[1:]] + [m["skill"] for m in medium_priority]
        weeks.append({
            "week": 3,
            "focus": "Advanced Learning",
            "skills": week3_skills[:2] if week3_skills else week1_skills,
            "tasks": [
                "Learn advanced concepts",
                "Study best practices",
                "Review industry standards"
            ],
            "projects": [],
            "milestone": "Gain deeper understanding"
        })
        
        # Week 4: Integration
        weeks.append({
            "week": 4,
            "focus": "Integration & Portfolio",
            "skills": week1_skills + week3_skills[:1],
            "tasks": [
                "Build a portfolio project",
                "Add projects to GitHub",
                "Update resume with new skills"
            ],
            "projects": [f"Build 1 portfolio project showcasing {week1_skills[0] if week1_skills else 'skills'}"],
            "milestone": "Complete portfolio project and update resume"
        })
        
        return {
            "duration": "30 days",
            "weeks": weeks,
            "total_projects": 2,
            "focus_areas": [h["skill"] for h in high_priority[:2]],
            "success_criteria": "Complete 2 projects and add skills to resume"
        }
    
    def _generate_60_day_plan(
        self,
        target_role: str,
        experience_level: str,
        missing_skills: List[str],
        missing_fundamentals: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate 60-day learning plan"""
        
        # More comprehensive plan
        high_priority = [m for m in missing_fundamentals if m.get("priority") == "high"][:3]
        medium_priority = [m for m in missing_fundamentals if m.get("priority") == "medium"][:2]
        
        weeks = []
        
        # Weeks 1-2: Foundation
        weeks.append({
            "weeks": "1-2",
            "focus": "Core Fundamentals",
            "skills": [h["skill"] for h in high_priority[:2]],
            "tasks": [
                "Complete comprehensive courses",
                "Practice daily coding problems",
                "Build understanding of core concepts"
            ],
            "projects": ["Build 1 foundational project"],
            "milestone": "Strong foundation in core skills"
        })
        
        # Weeks 3-4: Application
        weeks.append({
            "weeks": "3-4",
            "focus": "Practical Application",
            "skills": [h["skill"] for h in high_priority],
            "tasks": [
                "Build real-world projects",
                "Implement best practices",
                "Get code reviews"
            ],
            "projects": ["Build 2-3 practical projects"],
            "milestone": "Portfolio with 3+ projects"
        })
        
        # Weeks 5-6: Advanced & Specialization
        weeks.append({
            "weeks": "5-6",
            "focus": "Advanced Topics & Specialization",
            "skills": [m["skill"] for m in medium_priority] + missing_skills[:2],
            "tasks": [
                "Learn advanced concepts",
                "Study system design (if applicable)",
                "Prepare for interviews"
            ],
            "projects": ["Build 1 advanced project"],
            "milestone": "Ready for technical interviews"
        })
        
        # Weeks 7-8: Mastery & Portfolio
        weeks.append({
            "weeks": "7-8",
            "focus": "Mastery & Portfolio Building",
            "skills": "All learned skills",
            "tasks": [
                "Refine portfolio projects",
                "Write technical blog posts",
                "Contribute to open source",
                "Update resume comprehensively"
            ],
            "projects": ["Polish all projects", "Add to portfolio"],
            "milestone": "Strong portfolio ready for job applications"
        })
        
        return {
            "duration": "60 days",
            "phases": weeks,
            "total_projects": 5,
            "focus_areas": [h["skill"] for h in high_priority] + [m["skill"] for m in medium_priority],
            "success_criteria": "Complete 5+ projects, strong portfolio, interview-ready"
        }
    
    def _generate_90_day_plan(
        self,
        target_role: str,
        experience_level: str,
        missing_skills: List[str],
        missing_fundamentals: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate 90-day comprehensive learning plan"""
        
        # Comprehensive transformation plan
        high_priority = [m for m in missing_fundamentals if m.get("priority") == "high"]
        medium_priority = [m for m in missing_fundamentals if m.get("priority") == "medium"]
        low_priority = [m for m in missing_fundamentals if m.get("priority") == "low"][:2]
        
        phases = []
        
        # Phase 1: Foundation (Days 1-30)
        phases.append({
            "phase": "Foundation",
            "duration": "Days 1-30",
            "focus": "Build Strong Foundation",
            "skills": [h["skill"] for h in high_priority[:3]],
            "tasks": [
                "Complete comprehensive courses",
                "Daily coding practice",
                "Build foundational projects"
            ],
            "projects": 3,
            "milestone": "Strong foundation established"
        })
        
        # Phase 2: Application (Days 31-60)
        phases.append({
            "phase": "Application",
            "duration": "Days 31-60",
            "focus": "Real-World Application",
            "skills": [h["skill"] for h in high_priority] + [m["skill"] for m in medium_priority[:2]],
            "tasks": [
                "Build complex projects",
                "Implement best practices",
                "Get mentorship/feedback"
            ],
            "projects": 4,
            "milestone": "Portfolio with 7+ projects"
        })
        
        # Phase 3: Mastery (Days 61-90)
        phases.append({
            "phase": "Mastery",
            "duration": "Days 61-90",
            "focus": "Mastery & Specialization",
            "skills": "All skills + specialization",
            "tasks": [
                "Advanced projects",
                "Open source contributions",
                "Technical writing",
                "Interview preparation",
                "Resume optimization"
            ],
            "projects": 3,
            "milestone": "Job-ready with strong portfolio"
        })
        
        return {
            "duration": "90 days",
            "phases": phases,
            "total_projects": 10,
            "focus_areas": [h["skill"] for h in high_priority] + [m["skill"] for m in medium_priority],
            "success_criteria": "Complete 10+ projects, strong portfolio, interview-ready, job applications ready"
        }
    
    def _get_ai_roadmap(
        self,
        target_role: str,
        missing_skills: List[str]
    ) -> Dict[str, Any]:
        """Get AI-enhanced personalized roadmap"""
        if not self.ai_service or not self.ai_service.ai_enabled:
            return {}
        
        skills_str = ", ".join(missing_skills[:10])
        
        prompt = f"""Create a personalized 90-day learning roadmap for becoming a {target_role}.

MISSING SKILLS:
{skills_str}

Provide JSON with:
1. weekly_breakdown: Week-by-week learning plan
2. daily_schedule: Suggested daily time allocation
3. project_timeline: When to build projects
4. milestones: Key milestones to track progress
5. resources: Specific resources for each week

Format as JSON only."""
        
        try:
            return self.ai_service._call_ai(prompt, task="roadmap")
        except:
            return {}


