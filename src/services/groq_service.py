"""Service for interacting with Groq API."""

import aiohttp
import json
import random
from typing import Optional, Dict, Any
from loguru import logger
from src.config.settings import settings

class GroqService:
    """Service for generating content using Groq API."""
    
    API_URL = "https://api.groq.com/openai/v1/chat/completions"
    MODEL = "llama-3.3-70b-versatile"  # Updated to supported model

    @staticmethod
    async def generate_summary(text: str, title: str, link: str) -> Optional[Dict[str, str]]:
        """
        Generate a professional Uzbek summary using Groq with dynamic templates.
        
        Returns:
            Dict containing 'title', 'summary', 'hashtags' in Uzbek.
        """
        if not settings.groq_api_key:
            logger.error("Groq API key not configured")
            return None
            
        # --- TEMPLATE DEFINITIONS ---
        
        # Style 1: The Analyst (Your original "Dense" style)
        t_analyst = """
        ROLE: Data-Driven Tech Analyst.
        STYLE: Serious, dense, focused on numbers and hard facts.
        FORMAT (Native Uzbek Keys):
        - ⚡ **Asosiy mag'zi**: The main point in one sentence.
        - 🔑 **Muhim faktlar**: Bulleted list of specific features/numbers.
        - 💡 **Texnik xulosa**: Deep technical insight.
        """
        
        # Style 2: The Explainer (Q&A style for complex topics)
        t_explainer = """
        ROLE: Tech Educator.
        STYLE: Explaining complex news simply using a Q&A format.
        FORMAT (Native Uzbek Keys):
        - ❓ **Bu nima?**: Explain the core news simply.
        - 🛠 **Qanday ishlaydi?**: How it works tech-wise.
        - 🚀 **Nega muhim?**: Why developers should care.
        """
        
        # Style 3: The Insider (Breaking news style)
        t_insider = """
        ROLE: Tech Insider / Reporter.
        STYLE: Urgent, exciting, "Breaking News" feel.
        FORMAT (Native Uzbek Keys):
        - 🚨 **Tezkor Xabar**: The breaking news headline expanded.
        - 📝 **Tafsilotlar**: What actually happened (the event, release, or acquisition).
        - 🔮 **Kelajak prognozi**: What this means for the next 6 months.
        """
        
        # Algorithm: Randomly select a template
        # We can weigh them if desired, but uniform random is good for variety.
        templates = [t_analyst, t_explainer, t_insider]
        selected_template = random.choice(templates)
        
        prompt = f"""
        {selected_template}
        
        TASK:
        Analyze the following article and generate a structured Telegram post in UZBEK.
        
        ARTICLE TITLE: {title}
        ARTICLE CONTENT: {text}
        LINK: {link}
        
        STRICT GUIDELINES:
        1. ❌ NO GENERAL SENTENCES like "This is very important." or "In today's world...".
        2. ❌ ABSOLUTELY NO ENGLISH WORDS in headers (Native Uzbek keys only).
        3. ✅ TONE: Native Uzbek Professional. Natural phrasing.
        
        OUTPUT FORMAT (JSON):
        {{
            "title": "Natural Uzbek Title in Bold",
            "summary": {{ 
                "Key1": "Value1",
                "Key2": ["List Item 1", "List Item 2"],
                "Key3": "Value3"
            }},
            "hashtags": "#Hashtags"
        }}
        """
        
        headers = {
            "Authorization": f"Bearer {settings.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": GroqService.MODEL,
            "messages": [
                {"role": "system", "content": "You are a senior tech editor. You delete fluff and output only dense, useful knowledge."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5, # Lower temperature for more factual/focused output
            "response_format": {"type": "json_object"}
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(GroqService.API_URL, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Groq API Error: {response.status} - {error_text}")
                        return None
                        
                    data = await response.json()
                    content_str = data['choices'][0]['message']['content']
                    
                    try:
                        result = json.loads(content_str)
                        return {
                            "title": result.get("title", title),
                            "summary": result.get("summary", ""),
                            "hashtags": result.get("hashtags", "")
                        }
                    except json.JSONDecodeError:
                        logger.error("Failed to parse Groq JSON response")
                        # Fallback parsing or return raw text if needed, but for now return None to be safe
                        return None
                        
        except Exception as e:
            logger.error(f"Error calling Groq API: {e}")
            return None

    @staticmethod
    async def generate_coding_lesson(topic: str) -> Optional[Dict[str, str]]:
        """
        Generate a structured coding lesson.
        
        Returns:
            Dict containing 'title', 'summary', 'hashtags' suitable for immediate posting.
        """
        if not settings.groq_api_key:
            logger.error("Groq API key not configured")
            return None
            
        prompt = f"""
        You are a Senior Software Engineer teaching a junior.
        Topic: "{topic}" (UZBEK LANGUAGE).
        
        GOAL:
        Don't just explain WHAT it is. Explain the "TRICK", the "PITFALL", or the "BEST PRACTICE". Give them real engineering knowledge, not textbook definitions.
        
        STRUCTURE:
        1. 💎 **Pro Concept**: The deep technical insight (e.g., memory usage, performance check, clean code rule). MAX 2 sentences.
        2. 💻 **Real Code**: A snippet showing a "Pro" usage (not hello world). Comment the tricky parts.
        3. ⚔️ **Challenge**: A specific task to test their understanding.
        
        GUIDELINES:
        - LANGUAGE: STRICTLY UZBEK ONLY.
        - NO FLUFF: No "Hello friends", no "Today we will learn". Start immediately with knowledge.
        
        OUTPUT FORMAT (JSON):
        {{
            "title": "🎓 Master Class: [Topic]",
            "summary": "The structured lesson",
            "hashtags": "#Coding #Advanced #UzbekDev #Tutorial"
        }}
        """
        
        headers = {
            "Authorization": f"Bearer {settings.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": GroqService.MODEL,
            "messages": [
                {"role": "system", "content": "You are a Senior Engineer. You value density and correctness over politeness."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.6,
            "response_format": {"type": "json_object"}
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(GroqService.API_URL, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Groq API Error: {response.status} - {error_text}")
                        return None
                        
                    data = await response.json()
                    content_str = data['choices'][0]['message']['content']
                    
                    try:
                        result = json.loads(content_str)
                        return {
                            "title": result.get("title", f"🎓 Lesson: {topic}"),
                            "summary": result.get("summary", ""),
                            "hashtags": result.get("hashtags", "#Coding")
                        }
                    except json.JSONDecodeError:
                        logger.error("Failed to parse Groq JSON response")
                        return None
                        
        except Exception as e:
            logger.error(f"Error generating coding lesson: {e}")
            return None
