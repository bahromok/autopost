# settings.py

# List of RSS feed URLs
RSS_FEEDS = [
    'https://www.techcrunch.com/feed/',
    'https://www.wired.com/feed/rss',
    'https://www.cnet.com/rss/news/',
    'https://www.bbc.com/news/technology/rss.xml',
]

# Keywords to filter articles
KEYWORDS = ['tech', 'innovation', 'ai', 'future', 'artificial intelligence', 'startup', 'gadget', 'robotics', 'computing', 'software']

# File to store posted links
POSTED_LINKS_FILE = 'posted_links.txt'

# Intervals and Age Limit
CHECK_INTERVAL_SECONDS = 3600  # 1 hour
MAX_ARTICLE_AGE_HOURS = 24

# Translation & Image Config
TARGET_LANGUAGE = 'uz'  # Target language code (Uzbek)
ENABLE_TRANSLATION = True  # Set to False to post in English
ENABLE_IMAGE_FETCHING = True  # Set to False to only post text
REQUEST_TIMEOUT = 15  # Seconds to wait for fetching article page

# Headers to mimic a browser when fetching pages
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
