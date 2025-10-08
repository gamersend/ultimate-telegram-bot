"""Image generation and processing service with local Stable Diffusion integration."""

import logging
import base64
import io
import tempfile
import os
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path

import httpx
from PIL import Image, ImageEnhance, ImageFilter
import requests

from bot.config import settings
from bot.services.ai import ai_service
from bot.utils.metrics import images_generated


logger = logging.getLogger(__name__)


class ImageProcessor:
    """Advanced image processing and generation."""
    
    def __init__(self):
        # AUTOMATIC1111 WebUI API endpoint (adjust as needed)
        self.sd_api_url = "http://192.168.0.150:7860"  # Default SD WebUI port
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.webp', '.bmp']
        
    async def check_sd_availability(self) -> bool:
        """Check if Stable Diffusion WebUI is available."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.sd_api_url}/sdapi/v1/options")
                return response.status_code == 200
        except Exception:
            return False
    
    async def generate_image_sd(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 512,
        height: int = 512,
        steps: int = 20,
        cfg_scale: float = 7.0,
        sampler: str = "DPM++ 2M Karras",
        model: Optional[str] = None
    ) -> Optional[bytes]:
        """Generate image using local Stable Diffusion."""
        try:
            images_generated.inc()
            
            payload = {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "width": width,
                "height": height,
                "steps": steps,
                "cfg_scale": cfg_scale,
                "sampler_name": sampler,
                "batch_size": 1,
                "n_iter": 1,
                "seed": -1,
                "restore_faces": True,
                "tiling": False,
                "do_not_save_samples": True,
                "do_not_save_grid": True
            }
            
            if model:
                # Set model if specified
                await self._set_sd_model(model)
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.sd_api_url}/sdapi/v1/txt2img",
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                if result.get("images"):
                    # Decode base64 image
                    image_data = base64.b64decode(result["images"][0])
                    return image_data
                
                return None
                
        except Exception as e:
            logger.error(f"Error generating image with SD: {e}")
            return None
    
    async def _set_sd_model(self, model_name: str) -> bool:
        """Set the active Stable Diffusion model."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.sd_api_url}/sdapi/v1/options",
                    json={"sd_model_checkpoint": model_name}
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Error setting SD model: {e}")
            return False
    
    async def get_sd_models(self) -> List[str]:
        """Get available Stable Diffusion models."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.sd_api_url}/sdapi/v1/sd-models")
                response.raise_for_status()
                
                models = response.json()
                return [model["title"] for model in models]
                
        except Exception as e:
            logger.error(f"Error getting SD models: {e}")
            return []
    
    async def img2img_sd(
        self,
        image_data: bytes,
        prompt: str,
        negative_prompt: str = "",
        denoising_strength: float = 0.7,
        steps: int = 20,
        cfg_scale: float = 7.0
    ) -> Optional[bytes]:
        """Image-to-image generation using Stable Diffusion."""
        try:
            # Convert image to base64
            image_b64 = base64.b64encode(image_data).decode()
            
            payload = {
                "init_images": [image_b64],
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "denoising_strength": denoising_strength,
                "steps": steps,
                "cfg_scale": cfg_scale,
                "width": 512,
                "height": 512,
                "restore_faces": True,
                "do_not_save_samples": True,
                "do_not_save_grid": True
            }
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.sd_api_url}/sdapi/v1/img2img",
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                if result.get("images"):
                    return base64.b64decode(result["images"][0])
                
                return None
                
        except Exception as e:
            logger.error(f"Error with img2img SD: {e}")
            return None
    
    async def upscale_image_sd(
        self,
        image_data: bytes,
        upscaler: str = "R-ESRGAN 4x+",
        upscaling_resize: float = 2.0
    ) -> Optional[bytes]:
        """Upscale image using Stable Diffusion extras."""
        try:
            image_b64 = base64.b64encode(image_data).decode()
            
            payload = {
                "image": image_b64,
                "upscaling_resize": upscaling_resize,
                "upscaler_1": upscaler,
                "extras_upscaler_2_visibility": 0
            }
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.sd_api_url}/sdapi/v1/extra-single-image",
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                if result.get("image"):
                    return base64.b64decode(result["image"])
                
                return None
                
        except Exception as e:
            logger.error(f"Error upscaling image: {e}")
            return None
    
    async def enhance_image(
        self,
        image_data: bytes,
        brightness: float = 1.0,
        contrast: float = 1.0,
        saturation: float = 1.0,
        sharpness: float = 1.0,
        apply_filters: List[str] = None
    ) -> Optional[bytes]:
        """Enhance image using PIL."""
        try:
            # Load image
            image = Image.open(io.BytesIO(image_data))
            
            # Apply enhancements
            if brightness != 1.0:
                enhancer = ImageEnhance.Brightness(image)
                image = enhancer.enhance(brightness)
            
            if contrast != 1.0:
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(contrast)
            
            if saturation != 1.0:
                enhancer = ImageEnhance.Color(image)
                image = enhancer.enhance(saturation)
            
            if sharpness != 1.0:
                enhancer = ImageEnhance.Sharpness(image)
                image = enhancer.enhance(sharpness)
            
            # Apply filters
            if apply_filters:
                for filter_name in apply_filters:
                    if filter_name == "blur":
                        image = image.filter(ImageFilter.BLUR)
                    elif filter_name == "sharpen":
                        image = image.filter(ImageFilter.SHARPEN)
                    elif filter_name == "smooth":
                        image = image.filter(ImageFilter.SMOOTH)
                    elif filter_name == "edge_enhance":
                        image = image.filter(ImageFilter.EDGE_ENHANCE)
            
            # Convert back to bytes
            output = io.BytesIO()
            image.save(output, format='PNG')
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Error enhancing image: {e}")
            return None
    
    async def resize_image(
        self,
        image_data: bytes,
        width: int,
        height: int,
        maintain_aspect: bool = True
    ) -> Optional[bytes]:
        """Resize image."""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            if maintain_aspect:
                image.thumbnail((width, height), Image.Resampling.LANCZOS)
            else:
                image = image.resize((width, height), Image.Resampling.LANCZOS)
            
            output = io.BytesIO()
            image.save(output, format='PNG')
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Error resizing image: {e}")
            return None
    
    async def get_image_info(self, image_data: bytes) -> Dict[str, Any]:
        """Get image information."""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            return {
                "width": image.width,
                "height": image.height,
                "format": image.format,
                "mode": image.mode,
                "size_mb": len(image_data) / (1024 * 1024),
                "has_transparency": image.mode in ("RGBA", "LA") or "transparency" in image.info
            }
            
        except Exception as e:
            logger.error(f"Error getting image info: {e}")
            return {}
    
    async def generate_image(
        self,
        prompt: str,
        use_local: bool = True,
        **kwargs
    ) -> Optional[bytes]:
        """Generate image with fallback between local and cloud."""
        try:
            # Try local Stable Diffusion first
            if use_local and await self.check_sd_availability():
                logger.info("Using local Stable Diffusion for image generation")
                result = await self.generate_image_sd(prompt, **kwargs)
                if result:
                    return result
                
                logger.warning("Local SD failed, trying cloud...")
            
            # Fallback to OpenAI DALL-E
            logger.info("Using OpenAI DALL-E for image generation")
            image_urls = await ai_service.generate_image(prompt)
            
            if image_urls:
                # Download the image
                async with httpx.AsyncClient() as client:
                    response = await client.get(image_urls[0])
                    response.raise_for_status()
                    return response.content
            
            return None
            
        except Exception as e:
            logger.error(f"Error in image generation: {e}")
            return None


# Global image processor instance
image_processor = ImageProcessor()
