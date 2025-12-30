"""Update .env with dynamic content settings."""
import os

settings_to_add = """
# Dynamic Content
ENABLE_DYNAMIC_CONTENT=true
DYNAMIC_CONTENT_RATIO=0.8
"""

if os.path.exists('.env'):
    with open('.env', 'a') as f:
        f.write(settings_to_add)
    print("Updated .env")
else:
    print(".env not found")
