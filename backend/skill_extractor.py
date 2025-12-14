"""
Skill Extractor Module
Extracts skills from resume and job description using NLP
"""

import re
from typing import List, Set
import spacy


class SkillExtractor:
    """Extract technical and soft skills from text"""
    
    def __init__(self):
        # Common technical skills database
        self.technical_skills = {
            # Programming Languages
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'c', 'go', 'rust',
            'kotlin', 'swift', 'php', 'ruby', 'scala', 'r', 'matlab', 'perl', 'shell',
            'bash', 'powershell', 'sql', 'html', 'css', 'sass', 'less',
            
            # Web Technologies
            'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'fastapi',
            'spring', 'asp.net', 'laravel', 'symfony', 'rails', 'next.js', 'nuxt.js',
            'graphql', 'rest api', 'soap', 'microservices', 'docker', 'kubernetes',
            
            # Databases
            'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sqlite', 'cassandra',
            'elasticsearch', 'dynamodb', 'neo4j', 'firebase', 'supabase',
            
            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'google cloud', 'terraform', 'ansible', 'jenkins',
            'ci/cd', 'git', 'github', 'gitlab', 'bitbucket', 'jira', 'confluence',
            
            # Data Science & ML
            'machine learning', 'deep learning', 'neural networks', 'tensorflow', 'pytorch',
            'scikit-learn', 'pandas', 'numpy', 'matplotlib', 'seaborn', 'jupyter',
            'data analysis', 'data visualization', 'statistics', 'nlp', 'computer vision',
            
            # Mobile Development
            'android', 'ios', 'react native', 'flutter', 'xamarin', 'ionic',
            
            # Other Technologies
            'linux', 'unix', 'windows', 'agile', 'scrum', 'kanban', 'devops',
            'api development', 'web development', 'software development', 'testing',
            'unit testing', 'integration testing', 'selenium', 'cypress', 'jest'
        }
        
        # Soft skills
        self.soft_skills = {
            'leadership', 'communication', 'teamwork', 'problem solving', 'critical thinking',
            'time management', 'project management', 'collaboration', 'adaptability',
            'creativity', 'analytical', 'detail-oriented', 'self-motivated', 'mentoring',
            'presentation', 'negotiation', 'customer service', 'agile methodology'
        }
        
        # Try to load spaCy model, fallback to basic extraction if not available
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy model not found. Using basic extraction.")
            self.nlp = None
    
    def extract_skills(self, text: str) -> List[str]:
        """
        Extract skills from text
        
        Args:
            text: Input text (resume or job description)
        
        Returns:
            List of extracted skills
        """
        if not text:
            return []
        
        text_lower = text.lower()
        found_skills = set()
        
        # Extract technical skills
        for skill in self.technical_skills:
            # Use word boundaries for better matching
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower, re.IGNORECASE):
                found_skills.add(skill.title())
        
        # Extract soft skills
        for skill in self.soft_skills:
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower, re.IGNORECASE):
                found_skills.add(skill.title())
        
        # Use NLP for additional skill extraction if available
        if self.nlp:
            doc = self.nlp(text)
            # Extract noun phrases that might be skills
            for chunk in doc.noun_chunks:
                chunk_text = chunk.text.lower().strip()
                if len(chunk_text) > 2 and len(chunk_text) < 30:
                    # Check if it matches known skills
                    for skill in self.technical_skills | self.soft_skills:
                        if skill.lower() in chunk_text or chunk_text in skill.lower():
                            found_skills.add(skill.title())
        
        return sorted(list(found_skills))



