"""Scheduler for managing the posting workflow."""

import asyncio
import random
from datetime import datetime
from typing import List
from loguru import logger

from src.config.settings import settings
from src.database import (
    db,
    FeedRepository,
    ArticleRepository,
    PostingLogRepository,
    StatisticsRepository,
)
from src.services.telegram_service import TelegramService
from src.core.article_processor import ArticleProcessor
from src.core.article_scorer import ArticleScorer
from src.core.content_library import ContentLibrary
import random


class Scheduler:
    """Manages the article fetching and posting workflow."""
    
    def __init__(self):
        """Initialize the scheduler."""
        self.telegram_service = TelegramService()
        self.article_processor = ArticleProcessor()
        self.content_library = ContentLibrary()
        self.running = False
        self.posts_today = 0
        self.last_reset_date = datetime.now().date()
    
    async def initialize(self):
        """Initialize services."""
        logger.info("Initializing scheduler...")
        
        # Connect to Telegram
        await self.telegram_service.connect()
        
        # Initialize feeds in database
        await self._initialize_feeds()
        
        logger.success("Scheduler initialized")
    
    async def _initialize_feeds(self):
        """Initialize feeds in the database."""
        async with db.get_session() as session:
            for feed_url in settings.rss_feed_list:
                existing = await FeedRepository.get_by_url(session, feed_url)
                if not existing:
                    await FeedRepository.create(session, feed_url)
                    logger.info(f"Added feed to database: {feed_url}")
    
    async def process_and_post_article(self, processed_article: dict) -> bool:
        """
        Process and post a single article.
        
        Args:
            processed_article: Processed article data
        
        Returns:
            True if posted successfully, False otherwise
        """
        link = processed_article["link"]
        
        # Check if already posted
        async with db.get_session() as session:
            if await ArticleRepository.exists(session, link):
                logger.info(f"Article already posted: {link}")
                await StatisticsRepository.increment_skipped(session)
                return False
        
        # Send to Telegram
        message = processed_article["message"]
        image_url = processed_article.get("image_url")
        
        sent_message = await self.telegram_service.send_message(message, image_url)
        
        # Save to database
        async with db.get_session() as session:
            # Get or create feed
            feed = await FeedRepository.get_by_url(session, "unknown")
            if not feed:
                feed = await FeedRepository.create(session, "unknown")
            
            if sent_message:
                # Prepare summary for DB (serialize if dict)
                summary_val = processed_article["summary"]
                if isinstance(summary_val, dict):
                    import json
                    summary_val = json.dumps(summary_val, ensure_ascii=False)
                    
                # Create article record
                article = await ArticleRepository.create(
                    session,
                    feed_id=feed.id,
                    url=link,
                    title=processed_article["title"],
                    summary=summary_val,
                    published_at=processed_article.get("published_at"),
                    image_url=image_url,
                    telegram_message_id=sent_message.id,
                )
                
                # Log success
                await PostingLogRepository.create(
                    session,
                    article_id=article.id,
                    status="success",
                )
                
                # Update statistics
                await StatisticsRepository.increment_posted(session)
                
                logger.success(f"Article posted and saved: {link}")
                return True
            else:
                # Log failure
                await StatisticsRepository.increment_failed(session)
                logger.error(f"Failed to post article: {link}")
                return False
    
    
    async def post_educational_content(self) -> bool:
        """Post educational content (fact, tutorial, or tip)."""
        try:
            content = await self.content_library.get_random_educational_content()
            message = self.content_library.format_educational_post(content)
            
            sent_message = await self.telegram_service.send_message(message, image_url=None)
            
            if sent_message:
                logger.success(f"Educational content posted: {content['title']}")
                return True
            else:
                logger.error("Failed to post educational content")
                return False
        except Exception as e:
            logger.error(f"Error posting educational content: {e}")
            return False
    
    async def run_cycle(self):
        """Run a single posting cycle with content curation."""
        logger.info("Starting posting cycle...")
        
        # Reset daily counter if new day
        today = datetime.now().date()
        if today != self.last_reset_date:
            self.posts_today = 0
            self.last_reset_date = today
            logger.info("Daily post counter reset")
        
        # Check daily limit
        if self.posts_today >= settings.max_posts_per_day:
            logger.warning(
                f"Daily posting limit reached ({settings.max_posts_per_day}). "
                "Skipping this cycle."
            )
            return
        
        posted_count = 0
        all_processed_articles = []
        
        # Collect articles from all feeds
        for feed_url in settings.rss_feed_list:
            try:
                # Update feed last checked
                async with db.get_session() as session:
                    feed = await FeedRepository.get_by_url(session, feed_url)
                    if feed:
                        await FeedRepository.update_last_checked(session, feed.id, success=True)
                
                # Process feed
                processed_articles = await self.article_processor.process_feed(feed_url)
                all_processed_articles.extend(processed_articles)
                
            except Exception as e:
                logger.error(f"Error processing feed {feed_url}: {e}")
                
                # Update feed error count
                async with db.get_session() as session:
                    feed = await FeedRepository.get_by_url(session, feed_url)
                    if feed:
                        await FeedRepository.update_last_checked(session, feed.id, success=False)
        
        if not all_processed_articles:
            logger.info("No articles found in any feed")
            
            # Maybe post educational content instead
            if settings.enable_educational_content and self.posts_today < settings.max_posts_per_day:
                if await self.post_educational_content():
                    self.posts_today += 1
            return
        
        # Score and rank articles
        logger.info(f"Scoring {len(all_processed_articles)} articles...")
        top_articles = ArticleScorer.select_top_n(
            all_processed_articles,
            n=settings.max_news_per_cycle
        )
        
        logger.info(
            f"Selected top {len(top_articles)} articles from {len(all_processed_articles)} total"
        )
        
        # Post top articles
        for processed_article in top_articles:
            # Check daily limit
            if self.posts_today >= settings.max_posts_per_day:
                logger.warning(f"Daily limit reached ({settings.max_posts_per_day}). Stopping.")
                break
            
            if await self.process_and_post_article(processed_article):
                posted_count += 1
                self.posts_today += 1
                
                # Wait between posts
                await asyncio.sleep(15)
                
                # Maybe post educational content after some news
                if settings.enable_educational_content:
                    if random.random() < settings.educational_content_frequency:
                        if self.posts_today < settings.max_posts_per_day:
                            logger.info("Mixing in educational content...")
                            if await self.post_educational_content():
                                self.posts_today += 1
                            await asyncio.sleep(15)
        
        logger.info(
            f"Posting cycle complete. Posted {posted_count} articles. "
            f"Total posts today: {self.posts_today}/{settings.max_posts_per_day}"
        )
    
    async def start(self):
        """Start the scheduler loop."""
        self.running = True
        logger.info("Scheduler started")
        
        while self.running:
            try:
                await self.run_cycle()
                
                # Wait for next cycle
                wait_minutes = settings.check_interval_minutes
                logger.info(f"Waiting {wait_minutes} minutes until next cycle...")
                await asyncio.sleep(settings.check_interval_seconds)
                
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received, stopping...")
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                logger.info("Waiting 5 minutes before retry...")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def stop(self):
        """Stop the scheduler."""
        logger.info("Stopping scheduler...")
        self.running = False
        await self.telegram_service.disconnect()
        await db.close()
        logger.success("Scheduler stopped")
