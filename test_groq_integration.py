
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.groq_service import GroqService
from src.core.dynamic_content_fetcher import DynamicContentFetcher
from loguru import logger

async def test_groq():
    logger.info("Testing Groq Service...")
    service = GroqService()
    
    # Test 1: Generate Summary
    logger.info("Test 1: Summarize article (High Density)")
    summary = await service.generate_summary(
        text="Python 3.12 was released with significant performance improvements and error message enhancements.",
        title="Python 3.12 Released",
        link="https://python.org"
    )
    if summary:
        logger.success(f"Groq Summary: {summary}")
        # Test formatting
        from src.core.content_formatter import ContentFormatter
        formatted = ContentFormatter.format_message_groq(summary, "https://python.org")
        logger.info(f"Formatted Message Preview:\n{formatted}")
    else:
        logger.error("Groq Summary failed")

    # Test 2: Dynamic Content Fetcher (AI Fact)
    logger.info("Test 2: Dynamic Content Fetcher (AI Fact)")
    fetcher = DynamicContentFetcher()
    fact = await fetcher.generate_ai_fact()
    if fact:
        logger.success(f"AI Fact: {fact}")
    else:
        logger.error("AI Fact failed")

    # Test 3: Coding Lesson
    logger.info("Test 3: Coding Lesson")
    lesson = await fetcher.generate_coding_lesson()
    if lesson:
        logger.success(f"Coding Lesson: {lesson}")
    else:
        logger.error("Coding Lesson failed")

if __name__ == "__main__":
    asyncio.run(test_groq())
