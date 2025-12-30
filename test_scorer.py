
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.article_scorer import ArticleScorer
from loguru import logger

def test_scorer():
    logger.info("Testing ArticleScorer with Dict Summary...")
    
    # Mock data with DICT summary (which caused the crash)
    article_data = {
        'title': 'New AI Breakthrough from OpenAI',
        'summary': {
            '⚡ Qisqacha': 'OpenAI releases new model.',
            '🔑 Asosiy Qismlar': ['Huge performance jump', 'Python support'],
            '💡 Xulosa': 'Game changing for developers.'
        },
        'link': 'https://techcrunch.com/news/ai',
        'published_at': datetime.now()
    }
    
    try:
        score = ArticleScorer.score_article(article_data)
        logger.success(f"Score calculated successfully: {score}")
    except TypeError as e:
        logger.error(f"TypeError caught: {e}")
    except Exception as e:
        logger.error(f"Other error: {e}")

if __name__ == "__main__":
    test_scorer()
