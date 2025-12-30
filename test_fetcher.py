"""Test script for DynamicContentFetcher."""
import asyncio
import sys
from loguru import logger

# Add src to path
import os
sys.path.append(os.getcwd())

from src.core.dynamic_content_fetcher import DynamicContentFetcher

async def test_fetcher():
    fetcher = DynamicContentFetcher()
    
    print("Testing DynamicContentFetcher...")
    print("-" * 50)
    
    # Test RSS
    print("\n1. Testing RSS Fetch (Tutorial)...")
    content = await fetcher.fetch_rss_content('tutorial')
    if content:
        print("✅ SUCCESS!")
        print(f"Title: {content['title']}")
        print(f"Content Length: {len(content['content'])}")
        print(f"Hashtags: {content['hashtags']}")
    else:
        print("❌ FAILED to fetch RSS content")

    # Test Tech Quote
    print("\n2. Testing Tech Quote API...")
    quote = await fetcher.fetch_tech_quote()
    if quote:
        print("✅ SUCCESS!")
        print(f"Quote: {quote['content']}")
        print(f"Hashtags: {quote['hashtags']}")
    else:
        print("❌ FAILED to fetch quote")
        
    # Test Random
    print("\n3. Testing Random Fetch...")
    random_content = await fetcher.get_random_content()
    if random_content:
        print("✅ SUCCESS!")
        print(f"Type: {random_content['title']}")
    else:
        print("❌ FAILED random fetch")

if __name__ == "__main__":
    asyncio.run(test_fetcher())
