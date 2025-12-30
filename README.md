# Professional Telegram Autoposting Bot

A professional, enterprise-grade Telegram autoposting bot that fetches tech news from RSS feeds and posts to **@mirzohamidov** channel with multi-language support (Uzbek, Russian, English) and images.

## Features

✨ **Professional Architecture**
- Modular design with separation of concerns
- SQLite database for persistent storage
- Async/await throughout for performance
- Comprehensive error handling and retry logic

📰 **Content Management**
- RSS feed aggregation from multiple sources
- Keyword-based filtering
- Duplicate detection
- Age-based filtering

🌍 **Multi-Language Support**
- Automatic translation to Uzbek and Russian
- Fallback mechanisms for translation failures
- Original English content preserved

🖼️ **Image Support**
- Automatic image extraction from RSS feeds
- Open Graph image fallback
- Graceful fallback to text-only posts

📊 **Analytics & Logging**
- Posting statistics tracking
- Structured logging with rotation
- Error tracking and reporting

🔗 **Custom Branding**
- Social media footer with your links
- Professional message formatting
- Hashtag generation

## Installation

### Prerequisites
- Python 3.9 or higher
- Telegram API credentials ([Get them here](https://my.telegram.org))

### Setup

1. **Clone or download the project**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env with your credentials
   # Add your API_ID, API_HASH, PHONE_NUMBER
   ```

4. **Initialize database**
   ```bash
   python -m src.database.database
   ```

5. **Run the bot**
   ```bash
   python run.py
   ```

## Configuration

Edit `.env` file with your settings:

```env
# Telegram API (from https://my.telegram.org)
API_ID=your_api_id
API_HASH=your_api_hash
PHONE_NUMBER=+998901234567

# Channel
CHANNEL_USERNAME=@mirzohamidov

# Social Media Links (shown in post footer)
TELEGRAM_LINK=https://t.me/yourusername
LINKEDIN_LINK=https://linkedin.com/in/yourprofile
WEBSITE_LINK=https://yourwebsite.com

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
```

## Project Structure

```
telegram_autopost/
├── src/
│   ├── config/           # Configuration management
│   ├── database/         # Database models and repositories
│   ├── services/         # External service integrations
│   ├── core/             # Business logic
│   └── utils/            # Utilities and helpers
├── data/                 # Database and logs
├── tests/                # Unit tests
├── .env                  # Environment configuration
├── requirements.txt      # Python dependencies
├── run.py               # Application launcher
└── README.md            # This file
```

## Usage

### First Run

On first run, you'll be prompted to authenticate with Telegram:
1. Enter the code sent to your phone
2. If you have 2FA enabled, enter your password
3. The session will be saved for future runs

### Normal Operation

The bot will:
1. Check RSS feeds every hour (configurable)
2. Filter articles by keywords
3. Translate to Uzbek and Russian
4. Extract images when available
5. Post to @mirzohamidov channel
6. Track posted articles to avoid duplicates

### Graceful Shutdown

Press `Ctrl+C` to stop the bot gracefully. It will finish the current operation and save state.

## Troubleshooting

### Authentication Issues
- Ensure API_ID and API_HASH are correct
- Delete `*.session` files and re-authenticate
- Check phone number format (+998...)

### Translation Failures
- The bot uses multiple translation backends with fallback
- If all fail, it posts in English only
- Check internet connection

### Image Loading Failures
- Some RSS feeds don't provide images
- Bot automatically falls back to text-only posts
- Check logs for specific errors

### Database Errors
- Ensure `data/` directory exists and is writable
- Delete `data/autopost.db` to reset (loses history)
- Check disk space

## Logs

Logs are stored in `data/logs/` with automatic rotation:
- `autopost.log` - Main application log
- Rotates at 10 MB by default
- Keeps last 5 log files

## Development

### Running Tests
```bash
pytest tests/ -v --cov=src
```

### Code Style
```bash
# Format code
black src/

# Type checking
mypy src/
```

## Architecture

The bot follows a layered architecture:

1. **Config Layer** - Environment and settings management
2. **Database Layer** - Data persistence with SQLAlchemy
3. **Service Layer** - External integrations (RSS, Translation, Telegram)
4. **Core Layer** - Business logic and orchestration
5. **Utils Layer** - Cross-cutting concerns (logging, retry, validation)

## Security

- ✅ No credentials in code
- ✅ Session files in `.gitignore`
- ✅ Environment variable validation
- ✅ Secure credential storage

## License

MIT License - Feel free to use and modify

## Support

For issues or questions:
- Check logs in `data/logs/`
- Review configuration in `.env`
- Ensure all dependencies are installed

## Credits

Built with:
- [Telethon](https://github.com/LonamiWebs/Telethon) - Telegram client
- [SQLAlchemy](https://www.sqlalchemy.org/) - Database ORM
- [Feedparser](https://github.com/kurtmckee/feedparser) - RSS parsing
- [Pydantic](https://pydantic.dev/) - Configuration validation

---

**Channel**: [@mirzohamidov](https://t.me/mirzohamidov)
