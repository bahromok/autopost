"""Test script for message length handling."""
import asyncio
from src.core.content_formatter import ContentFormatter

def test_truncation():
    print("Testing Content Truncation...")
    print("-" * 50)
    
    long_text = "This is a very long text. " * 50  # ~1300 chars
    
    translations = {
        "title": {
            "en": "Short Title",
            "uz": "Short Title UZ",
            "ru": "Short Title RU"
        },
        "summary": {
            "en": long_text,
            "uz": long_text,
            "ru": long_text
        }
    }
    
    # Test formatting
    formatted = ContentFormatter.format_message(translations, "https://example.com")
    
    print(f"Original Content Length: {len(long_text) * 3 + 500} (approx)")
    print(f"Formatted Length: {len(formatted)}")
    
    if len(formatted) <= 1024:
        print("✅ SUCCESS: Message truncated to <= 1024 chars")
    else:
        print(f"❌ FAILED: Message length {len(formatted)} > 1024")

if __name__ == "__main__":
    test_truncation()
