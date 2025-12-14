"""
Resume-Job Matcher Module
Uses BERT embeddings and cosine similarity to match resumes with job descriptions
Enhanced with FREE-TIER AI services for intelligent analysis
"""

from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from skill_recommender import SkillRecommender
from ai_service import AIService, RoleAnalyzer
from advanced_analyzer import AdvancedResumeAnalyzer
from smart_suggestions import SmartSuggestionGenerator
from learning_roadmap import LearningRoadmapGenerator


class ResumeJobMatcher:
    """Advanced resume-job matcher with deep analysis and intelligent suggestions"""
    
    def __init__(self):
        # Initialize Sentence Transformer model (open-source, local)
        # Using a lightweight model for better performance
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            # Fallback to a different model if available
            self.model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
        
        # Initialize skill recommender
        self.skill_recommender = SkillRecommender()
        
        # Initialize AI service (free-tier APIs)
        try:
            self.ai_service = AIService()
            self.role_analyzer = RoleAnalyzer(self.ai_service)
            self.ai_enabled = True
        except Exception as e:
            print(f"AI service initialization warning: {str(e)}")
            print("Continuing with rule-based analysis only.")
            self.ai_service = None
            self.role_analyzer = None
            self.ai_enabled = False
        
        # Initialize advanced components
        if self.ai_service:
            self.advanced_analyzer = AdvancedResumeAnalyzer(self.ai_service)
            self.suggestion_generator = SmartSuggestionGenerator(self.ai_service)
            self.roadmap_generator = LearningRoadmapGenerator(self.ai_service)
        else:
            self.advanced_analyzer = None
            self.suggestion_generator = None
            self.roadmap_generator = None
    
    def match(
        self, 
        resume_text: str, 
        job_description: str,
        resume_skills: List[str],
        job_skills: List[str]
    ) -> Dict[str, Any]:
        """
        Match resume with job description
        
        Args:
            resume_text: Full text of the resume
            job_description: Full text of the job description
            resume_skills: List of skills extracted from resume
            job_skills: List of skills extracted from job description
        
        Returns:
            Dictionary with match score, matched skills, missing skills, and recommendations
        """
        # Calculate semantic similarity using embeddings
        resume_embedding = self.model.encode([resume_text])
        job_embedding = self.model.encode([job_description])
        
        # Cosine similarity score (0-1 range)
        similarity_score = cosine_similarity(resume_embedding, job_embedding)[0][0]
        
        # Convert numpy float32 to native Python float, then to percentage
        match_score = float(round(float(similarity_score) * 100, 2))
        
        # Find matched and missing skills
        resume_skills_set = {s.lower() for s in resume_skills}
        job_skills_set = {s.lower() for s in job_skills}
        
        matched_skills = sorted([s for s in job_skills if s.lower() in resume_skills_set])
        missing_skills = sorted([s for s in job_skills if s.lower() not in resume_skills_set])
        
        # Additional skills in resume (not in job description)
        extra_skills = sorted([s for s in resume_skills if s.lower() not in job_skills_set])
        
        # Generate detailed recommendations (rule-based)
        detailed_recommendations = self._generate_recommendations(
            match_score, matched_skills, missing_skills, resume_text, job_description
        )
        
        # Get skill recommendations
        skill_recommendations = self.skill_recommender.recommend_skills(missing_skills)
        
        # Perform advanced analysis
        advanced_analysis = None
        smart_suggestions = None
        learning_roadmap = None
        
        if self.advanced_analyzer:
            try:
                # Deep resume analysis
                advanced_analysis = self.advanced_analyzer.analyze_resume(
                    resume_text, job_description, resume_skills, job_skills
                )
                
                # Generate smart suggestions
                if advanced_analysis:
                    target_role = advanced_analysis.get("target_role", "Software Engineer")
                    experience_level = advanced_analysis.get("experience_level", {}).get("level", "mid")
                    missing_fundamentals = advanced_analysis.get("missing_fundamentals", [])
                    
                    smart_suggestions = self.suggestion_generator.generate_suggestions(
                        advanced_analysis,
                        target_role,
                        experience_level,
                        missing_skills
                    )
                    
                    # Generate learning roadmap
                    learning_roadmap = self.roadmap_generator.generate_roadmap(
                        target_role,
                        experience_level,
                        missing_skills,
                        missing_fundamentals
                    )
                
            except Exception as e:
                print(f"Advanced analysis error: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Legacy AI features (for backward compatibility)
        ai_analysis = None
        role_analysis = None
        resume_improvement = None
        
        if self.ai_enabled and self.ai_service:
            try:
                # Get AI-powered resume analysis
                ai_analysis = self.ai_service.analyze_resume(resume_text, job_description)
                
                # Get role-based recommendations
                target_role = self._detect_role(job_description)
                if target_role:
                    role_analysis = self.role_analyzer.analyze_for_role(resume_text, target_role)
                
                # Get resume improvement advice
                resume_improvement = self.ai_service.get_resume_improvement_advice(
                    resume_text, job_description
                )
                
            except Exception as e:
                print(f"AI analysis error (using fallback): {str(e)}")
        
        return {
            "match_score": match_score,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "extra_skills": extra_skills,
            "recommendations": detailed_recommendations,
            "skill_recommendations": skill_recommendations,
            "resume_skill_count": len(resume_skills),
            "job_skill_count": len(job_skills),
            "matched_skill_count": len(matched_skills),
            # Advanced analysis features
            "advanced_analysis": advanced_analysis,
            "smart_suggestions": smart_suggestions,
            "learning_roadmap": learning_roadmap,
            # Legacy AI features (for compatibility)
            "ai_analysis": ai_analysis,
            "role_analysis": role_analysis,
            "resume_improvement": resume_improvement,
            "ai_enabled": self.ai_enabled
        }
    
    def _detect_role(self, job_description: str) -> Optional[str]:
        """Detect target role from job description"""
        job_lower = job_description.lower()
        
        role_keywords = {
            "Software Engineer": ["software engineer", "sde", "swe", "software developer", "backend engineer", "full stack"],
            "Data Scientist": ["data scientist", "data science", "machine learning engineer", "ml engineer"],
            "Frontend Developer": ["frontend", "front-end", "react developer", "ui developer"],
            "Backend Developer": ["backend", "back-end", "api developer", "server developer"],
            "DevOps Engineer": ["devops", "sre", "site reliability", "cloud engineer", "infrastructure"]
        }
        
        for role, keywords in role_keywords.items():
            if any(keyword in job_lower for keyword in keywords):
                return role
        
        return "Software Engineer"  # Default
    
    def _generate_recommendations(
        self,
        match_score: float,
        matched_skills: List[str],
        missing_skills: List[str],
        resume_text: str,
        job_description: str
    ) -> Dict[str, Any]:
        """Generate detailed, beginner-friendly recommendations for resume improvement"""
        detailed_recommendations = {
            "summary": "",
            "resume_changes": [],
            "skill_improvements": [],
            "strengthen_existing": [],
            "general_tips": []
        }
        
        # Score-based summary
        if match_score < 50:
            detailed_recommendations["summary"] = (
                f"Your resume has a {match_score}% match score, which indicates significant gaps. "
                "Don't worry - this is fixable! Focus on aligning your resume with the job requirements."
            )
        elif match_score < 70:
            detailed_recommendations["summary"] = (
                f"Your resume shows a {match_score}% match - good foundation, but needs improvement. "
                "With some targeted changes, you can significantly increase your match score."
            )
        else:
            detailed_recommendations["summary"] = (
                f"Excellent! Your resume has a {match_score}% match score. "
                "You're well-aligned with the job requirements. Focus on highlighting your strengths."
            )
        
        # Detailed resume changes
        if missing_skills:
            top_missing = missing_skills[:5]
            detailed_recommendations["resume_changes"].append({
                "title": "Add Missing Skills Section",
                "description": f"Create a dedicated 'Technical Skills' section and include: {', '.join(top_missing)}. "
                             "Even if you're a beginner, mention if you've taken courses or worked on projects with these technologies.",
                "action": f"Add these keywords to your resume: {', '.join(top_missing)}"
            })
        
        # Skill improvement recommendations
        for skill in missing_skills[:5]:
            improvement_tip = self._get_skill_improvement_tip(skill)
            detailed_recommendations["skill_improvements"].append({
                "skill": skill,
                "current_status": "Not in resume",
                "action_plan": improvement_tip,
                "timeline": "1-2 weeks for basics, 1-3 months for proficiency"
            })
        
        # Strengthen existing skills
        if matched_skills:
            for skill in matched_skills[:3]:
                detailed_recommendations["strengthen_existing"].append({
                    "skill": skill,
                    "how_to_strengthen": (
                        f"✅ You already have {skill}! To strengthen it:\n"
                        f"  • Add specific projects where you used {skill}\n"
                        f"  • Quantify your experience (e.g., 'Built 3 applications using {skill}')\n"
                        f"  • Mention any certifications or courses related to {skill}\n"
                        f"  • Add {skill} to your resume summary/objective"
                    )
                })
        
        # General tips
        detailed_recommendations["general_tips"] = [
            {
                "tip": "Use Action Verbs",
                "description": "Replace passive language with action verbs: 'Developed', 'Implemented', 'Designed', 'Optimized', 'Led'"
            },
            {
                "tip": "Quantify Achievements",
                "description": "Add numbers: 'Improved performance by 30%', 'Managed team of 5', 'Reduced costs by $10K'"
            },
            {
                "tip": "Match Keywords",
                "description": "Use the exact same keywords from the job description in your resume (naturally, not forced)"
            },
            {
                "tip": "Highlight Relevant Experience",
                "description": "Move the most relevant experience to the top of your resume"
            },
            {
                "tip": "Add Projects Section",
                "description": "If you're missing required skills, add a 'Projects' section showing you've worked with those technologies"
            }
        ]
        
        return detailed_recommendations
    
    def _get_skill_improvement_tip(self, skill: str) -> str:
        """Get beginner-friendly improvement tip for a skill"""
        skill_lower = skill.lower()
        
        tips = {
            "python": "Start with Python basics on freeCodeCamp or Codecademy. Build 2-3 small projects (calculator, todo app, web scraper).",
            "javascript": "Learn JavaScript fundamentals on MDN Web Docs. Practice by building interactive web pages.",
            "react": "Complete React's official tutorial. Build a portfolio website or todo app to practice.",
            "aws": "Start with AWS Free Tier. Follow AWS's 'Getting Started' guides. Try deploying a simple website.",
            "docker": "Install Docker Desktop. Follow Docker's 'Get Started' tutorial. Containerize a simple web app.",
            "machine learning": "Take Andrew Ng's Machine Learning course on Coursera. Start with simple projects like house price prediction.",
            "sql": "Practice on SQLBolt or LeetCode. Learn JOINs, subqueries, and window functions.",
            "git": "Complete GitHub's 'Hello World' guide. Practice by creating a GitHub repository and making commits."
        }
        
        for key, tip in tips.items():
            if key in skill_lower:
                return tip
        
        return (
            f"To learn {skill}:\n"
            "  1. Find a beginner-friendly tutorial or course\n"
            "  2. Practice with small projects\n"
            "  3. Add it to your resume once you've built something with it\n"
            "  4. Consider getting a certification if available"
        )

