"""
Skill Recommender Module
Provides LinkedIn-style skill recommendations based on missing skills
"""

from typing import List, Dict


class SkillRecommender:
    """Recommend related skills, tools, and technologies"""
    
    def __init__(self):
        # Skill relationships and recommendations
        self.skill_relationships = {
            # Programming Languages
            "python": ["Django", "Flask", "FastAPI", "NumPy", "Pandas", "TensorFlow", "PyTorch"],
            "java": ["Spring Boot", "Hibernate", "Maven", "Gradle", "JUnit", "Apache Kafka"],
            "javascript": ["React", "Node.js", "Express", "TypeScript", "Vue.js", "Angular"],
            "c++": ["STL", "Boost", "Qt", "OpenCV", "CMake"],
            "c#": [".NET", "ASP.NET", "Entity Framework", "Xamarin", "Unity"],
            
            # Web Technologies
            "react": ["Redux", "Next.js", "React Router", "Material-UI", "Styled Components"],
            "angular": ["RxJS", "TypeScript", "Angular Material", "NgRx"],
            "vue": ["Vuex", "Nuxt.js", "Vuetify", "Pinia"],
            "node.js": ["Express", "MongoDB", "Socket.io", "JWT", "REST API"],
            
            # Databases
            "mysql": ["PostgreSQL", "MongoDB", "Redis", "Database Design", "SQL Optimization"],
            "mongodb": ["Mongoose", "NoSQL", "Database Design", "Indexing"],
            "postgresql": ["SQL", "Database Administration", "Performance Tuning"],
            
            # Cloud & DevOps
            "aws": ["EC2", "S3", "Lambda", "Docker", "Kubernetes", "Terraform", "CI/CD"],
            "docker": ["Kubernetes", "Docker Compose", "Container Orchestration", "CI/CD"],
            "kubernetes": ["Helm", "Docker", "Microservices", "Cloud Native"],
            "git": ["GitHub", "GitLab", "CI/CD", "Version Control", "Code Review"],
            
            # Data Science & ML
            "machine learning": ["Deep Learning", "TensorFlow", "PyTorch", "Scikit-learn", "Data Analysis"],
            "data science": ["Python", "Pandas", "NumPy", "Matplotlib", "Jupyter", "SQL"],
            "tensorflow": ["Keras", "Deep Learning", "Neural Networks", "Computer Vision"],
            "pytorch": ["Deep Learning", "Neural Networks", "Research", "Computer Vision"],
            
            # Mobile
            "android": ["Kotlin", "Java", "Material Design", "Firebase", "REST API"],
            "ios": ["Swift", "SwiftUI", "UIKit", "Core Data", "Xcode"],
            "react native": ["JavaScript", "Redux", "Mobile Development", "Firebase"],
            
            # Testing
            "testing": ["JUnit", "Jest", "Selenium", "Cypress", "Unit Testing", "Integration Testing"],
            "selenium": ["WebDriver", "Test Automation", "QA", "Python", "Java"],
        }
        
        # Learning resources mapping
        self.learning_resources = {
            "python": "Try: Python for Everybody (Coursera) or Automate the Boring Stuff",
            "javascript": "Try: JavaScript.info or freeCodeCamp's JavaScript course",
            "react": "Try: React Official Tutorial or The Complete React Developer Course",
            "aws": "Try: AWS Certified Solutions Architect course on Udemy",
            "docker": "Try: Docker & Kubernetes: The Practical Guide on Udemy",
            "machine learning": "Try: Machine Learning by Andrew Ng (Coursera) or Fast.ai",
            "data science": "Try: Data Science Specialization (Coursera) or Kaggle Learn"
        }
    
    def recommend_skills(self, missing_skills: List[str]) -> List[Dict]:
        """
        Recommend related skills based on missing skills
        
        Args:
            missing_skills: List of missing skills
        
        Returns:
            List of recommended skills with descriptions
        """
        recommendations = []
        recommended_skill_set = set()
        
        for skill in missing_skills[:10]:  # Top 10 missing skills
            skill_lower = skill.lower()
            
            # Find related skills
            related_skills = []
            for key, values in self.skill_relationships.items():
                if key in skill_lower or skill_lower in key:
                    related_skills.extend(values)
            
            # If no direct match, try partial matching
            if not related_skills:
                for key, values in self.skill_relationships.items():
                    if any(word in skill_lower for word in key.split()) or any(word in key for word in skill_lower.split()):
                        related_skills.extend(values)
            
            # Add recommendations
            for related_skill in related_skills[:3]:  # Top 3 related skills
                if related_skill not in recommended_skill_set:
                    recommended_skill_set.add(related_skill)
                    learning_tip = self.learning_resources.get(related_skill.lower(), 
                        "Start with official documentation and build a small project to practice.")
                    
                    recommendations.append({
                        "skill": related_skill,
                        "reason": f"Often used together with {skill}",
                        "learning_tip": learning_tip,
                        "priority": "high" if len(recommendations) < 5 else "medium"
                    })
        
        return recommendations[:10]  # Return top 10 recommendations
    
    def get_learning_path(self, skill: str) -> Dict:
        """
        Get learning path for a specific skill
        
        Args:
            skill: Skill name
        
        Returns:
            Learning path information
        """
        skill_lower = skill.lower()
        
        # Find related skills
        related = []
        for key, values in self.skill_relationships.items():
            if key in skill_lower:
                related = values
                break
        
        learning_tip = self.learning_resources.get(skill_lower, 
            "Start with the official documentation and build a practical project.")
        
        return {
            "skill": skill,
            "related_skills": related[:5],
            "learning_tip": learning_tip,
            "suggested_projects": self._get_suggested_projects(skill_lower)
        }
    
    def _get_suggested_projects(self, skill: str) -> List[str]:
        """Get suggested projects for learning a skill"""
        project_suggestions = {
            "python": ["Build a web scraper", "Create a REST API", "Build a data analysis dashboard"],
            "javascript": ["Build a todo app", "Create a weather app", "Build a calculator"],
            "react": ["Build a portfolio website", "Create a blog app", "Build a task manager"],
            "aws": ["Deploy a static website", "Set up a CI/CD pipeline", "Create a serverless function"],
            "docker": ["Containerize a web app", "Set up a multi-container app", "Deploy with Docker Compose"],
            "machine learning": ["Predict house prices", "Image classifier", "Sentiment analysis"],
            "data science": ["Analyze a dataset", "Create visualizations", "Build a dashboard"]
        }
        
        for key, projects in project_suggestions.items():
            if key in skill:
                return projects
        
        return ["Build a small project", "Follow a tutorial", "Contribute to open source"]



