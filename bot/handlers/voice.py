"""Voice and audio processing handlers."""

import logging
import os
import tempfile
from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, Voice, Audio, Document, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ChatAction

from bot.services.ai import ai_service
from bot.services.audio import audio_processor
from bot.services.n8n import n8n_service, log_bot_activity
from bot.utils.decorators import authorized_only, log_command
from bot.utils.metrics import voice_messages


logger = logging.getLogger(__name__)


@authorized_only
async def voice_handler(message: Message):
    """Handle voice messages for transcription with enhanced processing."""
    voice_messages.inc()

    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

    try:
        # Download voice message
        voice: Voice = message.voice
        file_info = await message.bot.get_file(voice.file_id)

        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as temp_file:
            await message.bot.download_file(file_info.file_path, temp_file.name)
            temp_path = temp_file.name

        try:
            # Get audio info
            audio_info = await audio_processor.extract_audio_info(temp_path)
            duration = audio_info.get('duration', 0)

            # Transcribe audio with quality enhancement
            transcription = await audio_processor.transcribe_audio(
                temp_path,
                use_local=True,
                enhance_quality=True
            )

            if transcription:
                # Create response with audio info
                response = f"🎙️ <b>Voice Transcription:</b>\n\n{transcription}"

                if duration > 0:
                    response += f"\n\n📊 <i>Duration: {duration:.1f}s</i>"

                # Create inline keyboard for actions
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text="🤖 Ask AI", callback_data=f"ai_ask:{transcription[:50]}"),
                        InlineKeyboardButton(text="📝 Summarize", callback_data=f"ai_summarize:{transcription[:50]}")
                    ],
                    [
                        InlineKeyboardButton(text="🔊 Text-to-Speech", callback_data=f"tts:{transcription[:50]}"),
                        InlineKeyboardButton(text="📋 Save Note", callback_data=f"save_note:{transcription[:50]}")
                    ]
                ])

                await message.answer(response, reply_markup=keyboard)

                # Log activity to n8n
                await log_bot_activity(
                    message.from_user.id,
                    "voice_transcription",
                    True,
                    {"duration": duration, "text_length": len(transcription)}
                )
            else:
                await message.answer("❌ Sorry, I couldn't transcribe your voice message.")
                await log_bot_activity(message.from_user.id, "voice_transcription", False)

        finally:
            # Clean up temporary file
            os.unlink(temp_path)

    except Exception as e:
        logger.error(f"Error transcribing voice message: {e}")
        await message.answer("❌ Sorry, I couldn't transcribe your voice message.")
        await log_bot_activity(message.from_user.id, "voice_transcription", False, {"error": str(e)})


@authorized_only
@log_command
async def tts_command(message: Message):
    """Handle /tts command for text-to-speech with options."""

    # Parse command arguments
    args = message.text.replace("/tts", "").strip().split()

    if not args:
        await message.answer(
            "🔊 <b>Text-to-Speech</b>\n\n"
            "Usage: /tts [options] <text>\n\n"
            "Options:\n"
            "• --voice <voice> (alloy, echo, fable, onyx, nova, shimmer)\n"
            "• --speed <0.25-4.0> (default: 1.0)\n\n"
            "Examples:\n"
            "• /tts Hello world!\n"
            "• /tts --voice nova --speed 1.2 Hello there!"
        )
        return

    # Parse options
    voice = "alloy"
    speed = 1.0
    text_parts = []

    i = 0
    while i < len(args):
        if args[i] == "--voice" and i + 1 < len(args):
            voice = args[i + 1]
            i += 2
        elif args[i] == "--speed" and i + 1 < len(args):
            try:
                speed = float(args[i + 1])
                speed = max(0.25, min(4.0, speed))  # Clamp to valid range
            except ValueError:
                pass
            i += 2
        else:
            text_parts.append(args[i])
            i += 1

    text = " ".join(text_parts)
    if not text:
        await message.answer("❌ Please provide text to convert to speech.")
        return

    await message.bot.send_chat_action(message.chat.id, ChatAction.RECORD_VOICE)

    try:
        # Generate speech with options
        audio_content = await audio_processor.generate_speech(
            text=text,
            voice=voice,
            speed=speed
        )

        if audio_content:
            # Send as voice message
            caption = f"🔊 <i>{text}</i>"
            if voice != "alloy" or speed != 1.0:
                caption += f"\n\n⚙️ Voice: {voice}, Speed: {speed}x"

            await message.answer_voice(
                voice=audio_content,
                caption=caption
            )

            await log_bot_activity(
                message.from_user.id,
                "text_to_speech",
                True,
                {"voice": voice, "speed": speed, "text_length": len(text)}
            )
        else:
            await message.answer("❌ Sorry, I couldn't generate speech right now.")
            await log_bot_activity(message.from_user.id, "text_to_speech", False)

    except Exception as e:
        logger.error(f"Error in TTS command: {e}")
        await message.answer("❌ Sorry, I couldn't generate speech right now.")
        await log_bot_activity(message.from_user.id, "text_to_speech", False, {"error": str(e)})


@authorized_only
@log_command
async def audio_info_command(message: Message):
    """Handle /audioinfo command for audio file analysis."""

    # Check if replying to an audio message
    if not message.reply_to_message or not (message.reply_to_message.voice or message.reply_to_message.audio):
        await message.answer("📊 Please reply to an audio message with /audioinfo")
        return

    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

    try:
        # Get the audio file
        if message.reply_to_message.voice:
            audio_file = message.reply_to_message.voice
            file_type = "Voice Message"
        else:
            audio_file = message.reply_to_message.audio
            file_type = "Audio File"

        file_info = await message.bot.get_file(audio_file.file_id)

        # Download and analyze
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as temp_file:
            await message.bot.download_file(file_info.file_path, temp_file.name)
            temp_path = temp_file.name

        try:
            audio_info = await audio_processor.extract_audio_info(temp_path)

            info_text = f"📊 <b>{file_type} Analysis:</b>\n\n"
            info_text += f"⏱️ Duration: {audio_info.get('duration', 0):.1f} seconds\n"
            info_text += f"🔊 Channels: {audio_info.get('channels', 'Unknown')}\n"
            info_text += f"📡 Sample Rate: {audio_info.get('sample_rate', 'Unknown')} Hz\n"
            info_text += f"📏 Sample Width: {audio_info.get('sample_width', 'Unknown')} bytes\n"
            info_text += f"📁 Format: {audio_info.get('format', 'Unknown')}\n"
            info_text += f"💾 Size: {audio_info.get('size_mb', 0):.2f} MB"

            await message.answer(info_text)

        finally:
            os.unlink(temp_path)

    except Exception as e:
        logger.error(f"Error analyzing audio: {e}")
        await message.answer("❌ Sorry, I couldn't analyze the audio file.")


@authorized_only
@log_command
async def audio_effects_command(message: Message):
    """Handle /effects command for audio effects."""

    if not message.reply_to_message or not (message.reply_to_message.voice or message.reply_to_message.audio):
        await message.answer(
            "🎛️ <b>Audio Effects</b>\n\n"
            "Reply to an audio message with /effects [options]\n\n"
            "Available effects:\n"
            "• --speed <0.5-2.0> - Change playback speed\n"
            "• --pitch <0.5-2.0> - Change pitch\n"
            "• --volume <0.1-3.0> - Adjust volume\n"
            "• --echo - Add echo effect\n"
            "• --reverb - Add reverb effect\n\n"
            "Example: /effects --speed 1.5 --echo"
        )
        return

    # Parse effects from command
    args = message.text.replace("/effects", "").strip().split()
    effects = {}

    i = 0
    while i < len(args):
        if args[i] == "--speed" and i + 1 < len(args):
            try:
                effects["speed"] = max(0.5, min(2.0, float(args[i + 1])))
            except ValueError:
                pass
            i += 2
        elif args[i] == "--pitch" and i + 1 < len(args):
            try:
                effects["pitch"] = max(0.5, min(2.0, float(args[i + 1])))
            except ValueError:
                pass
            i += 2
        elif args[i] == "--volume" and i + 1 < len(args):
            try:
                effects["volume"] = max(0.1, min(3.0, float(args[i + 1])))
            except ValueError:
                pass
            i += 2
        elif args[i] == "--echo":
            effects["echo"] = True
            i += 1
        elif args[i] == "--reverb":
            effects["reverb"] = True
            i += 1
        else:
            i += 1

    if not effects:
        await message.answer("❌ Please specify at least one effect.")
        return

    await message.bot.send_chat_action(message.chat.id, ChatAction.RECORD_VOICE)

    try:
        # Get the audio file
        if message.reply_to_message.voice:
            audio_file = message.reply_to_message.voice
        else:
            audio_file = message.reply_to_message.audio

        file_info = await message.bot.get_file(audio_file.file_id)

        # Download and process
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as temp_file:
            await message.bot.download_file(file_info.file_path, temp_file.name)
            temp_path = temp_file.name

        try:
            # Apply effects
            processed_path = await audio_processor.add_audio_effects(temp_path, effects)

            if processed_path:
                # Send processed audio
                with open(processed_path, "rb") as audio_file:
                    effects_desc = ", ".join([f"{k}: {v}" for k, v in effects.items()])

                    await message.answer_voice(
                        voice=audio_file.read(),
                        caption=f"🎛️ <b>Audio with Effects:</b>\n<i>{effects_desc}</i>"
                    )

                os.unlink(processed_path)
            else:
                await message.answer("❌ Sorry, I couldn't apply the effects.")

        finally:
            os.unlink(temp_path)

    except Exception as e:
        logger.error(f"Error applying audio effects: {e}")
        await message.answer("❌ Sorry, I couldn't process the audio.")


def register_handlers(dp: Dispatcher):
    """Register voice handlers."""
    dp.message.register(voice_handler, F.voice)
    dp.message.register(tts_command, Command("tts"))
    dp.message.register(audio_info_command, Command("audioinfo"))
    dp.message.register(audio_effects_command, Command("effects"))
