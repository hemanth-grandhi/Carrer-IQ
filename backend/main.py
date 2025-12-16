"""
Career-IQ Backend API
FastAPI server for resume analysis and job matching with authentication
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
import uvicorn
import os
from typing import Optional, Any
import numpy as np
from dotenv import load_dotenv

load_dotenv()

from resume_parser import ResumeParser
from skill_extractor import SkillExtractor
from matcher import ResumeJobMatcher
from auth import AuthManager
from email_service import EmailService
from llm_service import LLMService
from role_advisor import RoleAdvisor

app = FastAPI(title="Career-IQ API", version="2.0.0")

allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

resume_parser = ResumeParser()
skill_extractor = SkillExtractor()
matcher = ResumeJobMatcher()
auth_manager = AuthManager()
email_service = EmailService()
llm_service = LLMService()
role_advisor = RoleAdvisor(llm_service)

UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)


def convert_to_json_serializable(obj: Any) -> Any:
    if isinstance(obj, (np.integer, np.floating)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_to_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_json_serializable(i) for i in obj]
    return obj


# ✅ ROOT REDIRECT (FIXED)
@app.get("/")
async def root():
    return RedirectResponse(url="http://localhost:8080/index.html")


# ✅ CALLBACK ROUTE (MAIN FIX)
@app.get("/callback")
async def auth_callback(code: Optional[str] = None, state: Optional[str] = None):
    return RedirectResponse(url="http://localhost:8080/dashboard.html")


@app.post("/api/register")
async def register(
    email: str = Form(...),
    password: str = Form(...),
    name: str = Form(...)
):
    result = auth_manager.register(email, password, name)
    if result["success"]:
        return JSONResponse(content=result, status_code=201)
    return JSONResponse(content=result, status_code=400)


@app.post("/api/login")
async def login(
    email: str = Form(...),
    password: str = Form(...)
):
    result = auth_manager.login(email, password)
    if result["success"]:
        try:
            email_service.send_login_notification(
                result["user"]["email"],
                result["user"]["name"]
            )
        except:
            pass
        return JSONResponse(content=result)
    return JSONResponse(content=result, status_code=401)


@app.get("/api/verify")
async def verify_session(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token")

    token = authorization.replace("Bearer ", "")
    user = auth_manager.verify_session(token)

    if not user:
        raise HTTPException(status_code=401, detail="Session expired")

    return {"success": True, "user": user}


@app.post("/api/logout")
async def logout(authorization: Optional[str] = Header(None)):
    token = authorization.replace("Bearer ", "")
    auth_manager.logout(token)
    return {"success": True}


@app.post("/api/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    authorization: Optional[str] = Header(None)
):
    if not resume.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    file_ext = os.path.splitext(resume.filename)[1].lower()
    if file_ext not in [".pdf", ".docx", ".doc"]:
        raise HTTPException(status_code=400, detail="Invalid file type")

    file_path = os.path.join(UPLOADS_DIR, resume.filename)
    with open(file_path, "wb") as f:
        f.write(await resume.read())

    resume_text = resume_parser.parse(file_path)
    structured_data = resume_parser.parse_structured(file_path)

    resume_skills = skill_extractor.extract_skills(resume_text)
    job_skills = skill_extractor.extract_skills(job_description)

    match_result = matcher.match(resume_text, job_description, resume_skills, job_skills)

    detected_role = role_advisor.detect_role(job_description, resume_text)
    role_skills = await role_advisor.generate_role_skills(detected_role)
    skill_gaps = await role_advisor.analyze_skill_gaps(resume_skills, role_skills)
    roadmap = await role_advisor.generate_roadmap(
        detected_role, skill_gaps, resume_skills, match_result.get("match_score", 0)
    )

    result = {
        **match_result,
        "resume_data": structured_data,
        "role_analysis": {
            "detected_role": detected_role,
            "role_skills": role_skills,
            "skill_gaps": skill_gaps,
            "roadmap": roadmap
        }
    }

    os.remove(file_path)
    return convert_to_json_serializable(result)


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
