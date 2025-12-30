"""Database models using SQLAlchemy."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Feed(Base):
    """RSS feed source."""
    
    __tablename__ = "feeds"
    
    id = Column(Integer, primary_key=True)
    url = Column(String(500), unique=True, nullable=False, index=True)
    name = Column(String(200))
    enabled = Column(Boolean, default=True)
    last_checked = Column(DateTime)
    last_success = Column(DateTime)
    error_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    articles = relationship("Article", back_populates="feed", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Feed(id={self.id}, url='{self.url}', enabled={self.enabled})>"


class Article(Base):
    """Posted article."""
    
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True)
    feed_id = Column(Integer, ForeignKey("feeds.id"), nullable=False)
    url = Column(String(1000), unique=True, nullable=False, index=True)
    title = Column(String(500))
    summary = Column(Text)
    published_at = Column(DateTime)
    posted_at = Column(DateTime, default=datetime.utcnow)
    image_url = Column(String(1000))
    telegram_message_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    feed = relationship("Feed", back_populates="articles")
    logs = relationship("PostingLog", back_populates="article", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Article(id={self.id}, title='{self.title[:50]}...', url='{self.url}')>"


class PostingLog(Base):
    """Audit log for posting attempts."""
    
    __tablename__ = "posting_logs"
    
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    status = Column(String(20), nullable=False)  # 'success', 'failed', 'skipped'
    error_message = Column(Text)
    attempt_count = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    article = relationship("Article", back_populates="logs")
    
    def __repr__(self):
        return f"<PostingLog(id={self.id}, article_id={self.article_id}, status='{self.status}')>"


class Statistics(Base):
    """Daily posting statistics."""
    
    __tablename__ = "statistics"
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, unique=True, nullable=False, index=True)
    articles_checked = Column(Integer, default=0)
    articles_posted = Column(Integer, default=0)
    articles_failed = Column(Integer, default=0)
    articles_skipped = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<Statistics(date={self.date}, posted={self.articles_posted})>"
