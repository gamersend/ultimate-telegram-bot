"""Fun features service - memes, GIFs, trivia, and entertainment."""

import logging
import asyncio
import random
from typing import Dict, Any, List, Optional
import json

import httpx

from bot.config import settings
from bot.services.ai import ai_service
from bot.utils.metrics import request_counter


logger = logging.getLogger(__name__)


class FunService:
    """Service for entertainment and fun features."""
    
    def __init__(self):
        self.giphy_api_key = settings.giphy_api_key
        self.meme_cache = {}
        
        # Trivia questions database
        self.trivia_categories = {
            "general": 9,
            "science": 17,
            "history": 23,
            "geography": 22,
            "sports": 21,
            "entertainment": 11,
            "technology": 18,
            "animals": 27
        }
        
        # Fun facts database
        self.fun_facts = [
            "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly edible.",
            "A group of flamingos is called a 'flamboyance'.",
            "Bananas are berries, but strawberries aren't.",
            "The shortest war in history lasted only 38-45 minutes between Britain and Zanzibar in 1896.",
            "Octopuses have three hearts and blue blood.",
            "A shrimp's heart is in its head.",
            "It's impossible to hum while holding your nose.",
            "The human brain uses about 20% of the body's total energy.",
            "There are more possible games of chess than atoms in the observable universe.",
            "Dolphins have names for each other.",
            "A day on Venus is longer than its year.",
            "Wombat poop is cube-shaped.",
            "The Great Wall of China isn't visible from space with the naked eye.",
            "Cleopatra lived closer in time to the Moon landing than to the construction of the Great Pyramid.",
            "There are more trees on Earth than stars in the Milky Way galaxy."
        ]
        
        # Jokes database
        self.jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "Why don't eggs tell jokes? They'd crack each other up!",
            "What do you call a fake noodle? An impasta!",
            "Why did the math book look so sad? Because it had too many problems!",
            "What do you call a bear with no teeth? A gummy bear!",
            "Why don't skeletons fight each other? They don't have the guts!",
            "What do you call a sleeping bull? A bulldozer!",
            "Why did the coffee file a police report? It got mugged!",
            "What do you call a fish wearing a bowtie? Sofishticated!"
        ]
    
    async def get_random_meme(self) -> Optional[Dict[str, Any]]:
        """Get a random meme from Reddit."""
        try:
            request_counter.inc()
            
            # Use Reddit API to get memes
            subreddits = ["memes", "dankmemes", "wholesomememes", "programmerhumor"]
            subreddit = random.choice(subreddits)
            
            url = f"https://www.reddit.com/r/{subreddit}/hot.json"
            headers = {"User-Agent": "TelegramBot/1.0"}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                posts = data.get("data", {}).get("children", [])
                
                # Filter for image posts
                image_posts = []
                for post in posts:
                    post_data = post.get("data", {})
                    url = post_data.get("url", "")
                    
                    if any(url.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif"]):
                        image_posts.append({
                            "title": post_data.get("title", "Meme"),
                            "url": url,
                            "subreddit": post_data.get("subreddit", subreddit),
                            "score": post_data.get("score", 0),
                            "author": post_data.get("author", "unknown"),
                            "permalink": f"https://reddit.com{post_data.get('permalink', '')}"
                        })
                
                if image_posts:
                    return random.choice(image_posts)
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting random meme: {e}")
            return None
    
    async def search_gif(self, query: str) -> Optional[Dict[str, Any]]:
        """Search for GIFs using Giphy API."""
        if not self.giphy_api_key:
            return None
        
        try:
            request_counter.inc()
            
            url = "https://api.giphy.com/v1/gifs/search"
            params = {
                "api_key": self.giphy_api_key,
                "q": query,
                "limit": 10,
                "rating": "pg-13"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                gifs = data.get("data", [])
                
                if gifs:
                    gif = random.choice(gifs)
                    return {
                        "title": gif.get("title", "GIF"),
                        "url": gif.get("images", {}).get("original", {}).get("url", ""),
                        "preview_url": gif.get("images", {}).get("fixed_height", {}).get("url", ""),
                        "source": "Giphy",
                        "rating": gif.get("rating", ""),
                        "trending_datetime": gif.get("trending_datetime", "")
                    }
                
                return None
                
        except Exception as e:
            logger.error(f"Error searching GIF: {e}")
            return None
    
    async def get_trending_gifs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending GIFs from Giphy."""
        if not self.giphy_api_key:
            return []
        
        try:
            request_counter.inc()
            
            url = "https://api.giphy.com/v1/gifs/trending"
            params = {
                "api_key": self.giphy_api_key,
                "limit": limit,
                "rating": "pg-13"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                gifs = data.get("data", [])
                
                trending_gifs = []
                for gif in gifs:
                    trending_gifs.append({
                        "title": gif.get("title", "Trending GIF"),
                        "url": gif.get("images", {}).get("original", {}).get("url", ""),
                        "preview_url": gif.get("images", {}).get("fixed_height", {}).get("url", ""),
                        "source": "Giphy",
                        "rating": gif.get("rating", "")
                    })
                
                return trending_gifs
                
        except Exception as e:
            logger.error(f"Error getting trending GIFs: {e}")
            return []
    
    async def get_trivia_question(self, category: str = "general", difficulty: str = "medium") -> Optional[Dict[str, Any]]:
        """Get a trivia question from Open Trivia Database."""
        try:
            request_counter.inc()
            
            category_id = self.trivia_categories.get(category, 9)
            
            url = "https://opentdb.com/api.php"
            params = {
                "amount": 1,
                "category": category_id,
                "difficulty": difficulty,
                "type": "multiple"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                results = data.get("results", [])
                
                if results:
                    question_data = results[0]
                    
                    # Decode HTML entities
                    import html
                    question = html.unescape(question_data.get("question", ""))
                    correct_answer = html.unescape(question_data.get("correct_answer", ""))
                    incorrect_answers = [html.unescape(ans) for ans in question_data.get("incorrect_answers", [])]
                    
                    # Shuffle answers
                    all_answers = [correct_answer] + incorrect_answers
                    random.shuffle(all_answers)
                    
                    return {
                        "question": question,
                        "correct_answer": correct_answer,
                        "all_answers": all_answers,
                        "category": question_data.get("category", category),
                        "difficulty": question_data.get("difficulty", difficulty),
                        "correct_index": all_answers.index(correct_answer)
                    }
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting trivia question: {e}")
            return None
    
    async def get_random_joke(self) -> str:
        """Get a random joke."""
        return random.choice(self.jokes)
    
    async def get_dad_joke(self) -> Optional[str]:
        """Get a dad joke from icanhazdadjoke API."""
        try:
            request_counter.inc()
            
            url = "https://icanhazdadjoke.com/"
            headers = {
                "Accept": "application/json",
                "User-Agent": "TelegramBot/1.0"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                return data.get("joke", "")
                
        except Exception as e:
            logger.error(f"Error getting dad joke: {e}")
            return None
    
    async def get_fun_fact(self) -> str:
        """Get a random fun fact."""
        return random.choice(self.fun_facts)
    
    async def generate_ai_joke(self, topic: str = "") -> Optional[str]:
        """Generate a joke using AI."""
        try:
            if topic:
                prompt = f"Tell me a clean, funny joke about {topic}. Just the joke, no explanation."
            else:
                prompt = "Tell me a clean, funny joke. Just the joke, no explanation."
            
            joke = await ai_service.chat_completion(prompt)
            return joke
            
        except Exception as e:
            logger.error(f"Error generating AI joke: {e}")
            return None
    
    async def create_meme_text(self, image_description: str) -> Optional[str]:
        """Generate meme text for an image using AI."""
        try:
            prompt = f"Create funny meme text for an image that shows: {image_description}. Return only the meme text, no explanation. Make it witty and internet-culture appropriate."
            
            meme_text = await ai_service.chat_completion(prompt)
            return meme_text
            
        except Exception as e:
            logger.error(f"Error creating meme text: {e}")
            return None
    
    async def get_would_you_rather(self) -> Optional[Dict[str, Any]]:
        """Generate a 'Would You Rather' question using AI."""
        try:
            prompt = "Create an interesting 'Would You Rather' question with two choices. Format it as: 'Would you rather [option A] or [option B]?' Make it thought-provoking but appropriate."
            
            question = await ai_service.chat_completion(prompt)
            
            if question and "would you rather" in question.lower():
                return {
                    "question": question,
                    "type": "would_you_rather"
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating would you rather: {e}")
            return None
    
    async def get_this_or_that(self) -> Optional[Dict[str, Any]]:
        """Generate a 'This or That' question."""
        options = [
            ("Coffee", "Tea"),
            ("Pizza", "Burgers"),
            ("Movies", "Books"),
            ("Beach", "Mountains"),
            ("Summer", "Winter"),
            ("Cats", "Dogs"),
            ("Morning", "Night"),
            ("Sweet", "Salty"),
            ("iOS", "Android"),
            ("Netflix", "YouTube")
        ]
        
        option_a, option_b = random.choice(options)
        
        return {
            "question": f"This or That: {option_a} or {option_b}?",
            "option_a": option_a,
            "option_b": option_b,
            "type": "this_or_that"
        }
    
    def get_available_categories(self) -> List[str]:
        """Get available trivia categories."""
        return list(self.trivia_categories.keys())


# Global fun service instance
fun_service = FunService()
