"""Image extraction service."""

from typing import Optional, Dict, Any
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from loguru import logger

from src.config.settings import settings


class ImageService:
    """Service for extracting images from RSS feeds and web pages."""
    
    @staticmethod
    def extract_from_rss(entry: Dict[str, Any]) -> Optional[str]:
        """Extract image URL from RSS feed entry."""
        if not settings.enable_image_fetching:
            return None
        
        # Check standard media tags
        for key in ["media_content", "media_thumbnail", "enclosures"]:
            if key in entry:
                for item in entry[key]:
                    # Check for image in media_content
                    if "url" in item and "image" in item.get("medium", ""):
                        url = item["url"]
                        logger.info(f"Found image in RSS {key}: {url}")
                        return url
                    
                    # Check for image in href
                    if "href" in item and "image" in item.get("type", ""):
                        url = item["href"]
                        logger.info(f"Found image in RSS {key}: {url}")
                        return url
        
        return None
    
    @staticmethod
    def extract_from_page(article_url: str) -> Optional[str]:
        """Extract Open Graph image from article page."""
        if not settings.enable_image_fetching or not article_url:
            return None
        
        try:
            logger.info(f"Fetching page for image: {article_url}")
            
            response = requests.get(
                article_url,
                headers={"User-Agent": settings.user_agent},
                timeout=settings.request_timeout,
                allow_redirects=True,
            )
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get("content-type", "").lower()
            if "html" not in content_type:
                logger.warning(
                    f"Content type is not HTML ({content_type}), "
                    f"skipping image parse for {article_url}"
                )
                return None
            
            # Parse HTML
            soup = BeautifulSoup(response.text, "lxml")
            
            # Look for Open Graph image
            og_image_tag = soup.find("meta", property="og:image")
            if og_image_tag and og_image_tag.get("content"):
                image_url = og_image_tag["content"]
                
                # Handle relative URLs
                if image_url.startswith("/"):
                    image_url = urljoin(article_url, image_url)
                
                logger.success(f"Found og:image: {image_url}")
                return image_url
            
            # Fallback: look for Twitter image
            twitter_image_tag = soup.find("meta", attrs={"name": "twitter:image"})
            if twitter_image_tag and twitter_image_tag.get("content"):
                image_url = twitter_image_tag["content"]
                if image_url.startswith("/"):
                    image_url = urljoin(article_url, image_url)
                logger.success(f"Found twitter:image: {image_url}")
                return image_url
            
            logger.info(f"No image meta tags found on page: {article_url}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch article page {article_url}: {e}")
        except Exception as e:
            logger.error(f"Error parsing page {article_url} for image: {e}")
        
        return None
    
    @staticmethod
    def extract_image(entry: Dict[str, Any], article_url: str) -> Optional[str]:
        """
        Extract image URL from RSS entry or article page.
        
        Args:
            entry: Raw RSS entry
            article_url: URL of the article
        
        Returns:
            Image URL or None
        """
        # Try RSS first
        image_url = ImageService.extract_from_rss(entry)
        if image_url:
            return image_url
        
        # Fallback to page scraping
        return ImageService.extract_from_page(article_url)
    
    @staticmethod
    def validate_image_url(url: Optional[str]) -> bool:
        """Validate that an image URL is accessible."""
        if not url:
            return False
        
        try:
            response = requests.head(
                url,
                headers={"User-Agent": settings.user_agent},
                timeout=5,
                allow_redirects=True,
            )
            
            content_type = response.headers.get("content-type", "").lower()
            is_image = "image" in content_type
            
            if is_image:
                logger.success(f"Image URL validated: {url}")
            else:
                logger.warning(f"URL is not an image: {url} ({content_type})")
            
            return is_image
            
        except Exception as e:
            logger.error(f"Failed to validate image URL {url}: {e}")
            return False
