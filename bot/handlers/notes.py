"""Notes and file management handlers."""

import logging
import os
from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, Document

from bot.utils.decorators import authorized_only, log_command


logger = logging.getLogger(__name__)


@authorized_only
@log_command
async def note_command(message: Message):
    """Handle /note command for creating and managing notes."""

    args = message.text.replace("/note", "").strip()

    if not args:
        # Show notes management options
        notes_text = "📝 <b>Notes Management</b>\n\n"
        notes_text += "<b>Commands:</b>\n"
        notes_text += "• /note create [title] - Create new note\n"
        notes_text += "• /note list - Show recent notes\n"
        notes_text += "• /note search [query] - Search notes\n"
        notes_text += "• /note notion [title] - Create Notion page\n"
        notes_text += "• /files - File management\n\n"
        notes_text += "<b>Quick Actions:</b>\n"
        notes_text += "• Reply to any message with /note to save it\n"
        notes_text += "• Send a document to upload to cloud storage"

        await message.answer(notes_text)
        return

    parts = args.split(maxsplit=1)
    command = parts[0].lower()

    if command == "create":
        # Create a new note
        if len(parts) < 2:
            await message.answer("❌ Please provide a title for the note.\n\nUsage: /note create [title]")
            return

        title = parts[1]

        # Check if replying to a message
        if message.reply_to_message:
            content = message.reply_to_message.text or message.reply_to_message.caption or ""
            if not content:
                await message.answer("❌ The replied message has no text content.")
                return

            # Create simple local note
            from datetime import datetime
            import os

            # Create notes directory
            notes_dir = f"data/notes/{message.from_user.id}"
            os.makedirs(notes_dir, exist_ok=True)

            # Create note file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{title[:30]}.txt"
            filepath = os.path.join(notes_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Title: {title}\n")
                f.write(f"Created: {datetime.now().isoformat()}\n")
                f.write(f"From: Telegram Bot\n\n")
                f.write(content)

            await message.answer(f"✅ Note saved: {title}\n📁 File: {filename}")
        else:
            await message.answer(f"📝 Creating note: <b>{title}</b>\n\nPlease reply to a message to save it as a note.")

    elif command == "list":
        # List recent notes
        notes_dir = f"data/notes/{message.from_user.id}"
        if not os.path.exists(notes_dir):
            await message.answer("📝 No notes found. Create your first note!")
            return

        files = sorted([f for f in os.listdir(notes_dir) if f.endswith('.txt')], reverse=True)

        if not files:
            await message.answer("📝 No notes found.")
            return

        notes_text = f"📝 <b>Your Notes ({len(files)})</b>\n\n"
        for i, filename in enumerate(files[:10], 1):
            # Extract title from filename
            title = filename.replace('.txt', '').split('_', 1)[1] if '_' in filename else filename
            notes_text += f"{i}. {title}\n"

        await message.answer(notes_text)

    else:
        await message.answer("❌ Available commands: create, list")


@authorized_only
@log_command
async def files_command(message: Message):
    """Handle /files command for file management."""

    files_text = "📁 <b>File Management</b>\n\n"
    files_text += "<b>Features:</b>\n"
    files_text += "• Send any document to save it\n"
    files_text += "• Google Drive integration (when configured)\n"
    files_text += "• Notion integration (when configured)\n\n"
    files_text += "💡 Send a document to automatically save it!"

    await message.answer(files_text)


@authorized_only
async def document_handler(message: Message):
    """Handle document uploads for automatic saving."""

    if not message.document:
        return

    document = message.document

    try:
        # Create user directory
        files_dir = f"data/files/{message.from_user.id}"
        os.makedirs(files_dir, exist_ok=True)

        # Download the document
        file_info = await message.bot.get_file(document.file_id)

        # Save with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{document.file_name}"
        filepath = os.path.join(files_dir, filename)

        await message.bot.download_file(file_info.file_path, filepath)

        # Get file size
        file_size = os.path.getsize(filepath)
        size_mb = file_size / (1024 * 1024)

        upload_text = f"✅ <b>File Saved</b>\n\n"
        upload_text += f"📁 Name: {document.file_name}\n"
        upload_text += f"💾 Size: {size_mb:.2f} MB\n"
        upload_text += f"📂 Saved as: {filename}"

        await message.answer(upload_text)

    except Exception as e:
        logger.error(f"Error saving document: {e}")
        await message.answer("❌ Error saving file.")


def register_handlers(dp: Dispatcher):
    """Register notes handlers."""
    dp.message.register(note_command, Command("note"))
    dp.message.register(files_command, Command("files"))
    dp.message.register(document_handler, lambda message: message.document is not None)
