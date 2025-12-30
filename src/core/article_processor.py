"""Article processor - orchestrates the article processing pipeline."""

from typing import Dict, Any, Optional
from loguru import logger

from src.services.rss_service import RSSService
from src.services.groq_service import GroqService
from src.services.image_service import ImageService
from src.core.content_formatter import ContentFormatter


class ArticleProcessor:
    """Processes articles through the complete pipeline."""
    
    def __init__(self):
        """Initialize the article processor."""
        self.rss_service = RSSService()
        self.groq_service = GroqService()
        self.image_service = ImageService()
        self.formatter = ContentFormatter()
    
    async def process_article(self, entry_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a single article through the complete pipeline.
        
        Args:
            entry_data: Article data from RSS feed
        
        Returns:
            Processed article data with message and image, or None if processing fails
        """
        try:
            title = entry_data["title"]
            summary = entry_data["summary"] or entry_data.get("description", "")
            link = entry_data["link"]
            raw_entry = entry_data.get("raw_entry")
            
            logger.info(f"Processing article: {title}")
            
            # Step 1: Generate AI Summary via Groq
            logger.info("Generating AI summary via Groq...")
            groq_content = await self.groq_service.generate_summary(
                text=summary,
                title=title,
                link=link
            )
            
            if not groq_content:
                logger.warning("Groq generation failed, skipping article")
                return None
            
            # Step 2: Format message
            logger.info("Formatting message...")
            # We pass the Groq result directly to formatter
            message = self.formatter.format_message_groq(groq_content, link)
            
            # Step 3: Extract image
            logger.info("Extracting image...")
            image_url = None
            if raw_entry:
                image_url = self.image_service.extract_image(raw_entry, link)
            
            # Step 4: Validate message length
            has_image = image_url is not None
            if not self.formatter.validate_message_length(message, has_image):
                logger.warning("Message too long, will attempt to send anyway")
            
            # Return processed data
            processed_data = {
                "title": groq_content["title"],
                "summary": groq_content["summary"],
                "link": link,
                "published_at": entry_data.get("published_at"),
                "message": message,
                "image_url": image_url,
                "raw_title": title # Store original for reference
            }
            
            logger.success(f"Article processed successfully: {title}")
            return processed_data
            
        except Exception as e:
            logger.error(f"Failed to process article: {e}")
            return None
    
    async def process_feed(self, feed_url: str) -> list:
        """
        Process all relevant articles from a feed.
        
        Args:
            feed_url: RSS feed URL
        
        Returns:
            List of processed articles
        """
        logger.info(f"Processing feed: {feed_url}")
        
        # Fetch relevant entries
        entries = await self.rss_service.fetch_relevant_entries(feed_url)
        
        if not entries:
            logger.info(f"No relevant entries found in feed: {feed_url}")
            return []
        
        # Process each entry
        processed_articles = []
        for entry_data in entries:
            processed = await self.process_article(entry_data)
            if processed:
                processed_articles.append(processed)
        
        logger.info(
            f"Processed {len(processed_articles)} articles from {feed_url}"
        )
        return processed_articles
