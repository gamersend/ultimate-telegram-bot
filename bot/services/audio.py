"""Enhanced audio processing service with FFmpeg integration."""

import logging
import os
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import asyncio

from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range
import whisper

from bot.config import settings
from bot.services.ai import ai_service
from bot.utils.metrics import voice_messages


logger = logging.getLogger(__name__)


class AudioProcessor:
    """Advanced audio processing with FFmpeg and pydub."""
    
    def __init__(self):
        self.whisper_model = None
        self.supported_formats = {
            'input': ['.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac', '.wma'],
            'output': ['.mp3', '.wav', '.ogg', '.m4a']
        }
    
    async def load_whisper_model(self, model_size: str = "base") -> bool:
        """Load Whisper model for transcription."""
        try:
            if self.whisper_model is None:
                logger.info(f"Loading Whisper model: {model_size}")
                self.whisper_model = whisper.load_model(model_size)
            return True
        except Exception as e:
            logger.error(f"Error loading Whisper model: {e}")
            return False
    
    async def convert_audio_format(
        self,
        input_path: str,
        output_format: str = "wav",
        sample_rate: int = 16000,
        channels: int = 1
    ) -> Optional[str]:
        """Convert audio to specified format using FFmpeg."""
        try:
            output_path = input_path.rsplit('.', 1)[0] + f'.{output_format}'
            
            cmd = [
                'ffmpeg', '-i', input_path,
                '-ar', str(sample_rate),
                '-ac', str(channels),
                '-y',  # Overwrite output file
                output_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"Audio converted successfully: {output_path}")
                return output_path
            else:
                logger.error(f"FFmpeg error: {stderr.decode()}")
                return None
                
        except Exception as e:
            logger.error(f"Error converting audio format: {e}")
            return None
    
    async def enhance_audio_quality(self, input_path: str) -> Optional[str]:
        """Enhance audio quality using pydub effects."""
        try:
            # Load audio
            audio = AudioSegment.from_file(input_path)
            
            # Apply enhancements
            # Normalize volume
            audio = normalize(audio)
            
            # Apply dynamic range compression
            audio = compress_dynamic_range(audio)
            
            # Remove silence from beginning and end
            audio = audio.strip_silence(silence_thresh=-40)
            
            # Export enhanced audio
            output_path = input_path.rsplit('.', 1)[0] + '_enhanced.wav'
            audio.export(output_path, format="wav")
            
            logger.info(f"Audio enhanced successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error enhancing audio quality: {e}")
            return None
    
    async def extract_audio_info(self, file_path: str) -> Dict[str, Any]:
        """Extract audio file information."""
        try:
            audio = AudioSegment.from_file(file_path)
            
            return {
                "duration": len(audio) / 1000.0,  # Convert to seconds
                "channels": audio.channels,
                "sample_rate": audio.frame_rate,
                "sample_width": audio.sample_width,
                "format": Path(file_path).suffix.lower(),
                "size_mb": os.path.getsize(file_path) / (1024 * 1024)
            }
            
        except Exception as e:
            logger.error(f"Error extracting audio info: {e}")
            return {}
    
    async def trim_audio(
        self,
        input_path: str,
        start_time: float,
        end_time: Optional[float] = None
    ) -> Optional[str]:
        """Trim audio to specified time range."""
        try:
            audio = AudioSegment.from_file(input_path)
            
            start_ms = int(start_time * 1000)
            end_ms = int(end_time * 1000) if end_time else len(audio)
            
            trimmed_audio = audio[start_ms:end_ms]
            
            output_path = input_path.rsplit('.', 1)[0] + '_trimmed.wav'
            trimmed_audio.export(output_path, format="wav")
            
            logger.info(f"Audio trimmed successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error trimming audio: {e}")
            return None
    
    async def merge_audio_files(self, file_paths: list, output_path: str) -> bool:
        """Merge multiple audio files."""
        try:
            combined = AudioSegment.empty()
            
            for file_path in file_paths:
                audio = AudioSegment.from_file(file_path)
                combined += audio
            
            combined.export(output_path, format="wav")
            logger.info(f"Audio files merged successfully: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error merging audio files: {e}")
            return False
    
    async def add_audio_effects(
        self,
        input_path: str,
        effects: Dict[str, Any]
    ) -> Optional[str]:
        """Apply audio effects using FFmpeg."""
        try:
            output_path = input_path.rsplit('.', 1)[0] + '_effects.wav'
            
            # Build FFmpeg command with effects
            cmd = ['ffmpeg', '-i', input_path]
            
            # Audio filters
            filters = []
            
            if effects.get('speed', 1.0) != 1.0:
                filters.append(f"atempo={effects['speed']}")
            
            if effects.get('pitch', 1.0) != 1.0:
                filters.append(f"asetrate=44100*{effects['pitch']},aresample=44100")
            
            if effects.get('volume', 1.0) != 1.0:
                filters.append(f"volume={effects['volume']}")
            
            if effects.get('echo', False):
                filters.append("aecho=0.8:0.9:1000:0.3")
            
            if effects.get('reverb', False):
                filters.append("afreqshift=0.5")
            
            if filters:
                cmd.extend(['-af', ','.join(filters)])
            
            cmd.extend(['-y', output_path])
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"Audio effects applied successfully: {output_path}")
                return output_path
            else:
                logger.error(f"FFmpeg effects error: {stderr.decode()}")
                return None
                
        except Exception as e:
            logger.error(f"Error applying audio effects: {e}")
            return None
    
    async def transcribe_audio_local(self, file_path: str) -> Optional[str]:
        """Transcribe audio using local Whisper model."""
        try:
            if not await self.load_whisper_model():
                return None
            
            # Convert to WAV if needed
            if not file_path.endswith('.wav'):
                converted_path = await self.convert_audio_format(file_path, 'wav')
                if not converted_path:
                    return None
                file_path = converted_path
            
            # Transcribe
            result = self.whisper_model.transcribe(file_path)
            return result["text"].strip()
            
        except Exception as e:
            logger.error(f"Error transcribing audio locally: {e}")
            return None
    
    async def transcribe_audio_cloud(self, file_path: str) -> Optional[str]:
        """Transcribe audio using OpenAI Whisper API."""
        try:
            return await ai_service.transcribe_audio(file_path)
        except Exception as e:
            logger.error(f"Error transcribing audio via cloud: {e}")
            return None
    
    async def transcribe_audio(
        self,
        file_path: str,
        use_local: bool = True,
        enhance_quality: bool = True
    ) -> Optional[str]:
        """Transcribe audio with optional quality enhancement."""
        try:
            voice_messages.inc()
            
            # Enhance audio quality if requested
            if enhance_quality:
                enhanced_path = await self.enhance_audio_quality(file_path)
                if enhanced_path:
                    file_path = enhanced_path
            
            # Try local transcription first, fallback to cloud
            if use_local:
                transcription = await self.transcribe_audio_local(file_path)
                if transcription:
                    return transcription
                
                logger.warning("Local transcription failed, trying cloud...")
            
            return await self.transcribe_audio_cloud(file_path)
            
        except Exception as e:
            logger.error(f"Error in audio transcription: {e}")
            return None
    
    async def generate_speech(
        self,
        text: str,
        voice: str = "alloy",
        speed: float = 1.0,
        output_format: str = "mp3"
    ) -> Optional[bytes]:
        """Generate speech from text with options."""
        try:
            # Generate base audio
            audio_content = await ai_service.text_to_speech(text, voice)
            
            if speed != 1.0 and audio_content:
                # Apply speed adjustment
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                    temp_file.write(audio_content)
                    temp_path = temp_file.name
                
                try:
                    effects = {"speed": speed}
                    processed_path = await self.add_audio_effects(temp_path, effects)
                    
                    if processed_path:
                        with open(processed_path, "rb") as f:
                            audio_content = f.read()
                        os.unlink(processed_path)
                    
                finally:
                    os.unlink(temp_path)
            
            return audio_content
            
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            return None


# Global audio processor instance
audio_processor = AudioProcessor()
