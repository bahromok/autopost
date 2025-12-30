"""RSS feed service for fetching and parsing feeds."""

import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import feedparser
from loguru import logger

from src.config.settings import settings


class RSSService:
    """Service for RSS feed operations."""
    
    @staticmethod
    def parse_feed(feed_url: str) -> Optional[feedparser.FeedParserDict]:
        """Parse an RSS feed."""
        try:
            logger.info(f"Parsing feed: {feed_url}")
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                logger.warning(
                    f"Feed potentially malformed: {feed_url} - {feed.bozo_exception}"
                )
            
            if not feed.entries:
                logger.warning(f"No entries found in feed: {feed_url}")
                return None
            
            logger.success(f"Parsed {len(feed.entries)} entries from {feed_url}")
            return feed
            
        except Exception as e:
            logger.error(f"Failed to parse feed {feed_url}: {e}")
            return None
    
    @staticmethod
    def extract_entry_data(entry: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant data from a feed entry."""
        # Get title
        title = entry.get("title", "No Title")
        
        # Get link
        link = entry.get("link", "#")
        
        # Get summary and clean HTML
        summary = entry.get("summary", entry.get("description", ""))
        if summary and "<" in summary:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(summary, "html.parser")
            summary = soup.get_text(separator=" ", strip=True)
        
        # Limit summary length
        if len(summary) > 300:
            summary = summary[:300].rsplit(" ", 1)[0] + "..."
        
        # Get published date
        published_at = None
        if entry.get("published_parsed"):
            try:
                published_at = datetime.fromtimestamp(
                    time.mktime(entry.get("published_parsed"))
                )
            except Exception as e:
                logger.warning(f"Failed to parse published date: {e}")
        
        return {
            "title": title,
            "link": link,
            "summary": summary,
            "published_at": published_at,
        }
    
    @staticmethod
    def is_article_recent(published_at: Optional[datetime]) -> bool:
        """Check if article is within the age limit."""
        if not published_at:
            return True  # If no date, assume it's recent
        
        cutoff_time = datetime.now() - timedelta(hours=settings.max_article_age_hours)
        return published_at >= cutoff_time
    
    @staticmethod
    def contains_keywords(text: str, keywords: List[str]) -> bool:
        """Check if text contains any of the keywords."""
        if not text:
            return False
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in keywords)
    
    @staticmethod
    def filter_entry(entry_data: Dict[str, Any]) -> bool:
        """Filter entry based on keywords and age."""
        # Check age
        if not RSSService.is_article_recent(entry_data.get("published_at")):
            logger.debug(f"Article too old: {entry_data['title']}")
            return False
        
        # Check keywords
        keywords = settings.keyword_list
        title = entry_data.get("title", "")
        summary = entry_data.get("summary", "")
        
        if not (
            RSSService.contains_keywords(title, keywords)
            or RSSService.contains_keywords(summary, keywords)
        ):
            logger.debug(f"Article doesn't match keywords: {entry_data['title']}")
            return False
        
        return True
    
    @staticmethod
    async def fetch_relevant_entries(feed_url: str) -> List[Dict[str, Any]]:
        """Fetch and filter relevant entries from a feed."""
        feed = RSSService.parse_feed(feed_url)
        if not feed:
            return []
        
        relevant_entries = []
        
        for entry in feed.entries:
            entry_data = RSSService.extract_entry_data(entry)
            entry_data["raw_entry"] = entry  # Keep raw entry for image extraction
            
            if RSSService.filter_entry(entry_data):
                relevant_entries.append(entry_data)
                logger.info(f"Found relevant article: {entry_data['title']}")
        
        logger.info(f"Found {len(relevant_entries)} relevant entries from {feed_url}")
        return relevant_entries
