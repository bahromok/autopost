"""Service for fetching dynamic educational content from RSS feeds and APIs."""

import asyncio
import random
import feedparser
import aiohttp
from typing import Dict, List, Optional, Any
from loguru import logger
from bs4 import BeautifulSoup

from src.services.groq_service import GroqService

class DynamicContentFetcher:
    """Fetches educational content from various dynamic sources."""
    
    def __init__(self):
        self.groq_service = GroqService()
    
    # Educational RSS Feeds
    FEEDS = {
        'tutorial': [
            'https://dev.to/feed',
            'https://www.freecodecamp.org/news/rss/',
            'https://css-tricks.com/feed/',
            'https://realpython.com/atom.xml',
        ],
        'ai_ml': [
            'https://towardsdatascience.com/feed',
            'https://machinelearningmastery.com/feed/',
        ],
        'cs': [
            'https://www.geeksforgeeks.org/feed/',
            'https://betterprogramming.pub/feed',
        ]
    }
    
    async def fetch_rss_content(self, category: str) -> Optional[Dict[str, str]]:
        """Fetch content from RSS feeds for a specific category."""
        if category not in self.FEEDS:
            return None
            
        feed_url = random.choice(self.FEEDS[category])
        try:
            # We use aiohttp to fetch raw XML then parse with feedparser
            async with aiohttp.ClientSession() as session:
                async with session.get(feed_url, timeout=10) as response:
                    if response.status != 200:
                        logger.warning(f"Failed to fetch feed {feed_url}: {response.status}")
                        return None
                    xml_content = await response.text()
            
            feed = feedparser.parse(xml_content)
            
            if not feed.entries:
                logger.warning(f"No entries found in feed {feed_url}")
                return None
                
            # Pick a random entry from recent ones
            entries = feed.entries[:10]
            entry = random.choice(entries)
            
            title = entry.get('title', 'No Title')
            link = entry.get('link', '')
            summary = entry.get('summary', '') or entry.get('description', '')
            
            # Use Groq to summarize/translate this educational content
            groq_content = await self.groq_service.generate_summary(
                text=summary, 
                title=title, 
                link=link
            )
            
            if groq_content:
                return groq_content
                
            return None
            
        except Exception as e:
            logger.error(f"Error fetching RSS content from {feed_url}: {e}")
            return None

    async def generate_ai_fact(self) -> Optional[Dict[str, str]]:
        """Generate a random tech fact/tutorial using Groq."""
        try:
            topics = [
                "Python programming trick", "JavaScript modern feature", 
                "Linux command line tip", "Cybersecurity best practice",
                "AI/ML concept explained", "History of computing fact",
                "Web performance optimization tip", "Database scaling strategy"
            ]
            topic = random.choice(topics)
            
            # We treat this as "summarizing" a concept
            fake_title = f"Random Tech Knowledge: {topic}"
            fake_summary = f"Please generate a fascinating and useful fact or mini-tutorial about {topic}."
            
            return await self.groq_service.generate_summary(
                text=fake_summary,
                title=topic, 
                link="" # No link for random facts
            )
        except Exception as e:
            logger.error(f"Error generating AI fact: {e}")
            return None

    async def generate_coding_lesson(self) -> Optional[Dict[str, str]]:
        """Generate a full coding lesson using Groq."""
        try:
            topics = [
                "Python List Comprehensions", "Python Decorators", "Python Async/Await",
                "JavaScript Promises", "JavaScript Destructuring", "JavaScript Arrow Functions",
                "React Hooks", "CSS Flexbox", "CSS Grid",
                "SQL Joins", "Git Branching", "Docker Containers"
            ]
            topic = random.choice(topics)
            
            return await self.groq_service.generate_coding_lesson(topic)
        except Exception as e:
            logger.error(f"Error generating coding lesson: {e}")
            return None

    async def get_random_content(self) -> Optional[Dict[str, str]]:
        """Get random content from any source."""
        # 40% RSS, 30% AI Fact, 30% AI Lesson
        rand_val = random.random()
        
        if rand_val < 0.4:
            # RSS
            category = random.choice(list(self.FEEDS.keys()))
            return await self.fetch_rss_content(category)
        elif rand_val < 0.7:
            # AI Fact
            return await self.generate_ai_fact()
        else:
            # AI Lesson
            return await self.generate_coding_lesson()

