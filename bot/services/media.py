"""Media control and download service."""

import logging
import asyncio
import os
import tempfile
from typing import Dict, Any, List, Optional
from pathlib import Path
import json

import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from bot.config import settings
from bot.services.n8n import n8n_service
from bot.utils.metrics import request_counter


logger = logging.getLogger(__name__)


class MediaService:
    """Service for media downloads and streaming control."""
    
    def __init__(self):
        self.download_dir = Path("media/downloads")
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # Spotify setup
        self.spotify = None
        if all([settings.spotify_client_id, settings.spotify_client_secret]):
            try:
                self.spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
                    client_id=settings.spotify_client_id,
                    client_secret=settings.spotify_client_secret,
                    redirect_uri=settings.spotify_redirect_uri,
                    scope="user-read-playback-state,user-modify-playback-state,playlist-read-private,playlist-modify-private"
                ))
            except Exception as e:
                logger.error(f"Error initializing Spotify: {e}")
    
    async def download_youtube_video(
        self,
        url: str,
        format_type: str = "best",
        audio_only: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Download YouTube video or audio."""
        try:
            request_counter.inc()
            
            # Configure yt-dlp options
            ydl_opts = {
                'outtmpl': str(self.download_dir / '%(title)s.%(ext)s'),
                'restrictfilenames': True,
                'noplaylist': True,
                'extract_flat': False,
            }
            
            if audio_only:
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }]
                })
            else:
                # Video download options
                if format_type == "best":
                    ydl_opts['format'] = 'best[height<=720]'
                elif format_type == "worst":
                    ydl_opts['format'] = 'worst'
                else:
                    ydl_opts['format'] = format_type
            
            # Run download in thread pool
            loop = asyncio.get_event_loop()
            
            def download_video():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # First, extract info
                    info = ydl.extract_info(url, download=False)
                    
                    # Check file size (limit to 50MB for Telegram)
                    filesize = info.get('filesize') or info.get('filesize_approx', 0)
                    if filesize > 50 * 1024 * 1024:  # 50MB
                        raise Exception("File too large for Telegram (>50MB)")
                    
                    # Download the video
                    ydl.download([url])
                    
                    return {
                        "title": info.get("title", "Unknown"),
                        "duration": info.get("duration", 0),
                        "uploader": info.get("uploader", "Unknown"),
                        "view_count": info.get("view_count", 0),
                        "upload_date": info.get("upload_date", ""),
                        "description": info.get("description", "")[:500],  # Limit description
                        "thumbnail": info.get("thumbnail"),
                        "filesize": filesize,
                        "format": info.get("format", ""),
                        "ext": info.get("ext", "mp4")
                    }
            
            result = await loop.run_in_executor(None, download_video)
            
            # Find the downloaded file
            title = result["title"]
            ext = result["ext"]
            
            # Clean filename for search
            import re
            clean_title = re.sub(r'[^\w\s-]', '', title).strip()
            
            # Look for the file
            downloaded_file = None
            for file_path in self.download_dir.glob(f"*{clean_title[:20]}*"):
                if file_path.is_file():
                    downloaded_file = file_path
                    break
            
            if not downloaded_file:
                # Fallback: get the most recent file
                files = list(self.download_dir.glob("*"))
                if files:
                    downloaded_file = max(files, key=os.path.getctime)
            
            if downloaded_file:
                result["file_path"] = str(downloaded_file)
                result["file_size"] = downloaded_file.stat().st_size
            
            return result
            
        except Exception as e:
            logger.error(f"Error downloading YouTube video: {e}")
            return None
    
    async def get_youtube_info(self, url: str) -> Optional[Dict[str, Any]]:
        """Get YouTube video information without downloading."""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            loop = asyncio.get_event_loop()
            
            def extract_info():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    return ydl.extract_info(url, download=False)
            
            info = await loop.run_in_executor(None, extract_info)
            
            return {
                "title": info.get("title", "Unknown"),
                "duration": info.get("duration", 0),
                "uploader": info.get("uploader", "Unknown"),
                "view_count": info.get("view_count", 0),
                "upload_date": info.get("upload_date", ""),
                "description": info.get("description", "")[:500],
                "thumbnail": info.get("thumbnail"),
                "filesize": info.get("filesize") or info.get("filesize_approx", 0),
                "formats": len(info.get("formats", [])),
                "url": url
            }
            
        except Exception as e:
            logger.error(f"Error getting YouTube info: {e}")
            return None
    
    async def search_youtube(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search YouTube videos."""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'default_search': 'ytsearch',
            }
            
            search_query = f"ytsearch{max_results}:{query}"
            
            loop = asyncio.get_event_loop()
            
            def search_videos():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    return ydl.extract_info(search_query, download=False)
            
            results = await loop.run_in_executor(None, search_videos)
            
            videos = []
            for entry in results.get("entries", []):
                videos.append({
                    "title": entry.get("title", "Unknown"),
                    "url": f"https://youtube.com/watch?v={entry.get('id')}",
                    "duration": entry.get("duration", 0),
                    "uploader": entry.get("uploader", "Unknown"),
                    "view_count": entry.get("view_count", 0),
                    "thumbnail": entry.get("thumbnail")
                })
            
            return videos
            
        except Exception as e:
            logger.error(f"Error searching YouTube: {e}")
            return []
    
    async def get_spotify_current_track(self) -> Optional[Dict[str, Any]]:
        """Get currently playing track on Spotify."""
        if not self.spotify:
            return None
        
        try:
            current = self.spotify.current_playback()
            
            if not current or not current.get("item"):
                return None
            
            track = current["item"]
            
            return {
                "name": track.get("name", "Unknown"),
                "artists": [artist["name"] for artist in track.get("artists", [])],
                "album": track.get("album", {}).get("name", "Unknown"),
                "duration_ms": track.get("duration_ms", 0),
                "progress_ms": current.get("progress_ms", 0),
                "is_playing": current.get("is_playing", False),
                "device": current.get("device", {}).get("name", "Unknown"),
                "volume": current.get("device", {}).get("volume_percent", 0),
                "external_urls": track.get("external_urls", {}),
                "preview_url": track.get("preview_url"),
                "popularity": track.get("popularity", 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting Spotify current track: {e}")
            return None
    
    async def spotify_control(self, action: str, **kwargs) -> bool:
        """Control Spotify playback."""
        if not self.spotify:
            return False
        
        try:
            if action == "play":
                self.spotify.start_playback(**kwargs)
            elif action == "pause":
                self.spotify.pause_playback()
            elif action == "next":
                self.spotify.next_track()
            elif action == "previous":
                self.spotify.previous_track()
            elif action == "volume":
                volume = kwargs.get("volume", 50)
                self.spotify.volume(volume)
            elif action == "shuffle":
                state = kwargs.get("state", True)
                self.spotify.shuffle(state)
            elif action == "repeat":
                state = kwargs.get("state", "context")  # track, context, off
                self.spotify.repeat(state)
            else:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error controlling Spotify: {e}")
            return False
    
    async def search_spotify(self, query: str, search_type: str = "track", limit: int = 10) -> List[Dict[str, Any]]:
        """Search Spotify for tracks, albums, artists, or playlists."""
        if not self.spotify:
            return []
        
        try:
            results = self.spotify.search(query, type=search_type, limit=limit)
            
            items = []
            
            if search_type == "track":
                for track in results.get("tracks", {}).get("items", []):
                    items.append({
                        "name": track.get("name", "Unknown"),
                        "artists": [artist["name"] for artist in track.get("artists", [])],
                        "album": track.get("album", {}).get("name", "Unknown"),
                        "duration_ms": track.get("duration_ms", 0),
                        "popularity": track.get("popularity", 0),
                        "external_urls": track.get("external_urls", {}),
                        "preview_url": track.get("preview_url"),
                        "uri": track.get("uri")
                    })
            
            elif search_type == "artist":
                for artist in results.get("artists", {}).get("items", []):
                    items.append({
                        "name": artist.get("name", "Unknown"),
                        "genres": artist.get("genres", []),
                        "popularity": artist.get("popularity", 0),
                        "followers": artist.get("followers", {}).get("total", 0),
                        "external_urls": artist.get("external_urls", {}),
                        "uri": artist.get("uri")
                    })
            
            elif search_type == "album":
                for album in results.get("albums", {}).get("items", []):
                    items.append({
                        "name": album.get("name", "Unknown"),
                        "artists": [artist["name"] for artist in album.get("artists", [])],
                        "release_date": album.get("release_date", "Unknown"),
                        "total_tracks": album.get("total_tracks", 0),
                        "external_urls": album.get("external_urls", {}),
                        "uri": album.get("uri")
                    })
            
            return items
            
        except Exception as e:
            logger.error(f"Error searching Spotify: {e}")
            return []
    
    async def get_user_playlists(self) -> List[Dict[str, Any]]:
        """Get user's Spotify playlists."""
        if not self.spotify:
            return []
        
        try:
            playlists = self.spotify.current_user_playlists()
            
            items = []
            for playlist in playlists.get("items", []):
                items.append({
                    "name": playlist.get("name", "Unknown"),
                    "description": playlist.get("description", ""),
                    "tracks_total": playlist.get("tracks", {}).get("total", 0),
                    "public": playlist.get("public", False),
                    "collaborative": playlist.get("collaborative", False),
                    "external_urls": playlist.get("external_urls", {}),
                    "uri": playlist.get("uri"),
                    "id": playlist.get("id")
                })
            
            return items
            
        except Exception as e:
            logger.error(f"Error getting user playlists: {e}")
            return []
    
    async def cleanup_downloads(self, max_age_hours: int = 24) -> int:
        """Clean up old downloaded files."""
        try:
            import time
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            deleted_count = 0
            
            for file_path in self.download_dir.glob("*"):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        deleted_count += 1
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up downloads: {e}")
            return 0


# Global media service instance
media_service = MediaService()
