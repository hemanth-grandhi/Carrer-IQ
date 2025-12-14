"""
Authentication Module
Handles user registration, login, and session management
"""

import json
import os
import hashlib
import secrets
from typing import Optional, Dict
from datetime import datetime, timedelta


class AuthManager:
    """Manage user authentication and sessions"""
    
    def __init__(self, db_path: str = "users.json"):
        self.db_path = os.path.join(os.path.dirname(__file__), db_path)
        self.sessions = {}  # In-memory session storage
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Create users database file if it doesn't exist"""
        if not os.path.exists(self.db_path):
            with open(self.db_path, 'w') as f:
                json.dump({}, f)
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _load_users(self) -> Dict:
        """Load users from database"""
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_users(self, users: Dict):
        """Save users to database"""
        with open(self.db_path, 'w') as f:
            json.dump(users, f, indent=2)
    
    def register(self, email: str, password: str, name: str) -> Dict:
        """
        Register a new user
        
        Args:
            email: User email
            password: User password
            name: User full name
        
        Returns:
            Dict with success status and message
        """
        users = self._load_users()
        
        # Check if user already exists
        if email.lower() in users:
            return {
                "success": False,
                "message": "Email already registered"
            }
        
        # Validate password
        if len(password) < 8:
            return {
                "success": False,
                "message": "Password must be at least 8 characters"
            }
        
        # Create user
        users[email.lower()] = {
            "email": email.lower(),
            "password_hash": self._hash_password(password),
            "name": name,
            "created_at": datetime.now().isoformat()
        }
        
        self._save_users(users)
        
        return {
            "success": True,
            "message": "User registered successfully",
            "user": {
                "email": email.lower(),
                "name": name
            }
        }
    
    def login(self, email: str, password: str) -> Dict:
        """
        Login user and create session
        
        Args:
            email: User email
            password: User password
        
        Returns:
            Dict with success status, session token, and user info
        """
        # Validate inputs
        if not email or not password:
            return {
                "success": False,
                "message": "Email and password are required"
            }
        
        # Strip whitespace and validate
        email = email.strip()
        password = password.strip()
        
        if not email or not password:
            return {
                "success": False,
                "message": "Email and password cannot be empty"
            }
        
        try:
            users = self._load_users()
            email_lower = email.lower()
            
            # Check if user exists
            if email_lower not in users:
                return {
                    "success": False,
                    "message": "Invalid email or password"
                }
            
            user = users[email_lower]
            
            # Verify password
            password_hash = self._hash_password(password)
            if user["password_hash"] != password_hash:
                return {
                    "success": False,
                    "message": "Invalid email or password"
                }
            
            # Create session
            session_token = secrets.token_urlsafe(32)
            self.sessions[session_token] = {
                "email": email_lower,
                "name": user["name"],
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(days=7)).isoformat()
            }
            
            return {
                "success": True,
                "message": "Login successful",
                "session_token": session_token,
                "user": {
                    "email": email_lower,
                    "name": user["name"]
                }
            }
        except Exception as e:
            # Log error for debugging
            print(f"Login error: {str(e)}")
            return {
                "success": False,
                "message": "An error occurred during login. Please try again."
            }
    
    def verify_session(self, session_token: str) -> Optional[Dict]:
        """
        Verify session token and return user info
        
        Args:
            session_token: Session token
        
        Returns:
            User info if session is valid, None otherwise
        """
        if not session_token:
            return None
        
        if session_token not in self.sessions:
            return None
        
        try:
            session = self.sessions[session_token]
            
            # Check if session expired
            if "expires_at" in session:
                expires_at = datetime.fromisoformat(session["expires_at"])
                if datetime.now() > expires_at:
                    del self.sessions[session_token]
                    return None
            
            return session
        except Exception as e:
            # If there's an error verifying session, remove it and return None
            print(f"Error verifying session: {str(e)}")
            if session_token in self.sessions:
                del self.sessions[session_token]
            return None
    
    def logout(self, session_token: str):
        """Logout user by removing session"""
        if session_token in self.sessions:
            del self.sessions[session_token]


