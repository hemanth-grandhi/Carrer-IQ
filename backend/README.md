# Career-IQ Backend

FastAPI backend for Career-IQ resume analysis system.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Set up environment variables
cp ../env.example.txt .env
# Edit .env with your API keys

# Run the server
python main.py
```

Server runs on `http://localhost:8000`

## 📁 Structure

- `main.py` - FastAPI application and routes
- `auth.py` - User authentication and session management
- `email_service.py` - Email notifications (SMTP + EmailJS)
- `resume_parser.py` - Resume parsing (PDF/DOCX)
- `skill_extractor.py` - Skill extraction using NLP
- `matcher.py` - Resume-job matching with AI
- `advanced_analyzer.py` - Deep resume analysis
- `smart_suggestions.py` - Actionable suggestions
- `learning_roadmap.py` - Learning roadmap generation
- `ai_service.py` - Free AI API integration

## 🔧 Environment Variables

See `../env.example.txt` for all required variables.

## 📚 API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## 🧪 Testing

```bash
# Test health endpoint
curl http://localhost:8000/health
```

## 🚀 Deployment

See `../DEPLOYMENT.md` for production deployment instructions.

