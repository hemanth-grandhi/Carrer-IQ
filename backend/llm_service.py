"""
LLM Service Module
Supports multiple LLM providers: Gemini, OpenAI, and Hugging Face
"""

import os
import json
from typing import Optional, Dict, Any
from enum import Enum


class LLMProvider(Enum):
    """Supported LLM providers"""
    GEMINI = "gemini"
    OPENAI = "openai"
    HUGGINGFACE = "huggingface"
    NONE = "none"  # Fallback when no API key is provided


class LLMService:
    """Service for interacting with various LLM APIs"""
    
    def __init__(self):
        self.provider = self._detect_provider()
        self.api_key = self._get_api_key()
        self.model_name = os.getenv("LLM_MODEL_NAME", "")
        
    def _detect_provider(self) -> LLMProvider:
        """Detect which LLM provider to use based on available API keys"""
        gemini_key = os.getenv("GEMINI_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        hf_key = os.getenv("HUGGINGFACE_API_KEY")
        
        # Priority: Gemini > OpenAI > Hugging Face
        if gemini_key:
            return LLMProvider.GEMINI
        elif openai_key:
            return LLMProvider.OPENAI
        elif hf_key:
            return LLMProvider.HUGGINGFACE
        else:
            return LLMProvider.NONE
    
    def _get_api_key(self) -> Optional[str]:
        """Get the API key for the detected provider"""
        if self.provider == LLMProvider.GEMINI:
            return os.getenv("GEMINI_API_KEY")
        elif self.provider == LLMProvider.OPENAI:
            return os.getenv("OPENAI_API_KEY")
        elif self.provider == LLMProvider.HUGGINGFACE:
            return os.getenv("HUGGINGFACE_API_KEY")
        return None
    
    async def generate_text(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Generate text using the configured LLM provider
        
        Args:
            prompt: The prompt to send to the LLM
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        if self.provider == LLMProvider.NONE:
            return self._get_fallback_response(prompt)
        
        try:
            if self.provider == LLMProvider.GEMINI:
                return await self._call_gemini(prompt, max_tokens)
            elif self.provider == LLMProvider.OPENAI:
                return await self._call_openai(prompt, max_tokens)
            elif self.provider == LLMProvider.HUGGINGFACE:
                return await self._call_huggingface(prompt, max_tokens)
        except Exception as e:
            print(f"Error calling LLM API: {str(e)}")
            return self._get_fallback_response(prompt)
    
    async def _call_gemini(self, prompt: str, max_tokens: int) -> str:
        """Call Google Gemini API"""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            response = model.generate_content(
                prompt,
                generation_config={
                    'max_output_tokens': max_tokens,
                    'temperature': 0.7,
                }
            )
            
            return response.text
        except ImportError:
            raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    async def _call_openai(self, prompt: str, max_tokens: int) -> str:
        """Call OpenAI API"""
        try:
            import openai
            
            client = openai.OpenAI(api_key=self.api_key)
            
            model = self.model_name or "gpt-3.5-turbo"
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful career advisor and skill development expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    async def _call_huggingface(self, prompt: str, max_tokens: int) -> str:
        """Call Hugging Face Inference API"""
        try:
            import requests
            
            model = self.model_name or "mistralai/Mistral-7B-Instruct-v0.2"
            api_url = f"https://api-inference.huggingface.co/models/{model}"
            
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": 0.7,
                    "return_full_text": False
                }
            }
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # Handle different response formats
            if isinstance(result, list) and len(result) > 0:
                if "generated_text" in result[0]:
                    return result[0]["generated_text"]
                elif "summary_text" in result[0]:
                    return result[0]["summary_text"]
            
            return str(result)
        except ImportError:
            raise ImportError("requests package not installed. Run: pip install requests")
        except Exception as e:
            raise Exception(f"Hugging Face API error: {str(e)}")
    
    def _get_fallback_response(self, prompt: str) -> str:
        """Fallback response when no LLM is configured"""
        return (
            "LLM API not configured. Please set one of the following environment variables:\n"
            "- GEMINI_API_KEY (for Google Gemini)\n"
            "- OPENAI_API_KEY (for OpenAI)\n"
            "- HUGGINGFACE_API_KEY (for Hugging Face)\n\n"
            "The system will use rule-based responses until an API key is configured."
        )
    
    def is_available(self) -> bool:
        """Check if LLM service is available"""
        return self.provider != LLMProvider.NONE


