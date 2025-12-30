"""Content formatter for creating Telegram messages."""

from typing import Dict, Any
from loguru import logger

from src.config.settings import settings


class ContentFormatter:
    """Service for formatting content for Telegram posts."""
    
    @staticmethod
    def create_social_footer() -> str:
        """Create footer with channel link only."""
        # Requirement: "at the bottom channel link only"
        if settings.telegram_link:
            return f"👉 <a href='{settings.telegram_link}'>Kanalga obuna bo'ling</a>"
        return ""

    @staticmethod
    def _format_summary(summary: Any) -> str:
        """Format summary which might be a string or a structured dict."""
        if isinstance(summary, str):
            return summary
            
        if isinstance(summary, dict):
            parts = []
            for key, value in summary.items():
                # Capitalize key roughly usually it's "⚡ Qisqacha" etc
                parts.append(f"<b>{key}</b>")
                if isinstance(value, list):
                    for item in value:
                        parts.append(f"• {item}")
                elif isinstance(value, dict):
                    # Handle nested dicts (seen in logs: '🔑 Asosiy Qismlar': {'tafsilotlar': [...]})
                    for k, v in value.items():
                        if isinstance(v, list):
                             for item in v:
                                parts.append(f"• {item}")
                        else:
                            parts.append(f"• {v}")
                else:
                    parts.append(f"{value}")
                parts.append("") # Spacer
            return "\n".join(parts)
            
        return str(summary)

    @staticmethod
    def format_message_groq(
        groq_content: Dict[str, Any],
        article_link: str,
    ) -> str:
        """
        Format the message using Groq-generated content.
        
        Args:
            groq_content: Dict with 'title', 'summary', 'hashtags'
            article_link: URL to the original article
        
        Returns:
            Formatted HTML message
        """
        title = groq_content.get("title", "")
        summary_raw = groq_content.get("summary", "")
        hashtags = groq_content.get("hashtags", "")
        
        # Format summary if it is a dict
        summary = ContentFormatter._format_summary(summary_raw)
        
        # Build message
        message_parts = []
        
        # Title (Groq likely adds emoji, but we ensure bold)
        message_parts.append(f"<b>{title}</b>")
        message_parts.append("")
        
        # Summary
        message_parts.append(summary)
        message_parts.append("")
        
        # Source Link
        if article_link:
             message_parts.append(f"🔗 <a href='{article_link}'>Manba</a>")
             message_parts.append("")

        # Hashtags
        if hashtags:
            message_parts.append(hashtags)
        
        # Footer
        footer = ContentFormatter.create_social_footer()
        if footer:
            message_parts.append("")
            message_parts.append("━━━━━━━━━━━━━━━━━━━━")
            message_parts.append(footer)
        
        return "\n".join(message_parts)

    @staticmethod
    def validate_message_length(message: str, has_image: bool = False) -> bool:
        """
        Validate message length against Telegram limits.
        
        Args:
            message: Message text
            has_image: Whether message will be sent with an image
        
        Returns:
            True if valid, False otherwise
        """
        max_length = 1024 if has_image else 4096
        
        if len(message) > max_length:
            logger.error(
                f"Message too long: {len(message)} characters "
                f"(max: {max_length} for {'image' if has_image else 'text'})"
            )
            return False
        
        return True

