"""News and information feed service."""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import hashlib

import feedparser
import httpx
from bs4 import BeautifulSoup

from bot.config import settings
from bot.services.ai import ai_service
from bot.services.n8n import n8n_service
from bot.utils.metrics import request_counter


logger = logging.getLogger(__name__)


class NewsService:
    """Service for news and RSS feed management."""
    
    def __init__(self):
        self.news_api_key = settings.news_api_key
        self.feeds_cache = {}
        self.cache_expiry = {}
        
        # Default RSS feeds
        self.default_feeds = {
            "tech": [
                "https://feeds.feedburner.com/TechCrunch",
                "https://www.theverge.com/rss/index.xml",
                "https://feeds.arstechnica.com/arstechnica/index",
                "https://rss.cnn.com/rss/edition.rss"
            ],
            "news": [
                "https://feeds.bbci.co.uk/news/rss.xml",
                "https://rss.cnn.com/rss/edition.rss",
                "https://feeds.reuters.com/reuters/topNews",
                "https://feeds.npr.org/1001/rss.xml"
            ],
            "science": [
                "https://feeds.feedburner.com/oreilly/radar",
                "https://www.nature.com/nature.rss",
                "https://feeds.feedburner.com/sciencedaily",
                "https://www.sciencemag.org/rss/news_current.xml"
            ],
            "business": [
                "https://feeds.bloomberg.com/markets/news.rss",
                "https://feeds.reuters.com/reuters/businessNews",
                "https://feeds.feedburner.com/entrepreneur/latest",
                "https://feeds.fortune.com/fortune/headlines"
            ]
        }
    
    def _is_cache_valid(self, key: str, ttl_minutes: int = 30) -> bool:
        """Check if cached data is still valid."""
        if key not in self.cache_expiry:
            return False
        
        expiry_time = self.cache_expiry[key]
        return datetime.now() < expiry_time
    
    def _set_cache(self, key: str, data: Any, ttl_minutes: int = 30) -> None:
        """Set cached data with expiry."""
        self.feeds_cache[key] = data
        self.cache_expiry[key] = datetime.now() + timedelta(minutes=ttl_minutes)
    
    async def parse_rss_feed(self, feed_url: str, max_items: int = 10) -> List[Dict[str, Any]]:
        """Parse RSS feed and return articles."""
        try:
            request_counter.inc()
            
            cache_key = f"rss_{hashlib.md5(feed_url.encode()).hexdigest()}"
            if self._is_cache_valid(cache_key):
                return self.feeds_cache[cache_key]
            
            # Run feedparser in thread pool since it's synchronous
            loop = asyncio.get_event_loop()
            feed = await loop.run_in_executor(None, feedparser.parse, feed_url)
            
            if feed.bozo:
                logger.warning(f"RSS feed parsing warning for {feed_url}: {feed.bozo_exception}")
            
            articles = []
            for entry in feed.entries[:max_items]:
                # Extract article data
                article = {
                    "title": entry.get("title", "No Title"),
                    "link": entry.get("link", ""),
                    "description": self._clean_html(entry.get("description", "")),
                    "summary": self._clean_html(entry.get("summary", "")),
                    "published": self._parse_date(entry.get("published", "")),
                    "author": entry.get("author", "Unknown"),
                    "source": feed.feed.get("title", "RSS Feed"),
                    "source_url": feed_url,
                    "tags": [tag.term for tag in entry.get("tags", [])],
                    "guid": entry.get("guid", entry.get("link", ""))
                }
                
                # Use description or summary
                if not article["description"] and article["summary"]:
                    article["description"] = article["summary"]
                
                articles.append(article)
            
            self._set_cache(cache_key, articles)
            return articles
            
        except Exception as e:
            logger.error(f"Error parsing RSS feed {feed_url}: {e}")
            return []
    
    def _clean_html(self, html_content: str) -> str:
        """Clean HTML content and extract text."""
        if not html_content:
            return ""
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            text = soup.get_text(strip=True)
            # Limit length
            return text[:500] + "..." if len(text) > 500 else text
        except Exception:
            return html_content[:500] + "..." if len(html_content) > 500 else html_content
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string to ISO format."""
        if not date_str:
            return None
        
        try:
            # feedparser usually handles this well
            import time
            parsed_time = feedparser._parse_date(date_str)
            if parsed_time:
                return datetime(*parsed_time[:6]).isoformat()
        except Exception:
            pass
        
        return date_str
    
    async def get_news_by_category(self, category: str, max_items: int = 5) -> List[Dict[str, Any]]:
        """Get news articles by category."""
        try:
            if category not in self.default_feeds:
                return []
            
            all_articles = []
            feeds = self.default_feeds[category]
            
            # Parse multiple feeds concurrently
            tasks = [self.parse_rss_feed(feed_url, max_items) for feed_url in feeds]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, list):
                    all_articles.extend(result)
            
            # Sort by published date (newest first)
            all_articles.sort(key=lambda x: x.get("published", ""), reverse=True)
            
            return all_articles[:max_items]
            
        except Exception as e:
            logger.error(f"Error getting news by category {category}: {e}")
            return []
    
    async def search_news_api(self, query: str, max_items: int = 10) -> List[Dict[str, Any]]:
        """Search news using News API."""
        if not self.news_api_key:
            return []
        
        try:
            request_counter.inc()
            
            cache_key = f"news_api_{hashlib.md5(query.encode()).hexdigest()}"
            if self._is_cache_valid(cache_key, 15):  # 15 minute cache
                return self.feeds_cache[cache_key]
            
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": query,
                "apiKey": self.news_api_key,
                "pageSize": max_items,
                "sortBy": "publishedAt",
                "language": "en"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                articles = []
                
                for article in data.get("articles", []):
                    articles.append({
                        "title": article.get("title", "No Title"),
                        "link": article.get("url", ""),
                        "description": article.get("description", ""),
                        "summary": article.get("content", "")[:200] + "..." if article.get("content") else "",
                        "published": article.get("publishedAt", ""),
                        "author": article.get("author", "Unknown"),
                        "source": article.get("source", {}).get("name", "News API"),
                        "source_url": article.get("url", ""),
                        "image_url": article.get("urlToImage"),
                        "guid": article.get("url", "")
                    })
                
                self._set_cache(cache_key, articles)
                return articles
                
        except Exception as e:
            logger.error(f"Error searching news API: {e}")
            return []
    
    async def get_trending_topics(self) -> List[str]:
        """Get trending topics from various sources."""
        try:
            # This is a simplified implementation
            # In a real scenario, you'd aggregate from multiple sources
            
            trending = [
                "artificial intelligence",
                "climate change",
                "cryptocurrency",
                "space exploration",
                "renewable energy",
                "cybersecurity",
                "quantum computing",
                "biotechnology",
                "electric vehicles",
                "machine learning"
            ]
            
            return trending[:10]
            
        except Exception as e:
            logger.error(f"Error getting trending topics: {e}")
            return []
    
    async def summarize_article(self, article_url: str) -> Optional[Dict[str, Any]]:
        """Fetch and summarize a full article."""
        try:
            # Fetch article content
            async with httpx.AsyncClient() as client:
                response = await client.get(article_url, timeout=10.0)
                response.raise_for_status()
                
                # Parse HTML content
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Extract title
                title = soup.find('title')
                title_text = title.get_text() if title else "Unknown Title"
                
                # Extract main content (this is simplified)
                # In practice, you'd use more sophisticated content extraction
                paragraphs = soup.find_all('p')
                content = ' '.join([p.get_text() for p in paragraphs])
                
                # Limit content length for AI processing
                if len(content) > 4000:
                    content = content[:4000] + "..."
                
                # Generate AI summary
                summary_prompt = f"Please provide a concise summary of this article:\n\nTitle: {title_text}\n\nContent: {content}"
                summary = await ai_service.chat_completion(summary_prompt)
                
                return {
                    "title": title_text,
                    "url": article_url,
                    "content": content[:1000] + "..." if len(content) > 1000 else content,
                    "summary": summary,
                    "word_count": len(content.split()),
                    "reading_time": max(1, len(content.split()) // 200)  # Assume 200 WPM
                }
                
        except Exception as e:
            logger.error(f"Error summarizing article {article_url}: {e}")
            return None
    
    async def create_news_digest(self, categories: List[str], max_per_category: int = 3) -> str:
        """Create a comprehensive news digest."""
        try:
            digest = f"📰 **Daily News Digest - {datetime.now().strftime('%B %d, %Y')}**\n\n"
            
            for category in categories:
                articles = await self.get_news_by_category(category, max_per_category)
                
                if articles:
                    digest += f"## 📂 {category.title()}\n\n"
                    
                    for i, article in enumerate(articles, 1):
                        title = article.get("title", "No Title")
                        source = article.get("source", "Unknown")
                        link = article.get("link", "")
                        description = article.get("description", "")[:150]
                        
                        digest += f"{i}. **{title}**\n"
                        digest += f"   *{source}*\n"
                        if description:
                            digest += f"   {description}...\n"
                        if link:
                            digest += f"   🔗 [Read more]({link})\n"
                        digest += "\n"
                    
                    digest += "---\n\n"
            
            # Add trending topics
            trending = await self.get_trending_topics()
            if trending:
                digest += "## 🔥 Trending Topics\n\n"
                for topic in trending[:5]:
                    digest += f"• {topic}\n"
                digest += "\n"
            
            return digest
            
        except Exception as e:
            logger.error(f"Error creating news digest: {e}")
            return "❌ Error creating news digest."
    
    async def add_custom_feed(self, user_id: int, feed_url: str, category: str = "custom") -> bool:
        """Add a custom RSS feed for a user."""
        try:
            # Test the feed first
            articles = await self.parse_rss_feed(feed_url, 1)
            if not articles:
                return False
            
            # Store in n8n workflow for persistence
            feed_data = {
                "user_id": user_id,
                "feed_url": feed_url,
                "category": category,
                "added_at": datetime.now().isoformat(),
                "active": True
            }
            
            result = await n8n_service.trigger_n8n_workflow("custom_feed", feed_data)
            return result is not None
            
        except Exception as e:
            logger.error(f"Error adding custom feed: {e}")
            return False
    
    async def get_feed_categories(self) -> List[str]:
        """Get available feed categories."""
        return list(self.default_feeds.keys())


# Global news service instance
news_service = NewsService()
