"""Configuration management using Pydantic settings."""

from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Telegram API
    api_id: int = Field(..., description="Telegram API ID")
    api_hash: str = Field(..., description="Telegram API Hash")
    phone_number: str = Field(..., description="Phone number with country code")
    channel_username: str = Field(default="@mirzohamidov", description="Target channel")
    
    # Social Media Links
    telegram_link: str = Field(default="https://t.me/mirzohamidov", description="Telegram profile link")
    linkedin_link: str = Field(default="https://linkedin.com/in/yourprofile", description="LinkedIn profile link")
    website_link: str = Field(default="https://yourwebsite.com", description="Personal website link")
    
    # RSS Feeds
    rss_feeds: str = Field(
        default="https://www.techcrunch.com/feed/,https://www.wired.com/feed/rss,https://dev.to/feed,https://www.freecodecamp.org/news/rss/,https://css-tricks.com/feed/,https://www.smashingmagazine.com/feed/,https://towardsdatascience.com/feed,https://machinelearningmastery.com/feed/,https://www.artificialintelligence-news.com/feed/,https://hnrss.org/frontpage,https://www.producthunt.com/feed,https://www.geeksforgeeks.org/feed/,https://betterprogramming.pub/feed,https://news.ycombinator.com/rss,https://feeds.feedburner.com/TheHackersNews",
        description="Comma-separated RSS feed URLs"
    )
    
    # Keywords
    keywords: str = Field(
        default="tech,innovation,ai,future,artificial intelligence,startup,coding,programming,tutorial,python,javascript,web development,data science,machine learning,cybersecurity,linux,devops",
        description="Comma-separated keywords for filtering"
    )
    
    # Features
    enable_translation: bool = Field(default=True, description="Enable translation")
    enable_image_fetching: bool = Field(default=True, description="Enable image extraction")
    
    # Content Curation
    max_news_per_cycle: int = Field(default=10, description="Maximum news articles per cycle")
    max_posts_per_day: int = Field(default=50, description="Maximum total posts per day")
    enable_educational_content: bool = Field(default=True, description="Enable educational content")
    educational_content_frequency: float = Field(default=0.5, description="Probability of educational post (0-1)")
    
    # Dynamic Content
    enable_dynamic_content: bool = Field(default=True, description="Enable fetching from RSS/APIs")
    dynamic_content_ratio: float = Field(default=0.8, description="Ratio of dynamic vs static content")

    
    
    # Scheduling
    check_interval_minutes: int = Field(default=30, description="Minutes between feed checks")
    max_article_age_hours: int = Field(default=24, description="Maximum article age in hours")
    
    # Database
    database_path: str = Field(default="data/autopost.db", description="SQLite database path")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_rotation: str = Field(default="10 MB", description="Log rotation size")
    log_retention: int = Field(default=5, description="Number of log files to keep")
    
    # Translation
    translation_target_lang: str = Field(default="uz", description="Primary translation language")
    target_languages: List[str] = Field(default=["uz"], description="Target languages for posts")
    translation_secondary_lang: str = Field(default="ru", description="Secondary translation language")
    translation_backend: str = Field(default="bing", description="Translation backend")
    
    # Groq API
    groq_api_key: str = Field(default="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", description="Groq API Key")
    
    # Request Settings
    request_timeout: int = Field(default=15, description="HTTP request timeout in seconds")
    user_agent: str = Field(
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        description="User agent for HTTP requests"
    )
    
    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number format."""
        if not v.startswith("+"):
            raise ValueError("Phone number must start with + and country code")
        return v
    
    @field_validator("channel_username")
    @classmethod
    def validate_channel(cls, v: str) -> str:
        """Validate channel username format."""
        if not v.startswith("@"):
            return f"@{v}"
        return v
    
    @property
    def rss_feed_list(self) -> List[str]:
        """Get RSS feeds as a list."""
        return [feed.strip() for feed in self.rss_feeds.split(",") if feed.strip()]
    
    @property
    def keyword_list(self) -> List[str]:
        """Get keywords as a lowercase list."""
        return [kw.strip().lower() for kw in self.keywords.split(",") if kw.strip()]
    
    @property
    def check_interval_seconds(self) -> int:
        """Get check interval in seconds."""
        return self.check_interval_minutes * 60


# Global settings instance
settings = Settings()
