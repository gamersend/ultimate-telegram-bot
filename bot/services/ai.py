"""AI service integration for OpenAI and Anthropic."""

import logging
import asyncio
from typing import List, Dict, Optional, AsyncGenerator
import openai
from anthropic import AsyncAnthropic

from bot.config import settings
from bot.utils.metrics import ai_requests, ai_tokens, ai_cost


logger = logging.getLogger(__name__)


class AIService:
    """AI service for handling OpenAI and Anthropic requests."""
    
    def __init__(self):
        # Configure OpenAI client with your local endpoint
        self.openai_client = openai.AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url
        )
        
        # Configure Anthropic client (if available)
        self.anthropic_client = None
        if settings.anthropic_api_key:
            self.anthropic_client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False,
        provider: str = "openai"
    ) -> str:
        """Get chat completion from AI provider."""
        
        try:
            if provider == "openai":
                return await self._openai_chat(messages, model, temperature, max_tokens, stream)
            elif provider == "anthropic" and self.anthropic_client:
                return await self._anthropic_chat(messages, model, temperature, max_tokens)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
                
        except Exception as e:
            logger.error(f"AI chat completion error: {e}")
            raise
    
    async def _openai_chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
        stream: bool
    ) -> str:
        """Handle OpenAI chat completion."""
        
        ai_requests.labels(provider="openai").inc()
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            
            if stream:
                # Handle streaming response
                content = ""
                async for chunk in response:
                    if chunk.choices[0].delta.content:
                        content += chunk.choices[0].delta.content
                return content
            else:
                # Handle regular response
                content = response.choices[0].message.content
                
                # Track metrics
                if hasattr(response, 'usage'):
                    ai_tokens.labels(provider="openai", type="prompt").inc(response.usage.prompt_tokens)
                    ai_tokens.labels(provider="openai", type="completion").inc(response.usage.completion_tokens)
                
                return content
                
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def _anthropic_chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Handle Anthropic chat completion."""
        
        ai_requests.labels(provider="anthropic").inc()
        
        try:
            # Convert messages format for Anthropic
            system_message = ""
            user_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    user_messages.append(msg)
            
            response = await self.anthropic_client.messages.create(
                model=model if model.startswith("claude") else "claude-3-sonnet-20240229",
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_message,
                messages=user_messages
            )
            
            # Track metrics
            ai_tokens.labels(provider="anthropic", type="prompt").inc(response.usage.input_tokens)
            ai_tokens.labels(provider="anthropic", type="completion").inc(response.usage.output_tokens)
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise
    
    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        n: int = 1
    ) -> List[str]:
        """Generate images using OpenAI DALL-E."""
        
        try:
            response = await self.openai_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality=quality,
                n=n
            )
            
            return [img.url for img in response.data]
            
        except Exception as e:
            logger.error(f"Image generation error: {e}")
            raise
    
    async def transcribe_audio(self, audio_file_path: str) -> str:
        """Transcribe audio using OpenAI Whisper."""
        
        try:
            with open(audio_file_path, "rb") as audio_file:
                response = await self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Audio transcription error: {e}")
            raise
    
    async def text_to_speech(self, text: str, voice: str = "alloy") -> bytes:
        """Convert text to speech using OpenAI TTS."""
        
        try:
            response = await self.openai_client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text
            )
            
            return response.content
            
        except Exception as e:
            logger.error(f"Text-to-speech error: {e}")
            raise
    
    async def analyze_image(self, image_url: str, prompt: str = "What's in this image?") -> str:
        """Analyze image using OpenAI Vision."""
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Image analysis error: {e}")
            raise


# Global AI service instance
ai_service = AIService()


async def get_ai_response(
    user_message: str,
    context: Optional[List[Dict[str, str]]] = None,
    system_prompt: Optional[str] = None,
    provider: str = "openai"
) -> str:
    """Get AI response with context."""
    
    messages = []
    
    # Add system prompt
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    else:
        messages.append({
            "role": "system",
            "content": "You are a helpful AI assistant integrated into a Telegram bot. "
                      "Provide concise, accurate, and helpful responses. Use emojis when appropriate."
        })
    
    # Add context if provided
    if context:
        messages.extend(context)
    
    # Add user message
    messages.append({"role": "user", "content": user_message})
    
    return await ai_service.chat_completion(messages, provider=provider)
