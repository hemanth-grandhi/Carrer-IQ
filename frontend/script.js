/**
 * Career-IQ Frontend JavaScript
 * Handles authentication, form submissions, API calls, and UI interactions
 */

// API URL - automatically detects environment
// Uses config.js for production URL, falls back to localhost in development
const API_BASE_URL = (() => {
    // Check if config.js set the URL
    if (window.API_BASE_URL && window.API_BASE_URL !== 'https://career-iq-backend.onrender.com') {
        return window.API_BASE_URL;
    }
    // Development mode
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return 'http://localhost:8000';
    }
    // Production - use config.js value or default
    return window.API_BASE_URL || 'https://career-iq-backend.onrender.com';
})();

// Session management
function getSessionToken() {
    return localStorage.getItem('session_token');
}

function setSessionToken(token) {
    localStorage.setItem('session_token', token);
}

function clearSession() {
    localStorage.removeItem('session_token');
    localStorage.removeItem('user_name');
    localStorage.removeItem('user_email');
}

function getUserInfo() {
    return {
        name: localStorage.getItem('user_name'),
        email: localStorage.getItem('user_email')
    };
}

// Display user name on dashboard
function displayUserName() {
    const userName = localStorage.getItem('user_name');
    const userInfoEl = document.getElementById('userInfo');
    const userNameEl = document.getElementById('userName');
    
    if (userInfoEl && userNameEl) {
        if (userName) {
            userNameEl.textContent = `Welcome, ${userName}`;
            userInfoEl.style.display = 'block';
        } else {
            userInfoEl.style.display = 'none';
        }
    }
}

// Initialize on page load
// IMPORTANT: Ensure backend server is running (cd backend && python main.py)
document.addEventListener('DOMContentLoaded', function() {
    initializePage();
    checkAuth();
    
    // Check backend connection on page load
    checkBackendConnection();
    
    // Handle smooth scroll for About link
    initializeSmoothScroll();
});

function checkAuth() {
    // Check if user is on dashboard and has session
    if (window.location.pathname.includes('dashboard.html')) {
        const token = getSessionToken();
        if (!token) {
            window.location.href = 'login.html';
            return;
        }
        
        // Display user name
        displayUserName();
        
        // Verify session
        verifySession(token);
    }
}

async function verifySession(token) {
    if (!token) {
        clearSession();
        window.location.href = 'login.html';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/verify`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            clearSession();
            window.location.href = 'login.html';
            return;
        }
        
        const result = await response.json();
        if (!result.success) {
            clearSession();
            window.location.href = 'login.html';
        } else {
            // Update user name from session if available
            if (result.user && result.user.name) {
                localStorage.setItem('user_name', result.user.name);
                displayUserName();
            }
        }
    } catch (error) {
        console.error('Session verification failed:', error);
        // On network error, don't redirect - might be temporary connection issue
        // Only redirect if it's an authentication error
        if (error.message && !error.message.includes('Failed to fetch')) {
            clearSession();
            window.location.href = 'login.html';
        }
    }
}

function initializePage() {
    // Handle login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Handle signup form
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', handleSignup);
    }
    
    // Handle analysis form
    const analysisForm = document.getElementById('analysisForm');
    if (analysisForm) {
        analysisForm.addEventListener('submit', handleAnalysis);
        
        // Handle file input change
        const fileInput = document.getElementById('resumeFile');
        if (fileInput) {
            fileInput.addEventListener('change', handleFileSelect);
        }
    }
    
    // Handle logout
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
}

// Handle file selection
function handleFileSelect(event) {
    const file = event.target.files[0];
    const fileNameSpan = document.getElementById('fileName');
    
    if (file && fileNameSpan) {
        fileNameSpan.textContent = `Selected: ${file.name}`;
    }
}

// Handle signup
async function handleSignup(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const password = formData.get('password');
    const confirmPassword = formData.get('confirmPassword');
    const name = formData.get('name');
    const email = formData.get('email');
    
    // Debug logging
    console.log('Signup attempt:', { name, email, hasPassword: !!password });
    
    // Validate required fields
    if (!name || !email || !password) {
        alert('Please fill in all required fields.');
        return;
    }
    
    // Validate passwords match
    if (password !== confirmPassword) {
        alert('Passwords do not match!');
        return;
    }
    
    // Create new FormData with correct field names
    const submitData = new FormData();
    submitData.append('name', name);
    submitData.append('email', email);
    submitData.append('password', password);
    
    try {
        console.log('Sending request to:', `${API_BASE_URL}/api/register`);
        
        const response = await fetch(`${API_BASE_URL}/api/register`, {
            method: 'POST',
            body: submitData
        });
        
        console.log('Response status:', response.status, response.statusText);
        
        // Try to get response text first for debugging
        const responseText = await response.text();
        console.log('Response text:', responseText);
        
        let result;
        try {
            result = JSON.parse(responseText);
        } catch (parseError) {
            console.error('Failed to parse JSON:', parseError);
            alert(`Registration failed: Server returned invalid response. Status: ${response.status}\n\nMake sure the backend server is running on port 8000.`);
            return;
        }
        
        console.log('Parsed result:', result);
        
        // Check if response is ok
        if (!response.ok) {
            const errorMsg = result.message || result.detail || `Server error (${response.status})`;
            console.error('Registration failed:', errorMsg);
            alert(`Registration failed: ${errorMsg}`);
            return;
        }
        
        if (result.success) {
            alert('Account created successfully! Please login.');
            window.location.href = 'login.html';
        } else {
            alert(`Registration failed: ${result.message || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Signup error:', error);
        console.error('Error details:', {
            message: error.message,
            stack: error.stack,
            name: error.name
        });
        
        if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
            alert(`Registration failed: Cannot connect to server.\n\nMake sure the backend server is running:\n1. Open terminal\n2. cd backend\n3. python main.py\n\nThen try again.`);
        } else {
            alert(`Registration failed: ${error.message || 'Please check your connection and try again.'}`);
        }
    }
}

// Handle login
// NOTE: Make sure the backend server is running before attempting to login!
// To start the backend: cd backend && python main.py
async function handleLogin(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const email = formData.get('email');
    const password = formData.get('password');
    
    // Validate inputs on frontend
    if (!email || !email.trim()) {
        alert('Please enter your email address.');
        return;
    }
    
    if (!password || !password.trim()) {
        alert('Please enter your password.');
        return;
    }
    
    // Disable submit button to prevent double submission
    const submitBtn = event.target.querySelector('button[type="submit"]');
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Logging in...';
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/login`, {
            method: 'POST',
            body: formData
        });
        
        let result;
        try {
            result = await response.json();
        } catch (parseError) {
            // If response is not JSON, try to get text
            const text = await response.text().catch(() => 'Unknown error');
            alert(`Login failed: ${text || 'Server returned invalid response. Please check your connection.'}`);
            return;
        }
        
        // Check if response is ok
        if (!response.ok) {
            const errorMsg = result.message || result.detail || `Server error (${response.status})`;
            alert(`Login failed: ${errorMsg}`);
            return;
        }
        
        if (result.success) {
            // Validate that we have a session token
            if (!result.session_token) {
                alert('Login failed: No session token received. Please try again.');
                return;
            }
            
            // Store session token and user info
            setSessionToken(result.session_token);
            if (result.user) {
                localStorage.setItem('user_name', result.user.name || '');
                localStorage.setItem('user_email', result.user.email || email);
            }
            
            alert('Login successful! Redirecting to dashboard...');
            window.location.href = 'dashboard.html';
        } else {
            alert(`Login failed: ${result.message || 'Invalid email or password'}`);
        }
    } catch (error) {
        console.error('Login error:', error);
        if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
            // Show backend notice if hidden
            const backendNotice = document.getElementById('backendNotice');
            if (backendNotice) {
                backendNotice.style.display = 'block';
            }
            alert(`❌ Cannot connect to backend server!\n\n⚠️ IMPORTANT: Start the backend server first:\n\n📋 EASY WAY (Windows):\n   Double-click: start_backend.bat\n\n📋 MANUAL WAY:\n   1. Open terminal/command prompt\n   2. Navigate to backend folder:\n      cd backend\n   3. Run the server:\n      python main.py\n   4. Wait for "Application startup complete"\n   5. Then try logging in again\n\n✅ Server should run on: http://localhost:8000`);
        } else {
            alert(`Login failed: ${error.message || 'An unexpected error occurred. Please try again.'}`);
        }
    } finally {
        // Re-enable submit button
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Login';
        }
    }
}

// Handle resume analysis
async function handleAnalysis(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const resumeFile = formData.get('resume');
    const jobDescription = formData.get('jobDescription');
    
    // Validate inputs
    if (!resumeFile || resumeFile.size === 0) {
        alert('Please select a resume file');
        return;
    }
    
    if (!jobDescription || jobDescription.trim().length === 0) {
        alert('Please enter a job description');
        return;
    }
    
    // Show loading state
    const analyzeBtn = document.getElementById('analyzeBtn');
    const btnText = analyzeBtn.querySelector('.btn-text');
    const btnLoader = analyzeBtn.querySelector('.btn-loader');
    
    analyzeBtn.disabled = true;
    if (btnText) btnText.style.display = 'none';
    if (btnLoader) btnLoader.style.display = 'inline-block';
    
    try {
        // Prepare form data for API
        const apiFormData = new FormData();
        apiFormData.append('resume', resumeFile);
        apiFormData.append('job_description', jobDescription);
        
        // Add authorization header if logged in
        const headers = {};
        const token = getSessionToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        // Make API call
        const response = await fetch(`${API_BASE_URL}/api/analyze`, {
            method: 'POST',
            headers: headers,
            body: apiFormData
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Analysis failed');
        }
        
        const result = await response.json();
        displayResults(result);
        
    } catch (error) {
        console.error('Analysis error:', error);
        alert(`Error: ${error.message}\n\nMake sure the backend server is running on port 8000.`);
    } finally {
        // Reset button state
        analyzeBtn.disabled = false;
        if (btnText) btnText.style.display = 'inline-block';
        if (btnLoader) btnLoader.style.display = 'none';
    }
}

// Display analysis results
function displayResults(result) {
    // Show results section
    const resultsSection = document.getElementById('resultsSection');
    if (resultsSection) {
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    // Display resume data if available
    if (result.resume_data) {
        displayResumeData(result.resume_data);
    }
    
    // Update match score
    const matchScore = document.getElementById('matchScore');
    if (matchScore) {
        matchScore.textContent = `${result.match_score}%`;
        
        // Update score circle color
        const scoreCircle = matchScore.closest('.score-circle');
        if (scoreCircle) {
            if (result.match_score >= 70) {
                scoreCircle.style.background = 'linear-gradient(135deg, #10b981, #059669)';
            } else if (result.match_score >= 50) {
                scoreCircle.style.background = 'linear-gradient(135deg, #f59e0b, #d97706)';
            } else {
                scoreCircle.style.background = 'linear-gradient(135deg, #ef4444, #dc2626)';
            }
        }
    }
    
    // Display matched skills
    const matchedSkills = document.getElementById('matchedSkills');
    if (matchedSkills) {
        matchedSkills.innerHTML = '';
        if (result.matched_skills && result.matched_skills.length > 0) {
            result.matched_skills.forEach(skill => {
                const tag = document.createElement('span');
                tag.className = 'skill-tag';
                tag.textContent = skill;
                matchedSkills.appendChild(tag);
            });
        } else {
            matchedSkills.innerHTML = '<p style="color: var(--text-secondary);">No matching skills found</p>';
        }
    }
    
    // Display missing skills
    const missingSkills = document.getElementById('missingSkills');
    if (missingSkills) {
        missingSkills.innerHTML = '';
        if (result.missing_skills && result.missing_skills.length > 0) {
            result.missing_skills.forEach(skill => {
                const tag = document.createElement('span');
                tag.className = 'skill-tag';
                tag.textContent = skill;
                missingSkills.appendChild(tag);
            });
        } else {
            missingSkills.innerHTML = '<p style="color: var(--text-secondary);">No missing skills - great match!</p>';
        }
    }
    
    // Display extra skills
    const extraSkills = document.getElementById('extraSkills');
    if (extraSkills) {
        extraSkills.innerHTML = '';
        if (result.extra_skills && result.extra_skills.length > 0) {
            result.extra_skills.forEach(skill => {
                const tag = document.createElement('span');
                tag.className = 'skill-tag';
                tag.textContent = skill;
                extraSkills.appendChild(tag);
            });
        } else {
            extraSkills.innerHTML = '<p style="color: var(--text-secondary);">No additional skills</p>';
        }
    }
    
    // Update skill counts
    const matchedCount = document.getElementById('matchedCount');
    if (matchedCount) matchedCount.textContent = result.matched_skill_count || 0;
    
    const missingCount = document.getElementById('missingCount');
    if (missingCount) missingCount.textContent = result.missing_skills?.length || 0;
    
    const extraCount = document.getElementById('extraCount');
    if (extraCount) extraCount.textContent = result.extra_skills?.length || 0;
    
    // Display detailed recommendations
    if (result.recommendations) {
        displayDetailedRecommendations(result.recommendations);
    }
    
    // Display skill recommendations
    if (result.skill_recommendations) {
        displaySkillRecommendations(result.skill_recommendations);
    }
    
    // Display Advanced Analysis (NEW - Highly Intelligent)
    if (result.advanced_analysis) {
        displayAdvancedAnalysis(result.advanced_analysis);
    }
    
    // Display Smart Suggestions
    if (result.smart_suggestions) {
        displaySmartSuggestions(result.smart_suggestions);
    }
    
    // Display Learning Roadmap
    if (result.learning_roadmap) {
        displayLearningRoadmapAdvanced(result.learning_roadmap);
    }
    
    // Display AI-enhanced features (legacy) - only if we have real AI analysis
    if (result.ai_enabled) {
        // Only show AI analysis if it's meaningful (not fallback)
        if (result.ai_analysis && 
            result.ai_analysis.overall_assessment && 
            !result.ai_analysis.overall_assessment.includes("unavailable") &&
            !result.ai_analysis.overall_assessment.includes("rule-based")) {
            displayAIAnalysis(result.ai_analysis);
        }
        if (result.role_analysis) {
            displayRoleAnalysis(result.role_analysis);
        }
        if (result.resume_improvement && 
            result.resume_improvement.parsed !== false &&
            !result.resume_improvement.response?.includes("unavailable")) {
            displayResumeImprovement(result.resume_improvement);
        }
    }
}

// Display structured resume data
function displayResumeData(resumeData) {
    const resumeDataSection = document.getElementById('resumeDataSection');
    if (!resumeDataSection) return;
    
    let html = '<div class="resume-data-grid">';
    
    // Education
    if (resumeData.education && resumeData.education.length > 0) {
        html += '<div class="resume-data-card"><h4>🎓 Education</h4><ul>';
        resumeData.education.forEach(edu => {
            html += `<li><strong>${edu.degree || 'N/A'}</strong><br>${edu.institution || 'N/A'}</li>`;
        });
        html += '</ul></div>';
    }
    
    // Experience
    if (resumeData.experience && resumeData.experience.length > 0) {
        html += '<div class="resume-data-card"><h4>💼 Experience</h4><ul>';
        resumeData.experience.forEach(exp => {
            html += `<li><strong>${exp.title || 'N/A'}</strong><br>${exp.company || 'N/A'}<br><small>${exp.duration || 'N/A'}</small></li>`;
        });
        html += '</ul></div>';
    }
    
    // Skills
    if (resumeData.skills && resumeData.skills.length > 0) {
        html += '<div class="resume-data-card"><h4>🛠️ Skills</h4><div class="skills-list">';
        resumeData.skills.forEach(skill => {
            html += `<span class="skill-tag">${skill}</span>`;
        });
        html += '</div></div>';
    }
    
    // Projects
    if (resumeData.projects && resumeData.projects.length > 0) {
        html += '<div class="resume-data-card"><h4>🚀 Projects</h4><ul>';
        resumeData.projects.forEach(proj => {
            html += `<li><strong>${proj.name || 'N/A'}</strong><br><small>${proj.description || 'N/A'}</small></li>`;
        });
        html += '</ul></div>';
    }
    
    html += '</div>';
    resumeDataSection.innerHTML = html;
}

// Display detailed recommendations
function displayDetailedRecommendations(recommendations) {
    const recommendationsList = document.getElementById('recommendationsList');
    if (!recommendationsList) return;
    
    recommendationsList.innerHTML = '';
    
    // Summary
    if (recommendations.summary) {
        const summaryLi = document.createElement('li');
        summaryLi.className = 'recommendation-summary';
        summaryLi.innerHTML = `<strong>📊 Summary:</strong> ${recommendations.summary}`;
        recommendationsList.appendChild(summaryLi);
    }
    
    // Resume changes
    if (recommendations.resume_changes && recommendations.resume_changes.length > 0) {
        const sectionHeader = document.createElement('li');
        sectionHeader.innerHTML = '<strong>✏️ Resume Changes Needed:</strong>';
        sectionHeader.style.marginTop = '1rem';
        recommendationsList.appendChild(sectionHeader);
        
        recommendations.resume_changes.forEach(change => {
            const li = document.createElement('li');
            li.style.marginLeft = '1.5rem';
            li.innerHTML = `<strong>${change.title}:</strong> ${change.description}<br><em>Action: ${change.action}</em>`;
            recommendationsList.appendChild(li);
        });
    }
    
    // Skill improvements
    if (recommendations.skill_improvements && recommendations.skill_improvements.length > 0) {
        const sectionHeader = document.createElement('li');
        sectionHeader.innerHTML = '<strong>📚 Skills to Learn:</strong>';
        sectionHeader.style.marginTop = '1rem';
        recommendationsList.appendChild(sectionHeader);
        
        recommendations.skill_improvements.forEach(improvement => {
            const li = document.createElement('li');
            li.style.marginLeft = '1.5rem';
            li.innerHTML = `<strong>${improvement.skill}:</strong><br>${improvement.action_plan.replace(/\n/g, '<br>')}`;
            recommendationsList.appendChild(li);
        });
    }
    
    // Strengthen existing
    if (recommendations.strengthen_existing && recommendations.strengthen_existing.length > 0) {
        const sectionHeader = document.createElement('li');
        sectionHeader.innerHTML = '<strong>💪 Strengthen Your Existing Skills:</strong>';
        sectionHeader.style.marginTop = '1rem';
        recommendationsList.appendChild(sectionHeader);
        
        recommendations.strengthen_existing.forEach(item => {
            const li = document.createElement('li');
            li.style.marginLeft = '1.5rem';
            li.innerHTML = item.how_to_strengthen.replace(/\n/g, '<br>');
            recommendationsList.appendChild(li);
        });
    }
    
    // General tips
    if (recommendations.general_tips && recommendations.general_tips.length > 0) {
        const sectionHeader = document.createElement('li');
        sectionHeader.innerHTML = '<strong>💡 General Tips:</strong>';
        sectionHeader.style.marginTop = '1rem';
        recommendationsList.appendChild(sectionHeader);
        
        recommendations.general_tips.forEach(tip => {
            const li = document.createElement('li');
            li.style.marginLeft = '1.5rem';
            li.innerHTML = `<strong>${tip.tip}:</strong> ${tip.description}`;
            recommendationsList.appendChild(li);
        });
    }
}

// Display skill recommendations
function displaySkillRecommendations(skillRecs) {
    const skillRecSection = document.getElementById('skillRecommendationsSection');
    if (!skillRecSection) return;
    
    if (!skillRecs || skillRecs.length === 0) {
        skillRecSection.style.display = 'none';
        return;
    }
    
    skillRecSection.style.display = 'block';
    let html = '<h4>🔗 Recommended Skills to Learn</h4><div class="skill-recommendations-grid">';
    
    skillRecs.forEach(rec => {
        html += `
            <div class="skill-rec-card">
                <h5>${rec.skill}</h5>
                <p class="rec-reason">${rec.reason}</p>
                <p class="rec-tip"><strong>💡 Learning Tip:</strong> ${rec.learning_tip}</p>
                <span class="rec-priority priority-${rec.priority}">${rec.priority.toUpperCase()} PRIORITY</span>
            </div>
        `;
    });
    
    html += '</div>';
    skillRecSection.innerHTML = html;
}

// Display AI Analysis
function displayAIAnalysis(aiAnalysis) {
    const section = document.getElementById('aiAnalysisSection');
    if (!section || !aiAnalysis) return;
    
    // Hide section if AI is unavailable or showing fallback messages
    if (aiAnalysis.parsed === false || 
        !aiAnalysis.overall_assessment || 
        aiAnalysis.overall_assessment.includes("unavailable") ||
        aiAnalysis.overall_assessment.includes("rule-based") ||
        (aiAnalysis.strengths && aiAnalysis.strengths.length > 0 && 
         aiAnalysis.strengths[0].includes("Review your resume manually")) {
        section.style.display = 'none';
        return;
    }
    
    // Only show if we have meaningful AI analysis
    if (!aiAnalysis.overall_assessment && 
        (!aiAnalysis.strengths || aiAnalysis.strengths.length === 0) &&
        (!aiAnalysis.weaknesses || aiAnalysis.weaknesses.length === 0)) {
        section.style.display = 'none';
        return;
    }
    
    section.style.display = 'block';
    let html = '<h4>🤖 AI-Powered Analysis</h4><div class="ai-analysis-content">';
    
    if (aiAnalysis.overall_assessment && !aiAnalysis.overall_assessment.includes("unavailable")) {
        html += `<div class="ai-card"><h5>📊 Overall Assessment</h5><p>${aiAnalysis.overall_assessment}</p></div>`;
    }
    
    if (aiAnalysis.strengths && aiAnalysis.strengths.length > 0) {
        // Filter out generic fallback messages
        const realStrengths = aiAnalysis.strengths.filter(s => 
            !s.includes("Review your resume manually") && 
            !s.includes("Check skill alignment")
        );
        
        if (realStrengths.length > 0) {
            html += '<div class="ai-card"><h5>✅ Strengths</h5><ul>';
            realStrengths.forEach(strength => {
                html += `<li>${strength}</li>`;
            });
            html += '</ul></div>';
        }
    }
    
    if (aiAnalysis.weaknesses && aiAnalysis.weaknesses.length > 0) {
        // Filter out generic fallback messages
        const realWeaknesses = aiAnalysis.weaknesses.filter(w => 
            !w.includes("Check skill alignment") &&
            !w.includes("Review your resume manually")
        );
        
        if (realWeaknesses.length > 0) {
            html += '<div class="ai-card"><h5>⚠️ Areas for Improvement</h5><ul>';
            realWeaknesses.forEach(weakness => {
                html += `<li>${weakness}</li>`;
            });
            html += '</ul></div>';
        }
    }
    
    html += '</div>';
    
    // Only display if we have real content
    if (html.includes('<div class="ai-card">')) {
        section.innerHTML = html;
    } else {
        section.style.display = 'none';
    }
}

// Display Role Analysis
function displayRoleAnalysis(roleAnalysis) {
    const section = document.getElementById('roleAnalysisSection');
    if (!section || !roleAnalysis) return;
    
    section.style.display = 'block';
    let html = `<h4>🎯 Role Analysis: ${roleAnalysis.target_role || 'Software Engineer'}</h4>`;
    html += '<div class="role-analysis-content">';
    
    if (roleAnalysis.skill_gaps && roleAnalysis.skill_gaps.length > 0) {
        html += '<div class="role-card"><h5>📉 Skill Gaps</h5><div class="skills-list">';
        roleAnalysis.skill_gaps.forEach(skill => {
            html += `<span class="skill-tag">${skill}</span>`;
        });
        html += '</div></div>';
    }
    
    if (roleAnalysis.ai_recommendations && roleAnalysis.ai_recommendations.recommended_skills) {
        html += '<div class="role-card"><h5>💡 Recommended Skills</h5><ul>';
        roleAnalysis.ai_recommendations.recommended_skills.forEach(skill => {
            html += `<li>${skill}</li>`;
        });
        html += '</ul></div>';
    }
    
    html += '</div>';
    section.innerHTML = html;
}

// Display Learning Roadmap
function displayLearningRoadmap(roadmap) {
    const section = document.getElementById('learningRoadmapSection');
    if (!section || !roadmap || roadmap.parsed === false) return;
    
    section.style.display = 'block';
    let html = '<h4>🗺️ Learning Roadmap</h4><div class="roadmap-content">';
    
    if (roadmap.roadmap_steps && roadmap.roadmap_steps.length > 0) {
        html += '<ol class="roadmap-steps">';
        roadmap.roadmap_steps.forEach((step, index) => {
            const timeline = roadmap.estimated_timeline && roadmap.estimated_timeline[step] 
                ? ` (${roadmap.estimated_timeline[step]})` : '';
            html += `<li><strong>Step ${index + 1}: ${step}</strong>${timeline}</li>`;
        });
        html += '</ol>';
    } else if (roadmap.response) {
        html += `<p>${roadmap.response}</p>`;
    }
    
    html += '</div>';
    section.innerHTML = html;
}

// Display Advanced Analysis (NEW - Highly Intelligent)
function displayAdvancedAnalysis(analysis) {
    const section = document.getElementById('advancedAnalysisSection');
    if (!section) {
        // Create section if it doesn't exist
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) {
            const newSection = document.createElement('div');
            newSection.id = 'advancedAnalysisSection';
            newSection.className = 'advanced-analysis-section';
            resultsSection.insertBefore(newSection, resultsSection.firstChild);
        } else {
            return;
        }
    }
    
    const sectionEl = document.getElementById('advancedAnalysisSection');
    sectionEl.style.display = 'block';
    
    let html = '<div class="advanced-analysis-header"><h3>🧠 Deep Resume Analysis</h3>';
    html += `<p class="analysis-subtitle">Understanding your resume better than a human recruiter</p></div>`;
    
    // Role Readiness Score
    const readiness = analysis.role_readiness_score || {};
    html += `<div class="readiness-card">
        <div class="readiness-score">
            <div class="score-large">${readiness.score || 0}%</div>
            <div class="score-label">Role Readiness</div>
            <div class="readiness-level">${readiness.level || 'Assessing...'}</div>
        </div>
    </div>`;
    
    // Target Role & Experience
    html += `<div class="analysis-info">
        <div class="info-item"><strong>Target Role:</strong> ${analysis.target_role || 'Software Engineer'}</div>
        <div class="info-item"><strong>Experience Level:</strong> ${analysis.experience_level?.level || 'Mid'} (${analysis.experience_level?.description || ''})</div>
    </div>`;
    
    // Strengths
    const strengths = analysis.strengths || {};
    if (strengths.fundamentals && strengths.fundamentals.length > 0) {
        html += '<div class="analysis-section"><h4>✅ Resume Strengths</h4><div class="strengths-grid">';
        strengths.fundamentals.slice(0, 5).forEach(item => {
            html += `<div class="strength-item">
                <span class="strength-icon">✓</span>
                <div>
                    <strong>${item.skill}</strong>
                    <span class="priority-badge priority-${item.priority}">${item.priority.toUpperCase()}</span>
                </div>
            </div>`;
        });
        html += '</div></div>';
    }
    
    // Weaknesses & Skill Gaps
    const weaknesses = analysis.weaknesses || {};
    if (weaknesses.missing_fundamentals && weaknesses.missing_fundamentals.length > 0) {
        html += '<div class="analysis-section"><h4>❌ Skill Gaps</h4><div class="gaps-list">';
        weaknesses.missing_fundamentals.slice(0, 5).forEach(item => {
            html += `<div class="gap-item">
                <div class="gap-header">
                    <strong>${item.skill}</strong>
                    <span class="importance-badge importance-${item.priority}">${item.importance || 'Important'}</span>
                </div>
                <p class="gap-reason">${item.why_important || ''}</p>
            </div>`;
        });
        html += '</div></div>';
    }
    
    // Resume Structure Quality
    const structure = analysis.resume_structure || {};
    html += `<div class="analysis-section"><h4>📋 Resume Structure Quality</h4>`;
    html += `<div class="structure-score">Score: ${structure.score || 0}/100 - ${structure.quality || 'Good'}</div>`;
    if (structure.issues && structure.issues.length > 0) {
        html += '<ul class="structure-issues">';
        structure.issues.forEach(issue => {
            html += `<li>${issue}</li>`;
        });
        html += '</ul>';
    }
    html += '</div>';
    
    html += '</div>';
    sectionEl.innerHTML = html;
}

// Display Smart Suggestions
function displaySmartSuggestions(suggestions) {
    const section = document.getElementById('smartSuggestionsSection');
    if (!section) {
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) {
            const newSection = document.createElement('div');
            newSection.id = 'smartSuggestionsSection';
            newSection.className = 'smart-suggestions-section';
            resultsSection.appendChild(newSection);
        } else return;
    }
    
    const sectionEl = document.getElementById('smartSuggestionsSection');
    sectionEl.style.display = 'block';
    
    let html = '<h3>💡 Smart Suggestions</h3>';
    html += '<p class="section-subtitle">Actionable steps to improve your resume and skills</p>';
    
    // Skills to Add
    if (suggestions.skills_to_add && suggestions.skills_to_add.length > 0) {
        html += '<div class="suggestion-category"><h4>🛠️ Skills to Add</h4><div class="suggestions-grid">';
        suggestions.skills_to_add.slice(0, 5).forEach(item => {
            html += `<div class="suggestion-card">
                <div class="suggestion-header">
                    <strong>${item.skill}</strong>
                    <span class="priority-badge priority-${item.priority}">${item.priority.toUpperCase()}</span>
                </div>
                <p class="suggestion-action">${item.action || ''}</p>
                <div class="suggestion-meta">
                    <span>⏱️ ${item.timeline || '2-3 weeks'}</span>
                    <span>📚 ${item.resources || 'Online resources'}</span>
                </div>
            </div>`;
        });
        html += '</div></div>';
    }
    
    // Projects to Build
    if (suggestions.projects_to_build && suggestions.projects_to_build.length > 0) {
        html += '<div class="suggestion-category"><h4>🚀 Projects to Build</h4><div class="projects-grid">';
        suggestions.projects_to_build.slice(0, 3).forEach(project => {
            html += `<div class="project-card">
                <h5>${project.name}</h5>
                <p>${project.description}</p>
                <div class="project-meta">
                    <span>⏱️ ${project.timeline || '2-3 weeks'}</span>
                    <span>📊 ${project.complexity || 'Medium'}</span>
                </div>
                <div class="project-skills">${(project.skills || []).map(s => `<span class="skill-tag">${s}</span>`).join('')}</div>
            </div>`;
        });
        html += '</div></div>';
    }
    
    // Actionable Steps
    if (suggestions.actionable_steps && suggestions.actionable_steps.length > 0) {
        html += '<div class="suggestion-category"><h4>📝 Immediate Action Plan</h4><ol class="action-steps">';
        suggestions.actionable_steps.forEach(step => {
            html += `<li>
                <strong>Step ${step.step}: ${step.action}</strong>
                <p>${step.why || ''}</p>
                <div class="step-meta">⏱️ ${step.timeline || '2-3 weeks'} | 📚 ${step.resources || 'Resources'}</div>
            </li>`;
        });
        html += '</ol></div>';
    }
    
    sectionEl.innerHTML = html;
}

// Display Advanced Learning Roadmap
function displayLearningRoadmapAdvanced(roadmap) {
    const section = document.getElementById('learningRoadmapSection');
    if (!section) return;
    
    section.style.display = 'block';
    let html = '<h3>🗺️ Personalized Learning Roadmap</h3>';
    html += `<p class="section-subtitle">Your path to ${roadmap.target_role || 'success'}</p>`;
    
    // 30-Day Plan
    if (roadmap['30_day']) {
        const plan30 = roadmap['30_day'];
        html += '<div class="roadmap-plan"><h4>📅 30-Day Quick Start Plan</h4>';
        html += `<div class="plan-summary">Focus: ${plan30.focus_areas?.join(', ') || 'Core Skills'}</div>`;
        html += '<div class="weeks-container">';
        (plan30.weeks || []).forEach(week => {
            html += `<div class="week-card">
                <div class="week-header">Week ${week.week}: ${week.focus}</div>
                <div class="week-skills">Skills: ${(week.skills || []).join(', ')}</div>
                <ul class="week-tasks">${(week.tasks || []).map(t => `<li>${t}</li>`).join('')}</ul>
                ${week.projects && week.projects.length > 0 ? `<div class="week-projects">Projects: ${week.projects.join(', ')}</div>` : ''}
                <div class="week-milestone">🎯 ${week.milestone || ''}</div>
            </div>`;
        });
        html += '</div></div>';
    }
    
    // 60-Day Plan
    if (roadmap['60_day']) {
        const plan60 = roadmap['60_day'];
        html += '<div class="roadmap-plan"><h4>📅 60-Day Comprehensive Plan</h4>';
        html += `<div class="plan-summary">Total Projects: ${plan60.total_projects || 0} | Focus: ${plan60.focus_areas?.join(', ') || ''}</div>`;
        html += '<div class="phases-container">';
        (plan60.phases || []).forEach(phase => {
            html += `<div class="phase-card">
                <div class="phase-header">${phase.weeks || phase.phase}: ${phase.focus}</div>
                <div class="phase-skills">Skills: ${Array.isArray(phase.skills) ? phase.skills.join(', ') : phase.skills}</div>
                <ul class="phase-tasks">${(phase.tasks || []).map(t => `<li>${t}</li>`).join('')}</ul>
                <div class="phase-milestone">🎯 ${phase.milestone || ''}</div>
            </div>`;
        });
        html += '</div></div>';
    }
    
    // 90-Day Plan
    if (roadmap['90_day']) {
        const plan90 = roadmap['90_day'];
        html += '<div class="roadmap-plan"><h4>📅 90-Day Transformation Plan</h4>';
        html += `<div class="plan-summary">Total Projects: ${plan90.total_projects || 0} | Success: ${plan90.success_criteria || ''}</div>`;
        html += '<div class="phases-container">';
        (plan90.phases || []).forEach(phase => {
            html += `<div class="phase-card">
                <div class="phase-header">${phase.phase}: ${phase.duration}</div>
                <div class="phase-focus">Focus: ${phase.focus}</div>
                <div class="phase-skills">Skills: ${Array.isArray(phase.skills) ? phase.skills.join(', ') : phase.skills}</div>
                <ul class="phase-tasks">${(phase.tasks || []).map(t => `<li>${t}</li>`).join('')}</ul>
                <div class="phase-projects">Projects: ${phase.projects || 0}</div>
                <div class="phase-milestone">🎯 ${phase.milestone || ''}</div>
            </div>`;
        });
        html += '</div></div>';
    }
    
    section.innerHTML = html;
}

// Display Resume Improvement
function displayResumeImprovement(improvement) {
    const section = document.getElementById('resumeImprovementSection');
    if (!section || !improvement || improvement.parsed === false) return;
    
    section.style.display = 'block';
    let html = '<h4>✏️ AI Resume Improvement Advice</h4><div class="improvement-content">';
    
    if (improvement.summary_suggestions) {
        html += `<div class="improvement-card"><h5>📝 Summary Suggestions</h5><p>${improvement.summary_suggestions}</p></div>`;
    }
    
    if (improvement.experience_improvements) {
        html += `<div class="improvement-card"><h5>💼 Experience Improvements</h5><p>${improvement.experience_improvements}</p></div>`;
    }
    
    if (improvement.keyword_optimization) {
        html += `<div class="improvement-card"><h5>🔑 Keyword Optimization</h5><p>${improvement.keyword_optimization}</p></div>`;
    }
    
    if (improvement.response && !improvement.summary_suggestions) {
        html += `<p>${improvement.response}</p>`;
    }
    
    html += '</div>';
    section.innerHTML = html;
}

// Reset analysis form
function resetAnalysis() {
    const resultsSection = document.getElementById('resultsSection');
    if (resultsSection) {
        resultsSection.style.display = 'none';
    }
    
    // Hide all AI sections
    ['advancedAnalysisSection', 'smartSuggestionsSection', 'aiAnalysisSection', 'roleAnalysisSection', 'learningRoadmapSection', 'resumeImprovementSection'].forEach(id => {
        const section = document.getElementById(id);
        if (section) section.style.display = 'none';
    });
    
    const analysisForm = document.getElementById('analysisForm');
    if (analysisForm) {
        analysisForm.reset();
    }
    
    const fileName = document.getElementById('fileName');
    if (fileName) {
        fileName.textContent = '';
    }
    
    // Scroll to top of form
    const uploadSection = document.querySelector('.upload-section');
    if (uploadSection) {
        uploadSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Initialize smooth scroll for About section
function initializeSmoothScroll() {
    // Handle About link clicks
    const aboutLinks = document.querySelectorAll('a[href="#about"], a.nav-link-about, a[href*="#about"]');
    
    aboutLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // If on a different page, let the browser navigate first
            if (this.getAttribute('href').includes('index.html')) {
                return; // Let browser handle navigation
            }
            
            // If on same page, smooth scroll
            e.preventDefault();
            const aboutSection = document.getElementById('about');
            if (aboutSection) {
                aboutSection.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Handle hash in URL on page load
    if (window.location.hash === '#about') {
        setTimeout(() => {
            const aboutSection = document.getElementById('about');
            if (aboutSection) {
                aboutSection.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }, 100);
    }
}

// Check if backend server is running
// IMPORTANT: Users must run the backend server before using the app
// Command: cd backend && python main.py
async function checkBackendConnection() {
    try {
        // Create a timeout promise
        const timeoutPromise = new Promise((_, reject) => 
            setTimeout(() => reject(new Error('Timeout')), 3000)
        );
        
        const fetchPromise = fetch(`${API_BASE_URL}/health`, {
            method: 'GET'
        });
        
        const response = await Promise.race([fetchPromise, timeoutPromise]);
        
        if (response && response.ok) {
            // Backend is running, hide notice if shown
            const backendNotice = document.getElementById('backendNotice');
            if (backendNotice) {
                backendNotice.style.display = 'none';
            }
        }
    } catch (error) {
        // Backend is not running, show notice
        const backendNotice = document.getElementById('backendNotice');
        if (backendNotice) {
            backendNotice.style.display = 'block';
        }
        console.log('⚠️ Backend server is not running. Please start it with: cd backend && python main.py');
    }
}

// Handle logout
async function handleLogout(event) {
    event.preventDefault();
    
    if (confirm('Are you sure you want to logout?')) {
        const token = getSessionToken();
        
        if (token) {
            try {
                await fetch(`${API_BASE_URL}/api/logout`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
            } catch (error) {
                console.error('Logout error:', error);
            }
        }
        
        clearSession();
        // Hide user name before redirect
        const userInfoEl = document.getElementById('userInfo');
        if (userInfoEl) {
            userInfoEl.style.display = 'none';
        }
        window.location.href = 'index.html';
    }
}
