"""Data access layer - repositories for database operations."""

from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.database.models import Feed, Article, PostingLog, Statistics


class FeedRepository:
    """Repository for Feed operations."""
    
    @staticmethod
    async def create(session: AsyncSession, url: str, name: Optional[str] = None) -> Feed:
        """Create a new feed."""
        feed = Feed(url=url, name=name)
        session.add(feed)
        await session.commit()
        await session.refresh(feed)
        logger.info(f"Created feed: {url}")
        return feed
    
    @staticmethod
    async def get_by_url(session: AsyncSession, url: str) -> Optional[Feed]:
        """Get feed by URL."""
        result = await session.execute(select(Feed).where(Feed.url == url))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all_enabled(session: AsyncSession) -> List[Feed]:
        """Get all enabled feeds."""
        result = await session.execute(select(Feed).where(Feed.enabled == True))
        return list(result.scalars().all())
    
    @staticmethod
    async def update_last_checked(session: AsyncSession, feed_id: int, success: bool = True):
        """Update feed last checked timestamp."""
        result = await session.execute(select(Feed).where(Feed.id == feed_id))
        feed = result.scalar_one_or_none()
        if feed:
            feed.last_checked = datetime.utcnow()
            if success:
                feed.last_success = datetime.utcnow()
                feed.error_count = 0
            else:
                feed.error_count += 1
            await session.commit()


class ArticleRepository:
    """Repository for Article operations."""
    
    @staticmethod
    async def create(
        session: AsyncSession,
        feed_id: int,
        url: str,
        title: str,
        summary: str,
        published_at: Optional[datetime] = None,
        image_url: Optional[str] = None,
        telegram_message_id: Optional[int] = None,
    ) -> Article:
        """Create a new article."""
        article = Article(
            feed_id=feed_id,
            url=url,
            title=title,
            summary=summary,
            published_at=published_at,
            image_url=image_url,
            telegram_message_id=telegram_message_id,
        )
        session.add(article)
        await session.commit()
        await session.refresh(article)
        logger.info(f"Created article: {title}")
        return article
    
    @staticmethod
    async def get_by_url(session: AsyncSession, url: str) -> Optional[Article]:
        """Get article by URL."""
        result = await session.execute(select(Article).where(Article.url == url))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def exists(session: AsyncSession, url: str) -> bool:
        """Check if article exists."""
        result = await session.execute(select(Article.id).where(Article.url == url))
        return result.scalar_one_or_none() is not None
    
    @staticmethod
    async def get_recent(session: AsyncSession, limit: int = 100) -> List[Article]:
        """Get recent articles."""
        result = await session.execute(
            select(Article).order_by(Article.posted_at.desc()).limit(limit)
        )
        return list(result.scalars().all())


class PostingLogRepository:
    """Repository for PostingLog operations."""
    
    @staticmethod
    async def create(
        session: AsyncSession,
        article_id: int,
        status: str,
        error_message: Optional[str] = None,
        attempt_count: int = 1,
    ) -> PostingLog:
        """Create a posting log entry."""
        log = PostingLog(
            article_id=article_id,
            status=status,
            error_message=error_message,
            attempt_count=attempt_count,
        )
        session.add(log)
        await session.commit()
        await session.refresh(log)
        return log
    
    @staticmethod
    async def get_by_article(session: AsyncSession, article_id: int) -> List[PostingLog]:
        """Get all logs for an article."""
        result = await session.execute(
            select(PostingLog).where(PostingLog.article_id == article_id)
        )
        return list(result.scalars().all())


class StatisticsRepository:
    """Repository for Statistics operations."""
    
    @staticmethod
    async def get_or_create_today(session: AsyncSession) -> Statistics:
        """Get or create statistics for today."""
        today = date.today()
        result = await session.execute(
            select(Statistics).where(func.date(Statistics.date) == today)
        )
        stats = result.scalar_one_or_none()
        
        if not stats:
            stats = Statistics(date=datetime.combine(today, datetime.min.time()))
            session.add(stats)
            await session.commit()
            await session.refresh(stats)
        
        return stats
    
    @staticmethod
    async def increment_checked(session: AsyncSession):
        """Increment articles checked count."""
        stats = await StatisticsRepository.get_or_create_today(session)
        stats.articles_checked += 1
        await session.commit()
    
    @staticmethod
    async def increment_posted(session: AsyncSession):
        """Increment articles posted count."""
        stats = await StatisticsRepository.get_or_create_today(session)
        stats.articles_posted += 1
        await session.commit()
    
    @staticmethod
    async def increment_failed(session: AsyncSession):
        """Increment articles failed count."""
        stats = await StatisticsRepository.get_or_create_today(session)
        stats.articles_failed += 1
        await session.commit()
    
    @staticmethod
    async def increment_skipped(session: AsyncSession):
        """Increment articles skipped count."""
        stats = await StatisticsRepository.get_or_create_today(session)
        stats.articles_skipped += 1
        await session.commit()
    
    @staticmethod
    async def get_recent(session: AsyncSession, days: int = 7) -> List[Statistics]:
        """Get statistics for recent days."""
        result = await session.execute(
            select(Statistics).order_by(Statistics.date.desc()).limit(days)
        )
        return list(result.scalars().all())
