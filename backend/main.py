"""
Career-IQ Backend API
FastAPI server for resume analysis and job matching with authentication

IMPORTANT: To run this server:
    1. Make sure you're in the backend directory
    2. Install dependencies: pip install -r requirements.txt
    3. Run the server: python main.py
    4. Server will start on http://localhost:8000
    5. Keep this terminal window open while using the application

The frontend requires this backend to be running to function properly.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from typing import Optional, Any
import numpy as np
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from resume_parser import ResumeParser
from skill_extractor import SkillExtractor
from matcher import ResumeJobMatcher
from auth import AuthManager
from email_service import EmailService
from llm_service import LLMService
from role_advisor import RoleAdvisor

app = FastAPI(title="Career-IQ API", version="2.0.0")

# CORS middleware to allow frontend requests
# Get allowed origins from environment or use defaults
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "https://career-iq.vercel.app",
    "https://career-iq.netlify.app",
    "https://*.vercel.app",
    "https://*.netlify.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
resume_parser = ResumeParser()
skill_extractor = SkillExtractor()
matcher = ResumeJobMatcher()
auth_manager = AuthManager()
email_service = EmailService()
llm_service = LLMService()
role_advisor = RoleAdvisor(llm_service)

# Create uploads directory if it doesn't exist (relative to backend folder)
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)


def convert_to_json_serializable(obj: Any) -> Any:
    """
    Convert numpy types and other non-JSON-serializable types to native Python types
    
    Args:
        obj: Object that may contain numpy types
        
    Returns:
        Object with all numpy types converted to native Python types
    """
    if isinstance(obj, (np.integer, np.floating)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_json_serializable(item) for item in obj]
    else:
        return obj


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Career-IQ API is running", "version": "2.0.0"}


@app.post("/api/register")
async def register(
    email: str = Form(...),
    password: str = Form(...),
    name: str = Form(...)
):
    """
    Register a new user
    
    Args:
        email: User email
        password: User password
        name: User full name
    
    Returns:
        Registration result
    """
    try:
        result = auth_manager.register(email, password, name)
        if result["success"]:
            return JSONResponse(content=result, status_code=201)
        else:
            return JSONResponse(content=result, status_code=400)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration error: {str(e)}")


@app.post("/api/login")
async def login(
    email: str = Form(...),
    password: str = Form(...)
):
    """
    Login user and send email notification
    
    Args:
        email: User email
        password: User password
    
    Returns:
        Login result with session token
    """
    try:
        result = auth_manager.login(email, password)
        
        if result["success"]:
            # Send login notification email (non-blocking)
            # Don't let email failures prevent successful login
            try:
                email_sent = email_service.send_login_notification(
                    result["user"]["email"],
                    result["user"]["name"]
                )
                if email_sent:
                    print(f"✓ Login notification email sent to {result['user']['email']}")
                else:
                    print(f"⚠ Login notification email failed for {result['user']['email']} (login still successful)")
            except Exception as email_error:
                # Log error but don't fail the login
                print(f"⚠ Warning: Failed to send login notification email: {str(email_error)}")
                print(f"   Login was successful, but email notification could not be sent")
            
            return JSONResponse(content=result)
        else:
            return JSONResponse(content=result, status_code=401)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")


@app.get("/api/verify")
async def verify_session(
    authorization: Optional[str] = Header(None)
):
    """
    Verify session token
    
    Args:
        authorization: Bearer token in header
    
    Returns:
        User info if session is valid
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    session_token = authorization.replace("Bearer ", "")
    user = auth_manager.verify_session(session_token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    return JSONResponse(content={"success": True, "user": user})


@app.post("/api/logout")
async def logout(
    authorization: Optional[str] = Header(None)
):
    """
    Logout user
    
    Args:
        authorization: Bearer token in header
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    session_token = authorization.replace("Bearer ", "")
    auth_manager.logout(session_token)
    
    return JSONResponse(content={"success": True, "message": "Logged out successfully"})


@app.post("/api/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    authorization: Optional[str] = Header(None)
):
    """
    Analyze resume and match with job description
    
    Args:
        resume: Uploaded resume file (PDF or DOCX)
        job_description: Job description text
        authorization: Optional Bearer token for authenticated users
    
    Returns:
        JSON with match score, skills, structured resume data, and recommendations
    """
    try:
        # Optional: Verify session if token provided
        user = None
        if authorization and authorization.startswith("Bearer "):
            session_token = authorization.replace("Bearer ", "")
            user = auth_manager.verify_session(session_token)
        
        # Validate file type
        if not resume.filename:
            raise HTTPException(status_code=400, detail="No file uploaded")
        
        file_ext = os.path.splitext(resume.filename)[1].lower()
        if file_ext not in ['.pdf', '.docx', '.doc']:
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type. Please upload PDF or DOCX file"
            )
        
        # Save uploaded file
        file_path = os.path.join(UPLOADS_DIR, resume.filename)
        with open(file_path, "wb") as buffer:
            content = await resume.read()
            buffer.write(content)
        
        # Parse resume - get both text and structured data
        resume_text = resume_parser.parse(file_path)
        if not resume_text:
            raise HTTPException(
                status_code=400, 
                detail="Failed to extract text from resume"
            )
        
        # Get structured resume data
        structured_data = resume_parser.parse_structured(file_path)
        
        # Extract skills from resume and job description
        resume_skills = skill_extractor.extract_skills(resume_text)
        job_skills = skill_extractor.extract_skills(job_description)
        
        # Calculate match score and get recommendations
        match_result = matcher.match(resume_text, job_description, resume_skills, job_skills)
        
        # Role-based analysis
        detected_role = role_advisor.detect_role(job_description, resume_text)
        role_skills = await role_advisor.generate_role_skills(detected_role)
        skill_gaps = await role_advisor.analyze_skill_gaps(resume_skills, role_skills)
        roadmap = await role_advisor.generate_roadmap(
            detected_role, 
            skill_gaps, 
            resume_skills, 
            match_result.get("match_score", 0)
        )
        
        # Combine results
        result = {
            **match_result,
            "resume_data": structured_data,
            "resume_text": resume_text[:500] + "..." if len(resume_text) > 500 else resume_text,  # Preview
            # Role-based advisor data
            "role_analysis": {
                "detected_role": detected_role,
                "role_skills": role_skills,
                "skill_gaps": skill_gaps,
                "roadmap": roadmap
            }
        }
        
        # Convert any numpy types to native Python types for JSON serialization
        result = convert_to_json_serializable(result)
        
        # Clean up uploaded file
        try:
            os.remove(file_path)
        except:
            pass
        
        return JSONResponse(content=result)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    # Get port from environment (for Render/Railway) or default to 8000
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
