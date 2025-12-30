"""Article scoring and ranking system."""

from datetime import datetime
from typing import Dict, Any
from urllib.parse import urlparse
from loguru import logger


class ArticleScorer:
    """Scores articles by importance and relevance."""
    
    # Source reputation scores
    SOURCE_SCORES = {
        'techcrunch.com': 30,
        'wired.com': 25,
        'bbc.com': 20,
        'cnet.com': 15,
    }
    
    # High-impact keywords (worth more points)
    HIGH_IMPACT_KEYWORDS = [
        # AI & ML - highest priority
        'ai', 'artificial intelligence', 'chatgpt', 'gpt-4', 'gpt-5', 'claude',
        'gemini', 'llama', 'machine learning', 'deep learning', 'neural network',
        'transformer', 'diffusion', 'stable diffusion', 'midjourney', 'dall-e',
        # Major announcements
        'breakthrough', 'major', 'announces', 'launches', 'releases', 'unveils',
        'revolutionary', 'game-changing', 'first-ever', 'new model',
        # Security & Important
        'security breach', 'vulnerability', 'zero-day', 'hack', 'breach',
        # Business
        'acquisition', 'funding', 'ipo', 'billion', 'million', 'raises',
        # Programming & Dev
        'programming', 'python', 'javascript', 'rust', 'go', 'framework',
        'open source', 'github', 'developer', 'coding',
    ]
    
    # Major tech companies and AI labs
    MAJOR_COMPANIES = [
        # AI Labs (highest priority)
        'openai', 'anthropic', 'deepmind', 'google ai', 'meta ai',
        # Big Tech
        'google', 'apple', 'microsoft', 'meta', 'facebook', 'amazon',
        'tesla', 'nvidia', 'spacex', 'twitter', 'x corp',
        # Important Tech
        'samsung', 'intel', 'amd', 'qualcomm', 'arm',
        'github', 'gitlab', 'stackoverflow', 'reddit',
    ]
    
    @staticmethod
    def extract_domain(url: str) -> str:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            return parsed.netloc.replace('www.', '')
        except Exception:
            return ''
    
    @staticmethod
    def score_source(url: str) -> float:
        """Score based on source reputation (0-30 points)."""
        domain = ArticleScorer.extract_domain(url)
        return ArticleScorer.SOURCE_SCORES.get(domain, 10)
    
    @staticmethod
    def _get_text_content(content: Any) -> str:
        """Extract text content from string or dict summary."""
        if isinstance(content, str):
            return content
        if isinstance(content, dict):
            parts = []
            for key, value in content.items():
                parts.append(str(key))
                if isinstance(value, (list, tuple)):
                    parts.extend([str(v) for v in value])
                elif isinstance(value, dict):
                    parts.append(ArticleScorer._get_text_content(value))
                else:
                    parts.append(str(value))
            return " ".join(parts)
        return str(content)

    @staticmethod
    def score_keywords(title: str, summary: Any) -> float:
        """Score based on high-impact keywords (0-25 points)."""
        summary_text = ArticleScorer._get_text_content(summary)
        text = (title + ' ' + summary_text).lower()
        score = 0
        
        for keyword in ArticleScorer.HIGH_IMPACT_KEYWORDS:
            if keyword in text:
                score += 5
        
        return min(score, 25)  # Cap at 25
    
    @staticmethod
    def score_recency(published_at: datetime) -> float:
        """Score based on article age (0-20 points)."""
        if not published_at:
            return 5  # Default for unknown age
        
        hours_old = (datetime.now() - published_at).total_seconds() / 3600
        
        if hours_old < 2:
            return 20
        elif hours_old < 6:
            return 15
        elif hours_old < 12:
            return 10
        elif hours_old < 24:
            return 5
        else:
            return 0
    
    @staticmethod
    def score_companies(title: str, summary: Any) -> float:
        """Score based on major company mentions (0-15 points)."""
        summary_text = ArticleScorer._get_text_content(summary)
        text = (title + ' ' + summary_text).lower()
        score = 0
        
        for company in ArticleScorer.MAJOR_COMPANIES:
            if company in text:
                score += 3
        
        return min(score, 15)  # Cap at 15
    
    @staticmethod
    def score_engagement(title: str) -> float:
        """Score based on engagement indicators (0-10 points)."""
        engagement_words = ['breaking', 'exclusive', 'first', 'new', 'just']
        title_lower = title.lower()
        
        if any(word in title_lower for word in engagement_words):
            return 10
        return 0
    
    @staticmethod
    def score_article(article_data: Dict[str, Any]) -> float:
        """
        Calculate total article score (0-100).
        
        Components:
        - Source reputation: 0-30 points
        - High-impact keywords: 0-25 points
        - Recency: 0-20 points
        - Company mentions: 0-15 points
        - Engagement indicators: 0-10 points
        
        Total: 0-100 points
        """
        title = article_data.get('title', '')
        summary = article_data.get('summary', '')
        link = article_data.get('link', '')
        published_at = article_data.get('published_at')
        
        # Calculate component scores
        source_score = ArticleScorer.score_source(link)
        keyword_score = ArticleScorer.score_keywords(title, summary)
        recency_score = ArticleScorer.score_recency(published_at)
        company_score = ArticleScorer.score_companies(title, summary)
        engagement_score = ArticleScorer.score_engagement(title)
        
        # Total score
        total = source_score + keyword_score + recency_score + company_score + engagement_score
        
        logger.debug(
            f"Article score: {total:.1f} | "
            f"Source: {source_score} | Keywords: {keyword_score} | "
            f"Recency: {recency_score} | Companies: {company_score} | "
            f"Engagement: {engagement_score} | Title: {title[:50]}..."
        )
        
        return min(total, 100)  # Cap at 100
    
    @staticmethod
    def rank_articles(articles: list) -> list:
        """
        Rank articles by score (highest first).
        
        Args:
            articles: List of article data dictionaries
        
        Returns:
            List of articles sorted by score (descending)
        """
        # Score each article
        scored_articles = []
        for article in articles:
            score = ArticleScorer.score_article(article)
            article['score'] = score
            scored_articles.append(article)
        
        # Sort by score (highest first)
        ranked = sorted(scored_articles, key=lambda x: x['score'], reverse=True)
        
        logger.info(
            f"Ranked {len(ranked)} articles. "
            f"Top score: {ranked[0]['score']:.1f}, "
            f"Lowest: {ranked[-1]['score']:.1f}"
        )
        
        return ranked
    
    @staticmethod
    def select_top_n(articles: list, n: int = 5) -> list:
        """
        Select top N articles by score.
        
        Args:
            articles: List of article data dictionaries
            n: Number of articles to select
        
        Returns:
            Top N articles
        """
        ranked = ArticleScorer.rank_articles(articles)
        top_n = ranked[:n]
        
        logger.info(
            f"Selected top {len(top_n)} articles from {len(articles)} total. "
            f"Score range: {top_n[0]['score']:.1f} - {top_n[-1]['score']:.1f}"
        )
        
        return top_n
