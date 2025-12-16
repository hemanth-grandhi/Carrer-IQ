# Career-IQ Frontend

Modern, responsive frontend for Career-IQ.

## 🚀 Quick Start

### Option 1: Direct File Access
Simply open `index.html` in your web browser.

### Option 2: Local Server
```bash
# Using Python
python -m http.server 8080

# Using Node.js (if installed)
npx serve .
```

Visit `http://localhost:8080`

## 📁 Structure

- `index.html` - Landing page
- `login.html` - Login page
- `signup.html` - Signup page
- `dashboard.html` - Main analysis dashboard
- `style.css` - Global stylesheet
- `script.js` - Frontend JavaScript
- `config.js` - API URL configuration
- `404.html` - Error page

## ⚙️ Configuration

Update `config.js` to set the backend API URL:

```javascript
window.API_BASE_URL = 'https://your-backend-url.onrender.com';
```

For local development, it auto-detects `localhost:8000`.

## 🎨 Features

- Responsive design (mobile + desktop)
- Modern UI with smooth animations
- Real-time analysis results
- Advanced AI insights display
- Error handling and loading states

## 🚀 Deployment

Deploy to Vercel or Netlify - see `../DEPLOYMENT.md` for instructions.


