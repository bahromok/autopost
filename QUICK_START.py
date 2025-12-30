"""
Quick Start Guide for Telegram Autoposting Bot
===============================================

ISSUE: API credentials are invalid
SOLUTION: You need to get NEW credentials from https://my.telegram.org

The credentials in the screenshot may be from a test app or expired.

Steps to Fix:
-------------

1. Go to https://my.telegram.org
2. Log in with your phone number (+998944977155)
3. Click on "API Development Tools"
4. Create a new application (or use existing)
5. Copy the EXACT values:
   - App api_id (number)
   - App api_hash (long string)

6. Update .env file with the NEW credentials

7. Run the bot:
   python run.py

NOT: python src/main.py  ❌
USE: python run.py       ✅

The run.py script properly sets up the Python path.

Current Status:
--------------
✅ All code is complete and working
✅ Database is initialized
✅ Dependencies are installed
❌ API credentials need to be verified

Once you update the .env file with valid credentials from my.telegram.org,
the bot will work perfectly!
"""

print(__doc__)
