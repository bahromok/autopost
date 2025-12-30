"""Configuration check and fix script."""

import os
from pathlib import Path

# Read current .env
env_path = Path('.env')
if env_path.exists():
    with open(env_path, 'r') as f:
        content = f.read()
    
    print("Current .env content (first 500 chars):")
    print(content[:500])
    print("\n" + "="*60 + "\n")

# Create corrected .env with exact values from screenshot
corrected_env = """# Telegram API credentials (Get from https://my.telegram.org)
API_ID=28739061
API_HASH=c90fc951dfdace987eb56e2c467175599
PHONE_NUMBER=+998901234567

# Channel to post to
CHANNEL_USERNAME=@mirzohamidov

# Social Media Links (shown in post footer)
TELEGRAM_LINK=https://t.me/mirzohamidov
LINKEDIN_LINK=https://linkedin.com/in/yourprofile
WEBSITE_LINK=https://yourwebsite.com

# RSS Feed URLs (comma-separated)
RSS_FEEDS=https://www.techcrunch.com/feed/,https://www.wired.com/feed/rss,https://www.cnet.com/rss/news/,https://www.bbc.com/news/technology/rss.xml

# Keywords for filtering (comma-separated, lowercase)
KEYWORDS=tech,innovation,ai,future,artificial intelligence,startup,gadget,robotics,computing,software,machine learning,deep learning,neural network

# Features
ENABLE_TRANSLATION=true
ENABLE_IMAGE_FETCHING=true

# Scheduling
CHECK_INTERVAL_MINUTES=60
MAX_ARTICLE_AGE_HOURS=24

# Database
DATABASE_PATH=data/autopost.db

# Logging
LOG_LEVEL=INFO
LOG_ROTATION=10 MB
LOG_RETENTION=5

# Translation
TRANSLATION_TARGET_LANG=uz
TRANSLATION_SECONDARY_LANG=ru
TRANSLATION_BACKEND=bing

# Request Settings
REQUEST_TIMEOUT=15
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
"""

# Write corrected version
with open('.env', 'w', encoding='utf-8') as f:
    f.write(corrected_env)

print("✓ Created fresh .env file with correct formatting")
print("\nIMPORTANT: Please update these values:")
print("  - PHONE_NUMBER: Your actual phone number with country code")
print("  - LINKEDIN_LINK: Your LinkedIn profile URL")
print("  - WEBSITE_LINK: Your website URL")
print("\nAPI Credentials from screenshot:")
print("  API_ID: 28739061")
print("  API_HASH: c90fc951dfdace987eb56e2c467175599")
