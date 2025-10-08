"""Media control and download handlers."""

import logging
import os
from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.enums import ChatAction

from bot.services.media import media_service
from bot.services.n8n import log_bot_activity
from bot.utils.decorators import authorized_only, log_command


logger = logging.getLogger(__name__)


@authorized_only
@log_command
async def download_command(message: Message):
    """Handle /download command for YouTube downloads."""

    args = message.text.replace("/download", "").strip()

    if not args:
        await message.answer(
            "⬇️ <b>YouTube Downloader</b>\n\n"
            "Usage: /download [options] <URL or search>\n\n"
            "Options:\n"
            "• --audio - Download audio only (MP3)\n"
            "• --info - Get video info without downloading\n"
            "• --search - Search YouTube videos\n\n"
            "Examples:\n"
            "• /download https://youtube.com/watch?v=...\n"
            "• /download --audio https://youtube.com/watch?v=...\n"
            "• /download --search funny cats\n"
            "• /download --info https://youtube.com/watch?v=..."
        )
        return

    # Parse options
    parts = args.split()
    audio_only = "--audio" in parts
    info_only = "--info" in parts
    search_mode = "--search" in parts

    # Remove options from parts
    url_or_query = " ".join([p for p in parts if not p.startswith("--")])

    if not url_or_query:
        await message.answer("❌ Please provide a URL or search query.")
        return

    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

    try:
        if search_mode:
            # Search YouTube
            results = await media_service.search_youtube(url_or_query, max_results=5)

            if not results:
                await message.answer("❌ No videos found.")
                return

            search_text = f"🔍 <b>YouTube Search: {url_or_query}</b>\n\n"

            for i, video in enumerate(results, 1):
                title = video.get("title", "Unknown")
                uploader = video.get("uploader", "Unknown")
                duration = video.get("duration", 0)

                # Format duration
                if duration:
                    minutes, seconds = divmod(duration, 60)
                    duration_str = f"{minutes}:{seconds:02d}"
                else:
                    duration_str = "Unknown"

                search_text += f"{i}. <b>{title}</b>\n"
                search_text += f"   👤 {uploader} | ⏱️ {duration_str}\n"
                search_text += f"   🔗 {video['url']}\n\n"

            await message.answer(search_text)
            return

        elif info_only:
            # Get video info
            info = await media_service.get_youtube_info(url_or_query)

            if not info:
                await message.answer("❌ Could not get video information.")
                return

            title = info.get("title", "Unknown")
            uploader = info.get("uploader", "Unknown")
            duration = info.get("duration", 0)
            view_count = info.get("view_count", 0)
            filesize = info.get("filesize", 0)

            # Format duration
            if duration:
                minutes, seconds = divmod(duration, 60)
                hours, minutes = divmod(minutes, 60)
                if hours:
                    duration_str = f"{hours}:{minutes:02d}:{seconds:02d}"
                else:
                    duration_str = f"{minutes}:{seconds:02d}"
            else:
                duration_str = "Unknown"

            # Format file size
            if filesize:
                size_mb = filesize / (1024 * 1024)
                size_str = f"{size_mb:.1f} MB"
            else:
                size_str = "Unknown"

            info_text = f"ℹ️ <b>Video Information</b>\n\n"
            info_text += f"📺 <b>{title}</b>\n\n"
            info_text += f"👤 Uploader: {uploader}\n"
            info_text += f"⏱️ Duration: {duration_str}\n"
            info_text += f"👀 Views: {view_count:,}\n"
            info_text += f"💾 Size: {size_str}\n"
            info_text += f"🔗 URL: {url_or_query}\n"

            if info.get("description"):
                description = info["description"][:200]
                info_text += f"\n📝 Description: {description}..."

            # Create download keyboard
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="📹 Download Video", callback_data=f"dl_video:{url_or_query[:50]}"),
                    InlineKeyboardButton(text="🎵 Download Audio", callback_data=f"dl_audio:{url_or_query[:50]}")
                ]
            ])

            await message.answer(info_text, reply_markup=keyboard)
            return

        else:
            # Download video/audio
            await message.bot.send_chat_action(
                message.chat.id,
                ChatAction.UPLOAD_DOCUMENT if not audio_only else ChatAction.UPLOAD_VOICE
            )

            result = await media_service.download_youtube_video(
                url_or_query,
                audio_only=audio_only
            )

            if not result:
                await message.answer("❌ Failed to download. The file might be too large or unavailable.")
                await log_bot_activity(message.from_user.id, "youtube_download", False)
                return

            file_path = result.get("file_path")
            if not file_path or not os.path.exists(file_path):
                await message.answer("❌ Download completed but file not found.")
                return

            # Check file size for Telegram limits
            file_size = os.path.getsize(file_path)
            if file_size > 50 * 1024 * 1024:  # 50MB limit
                await message.answer("❌ File too large for Telegram (>50MB). Try audio-only download.")
                os.unlink(file_path)  # Clean up
                return

            # Send the file
            title = result.get("title", "Downloaded Media")
            uploader = result.get("uploader", "Unknown")
            duration = result.get("duration", 0)

            caption = f"🎵 <b>{title}</b>\n👤 {uploader}"
            if duration:
                minutes, seconds = divmod(duration, 60)
                caption += f"\n⏱️ {minutes}:{seconds:02d}"

            try:
                if audio_only:
                    await message.answer_audio(
                        audio=FSInputFile(file_path),
                        caption=caption,
                        title=title,
                        performer=uploader
                    )
                else:
                    await message.answer_video(
                        video=FSInputFile(file_path),
                        caption=caption
                    )

                await log_bot_activity(
                    message.from_user.id,
                    "youtube_download",
                    True,
                    {"title": title, "audio_only": audio_only, "size_mb": file_size / (1024 * 1024)}
                )

            finally:
                # Clean up the file
                try:
                    os.unlink(file_path)
                except:
                    pass

    except Exception as e:
        logger.error(f"Error in download command: {e}")
        await message.answer("❌ Error processing download request.")
        await log_bot_activity(message.from_user.id, "youtube_download", False, {"error": str(e)})


@authorized_only
@log_command
async def spotify_command(message: Message):
    """Handle /spotify command for Spotify controls."""

    args = message.text.replace("/spotify", "").strip().split()

    if not args:
        # Show current status and controls
        await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

        current_track = await media_service.get_spotify_current_track()

        if current_track:
            name = current_track.get("name", "Unknown")
            artists = ", ".join(current_track.get("artists", ["Unknown"]))
            album = current_track.get("album", "Unknown")
            is_playing = current_track.get("is_playing", False)
            progress_ms = current_track.get("progress_ms", 0)
            duration_ms = current_track.get("duration_ms", 0)
            device = current_track.get("device", "Unknown")
            volume = current_track.get("volume", 0)

            # Format progress
            progress_min, progress_sec = divmod(progress_ms // 1000, 60)
            duration_min, duration_sec = divmod(duration_ms // 1000, 60)

            status_emoji = "▶️" if is_playing else "⏸️"

            spotify_text = f"🎵 <b>Spotify Status</b>\n\n"
            spotify_text += f"{status_emoji} <b>{name}</b>\n"
            spotify_text += f"👤 {artists}\n"
            spotify_text += f"💿 {album}\n"
            spotify_text += f"⏱️ {progress_min}:{progress_sec:02d} / {duration_min}:{duration_sec:02d}\n"
            spotify_text += f"📱 Device: {device}\n"
            spotify_text += f"🔊 Volume: {volume}%\n"

            # Create control keyboard
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="⏮️ Previous", callback_data="spotify_previous"),
                    InlineKeyboardButton(text="⏸️ Pause" if is_playing else "▶️ Play", callback_data="spotify_pause" if is_playing else "spotify_play"),
                    InlineKeyboardButton(text="⏭️ Next", callback_data="spotify_next")
                ],
                [
                    InlineKeyboardButton(text="🔀 Shuffle", callback_data="spotify_shuffle"),
                    InlineKeyboardButton(text="🔁 Repeat", callback_data="spotify_repeat"),
                    InlineKeyboardButton(text="🔊 Volume", callback_data="spotify_volume")
                ],
                [
                    InlineKeyboardButton(text="🔍 Search", callback_data="spotify_search"),
                    InlineKeyboardButton(text="📋 Playlists", callback_data="spotify_playlists")
                ]
            ])

            await message.answer(spotify_text, reply_markup=keyboard)
        else:
            await message.answer(
                "🎵 <b>Spotify</b>\n\n"
                "No music currently playing or Spotify not connected.\n\n"
                "<b>Commands:</b>\n"
                "• /spotify play - Resume playback\n"
                "• /spotify search [query] - Search music\n"
                "• /spotify playlists - Show playlists\n"
                "• /spotify volume [0-100] - Set volume"
            )

        return

    action = args[0].lower()

    if action == "play":
        success = await media_service.spotify_control("play")
        if success:
            await message.answer("▶️ Playback resumed.")
            await log_bot_activity(message.from_user.id, "spotify_play", True)
        else:
            await message.answer("❌ Failed to resume playback.")
            await log_bot_activity(message.from_user.id, "spotify_play", False)

    elif action == "pause":
        success = await media_service.spotify_control("pause")
        if success:
            await message.answer("⏸️ Playback paused.")
            await log_bot_activity(message.from_user.id, "spotify_pause", True)
        else:
            await message.answer("❌ Failed to pause playback.")
            await log_bot_activity(message.from_user.id, "spotify_pause", False)

    elif action == "next":
        success = await media_service.spotify_control("next")
        if success:
            await message.answer("⏭️ Skipped to next track.")
            await log_bot_activity(message.from_user.id, "spotify_next", True)
        else:
            await message.answer("❌ Failed to skip track.")
            await log_bot_activity(message.from_user.id, "spotify_next", False)

    elif action == "previous":
        success = await media_service.spotify_control("previous")
        if success:
            await message.answer("⏮️ Skipped to previous track.")
            await log_bot_activity(message.from_user.id, "spotify_previous", True)
        else:
            await message.answer("❌ Failed to skip to previous track.")
            await log_bot_activity(message.from_user.id, "spotify_previous", False)

    elif action == "volume" and len(args) > 1:
        try:
            volume = int(args[1])
            volume = max(0, min(100, volume))
            success = await media_service.spotify_control("volume", volume=volume)
            if success:
                await message.answer(f"🔊 Volume set to {volume}%.")
                await log_bot_activity(message.from_user.id, "spotify_volume", True, {"volume": volume})
            else:
                await message.answer("❌ Failed to set volume.")
                await log_bot_activity(message.from_user.id, "spotify_volume", False)
        except ValueError:
            await message.answer("❌ Invalid volume value. Use 0-100.")

    elif action == "search" and len(args) > 1:
        query = " ".join(args[1:])

        await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

        results = await media_service.search_spotify(query, "track", limit=5)

        if not results:
            await message.answer("❌ No tracks found.")
            return

        search_text = f"🔍 <b>Spotify Search: {query}</b>\n\n"

        for i, track in enumerate(results, 1):
            name = track.get("name", "Unknown")
            artists = ", ".join(track.get("artists", ["Unknown"]))
            album = track.get("album", "Unknown")
            duration_ms = track.get("duration_ms", 0)

            # Format duration
            duration_min, duration_sec = divmod(duration_ms // 1000, 60)

            search_text += f"{i}. <b>{name}</b>\n"
            search_text += f"   👤 {artists}\n"
            search_text += f"   💿 {album} | ⏱️ {duration_min}:{duration_sec:02d}\n\n"

        await message.answer(search_text)

    elif action == "playlists":
        await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

        playlists = await media_service.get_user_playlists()

        if not playlists:
            await message.answer("❌ No playlists found or Spotify not connected.")
            return

        playlist_text = "📋 <b>Your Spotify Playlists</b>\n\n"

        for i, playlist in enumerate(playlists[:10], 1):  # Limit to 10
            name = playlist.get("name", "Unknown")
            tracks_total = playlist.get("tracks_total", 0)
            public = "🌍" if playlist.get("public") else "🔒"

            playlist_text += f"{i}. {public} <b>{name}</b>\n"
            playlist_text += f"   🎵 {tracks_total} tracks\n\n"

        if len(playlists) > 10:
            playlist_text += f"... and {len(playlists) - 10} more playlists"

        await message.answer(playlist_text)

    else:
        await message.answer(
            "❌ Invalid Spotify command.\n\n"
            "Available commands:\n"
            "• play, pause, next, previous\n"
            "• volume [0-100]\n"
            "• search [query]\n"
            "• playlists"
        )


def register_handlers(dp: Dispatcher):
    """Register media handlers."""
    dp.message.register(download_command, Command("download"))
    dp.message.register(spotify_command, Command("spotify"))
