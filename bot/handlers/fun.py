"""Fun and entertainment handlers."""

import logging
from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ChatAction

from bot.services.fun import fun_service
from bot.services.n8n import log_bot_activity
from bot.utils.decorators import authorized_only, log_command


logger = logging.getLogger(__name__)


@authorized_only
@log_command
async def meme_command(message: Message):
    """Handle /meme command for random memes."""

    await message.bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)

    try:
        meme = await fun_service.get_random_meme()

        if meme:
            caption = f"😂 <b>{meme['title']}</b>\n\n"
            caption += f"📊 Score: {meme['score']}\n"
            caption += f"📱 r/{meme['subreddit']}"

            await message.answer_photo(
                photo=meme['url'],
                caption=caption
            )

            await log_bot_activity(message.from_user.id, "meme_request", True)
        else:
            await message.answer("😅 Couldn't find a meme right now. Try again!")
            await log_bot_activity(message.from_user.id, "meme_request", False)

    except Exception as e:
        logger.error(f"Error getting meme: {e}")
        await message.answer("❌ Error getting meme. Please try again.")


@authorized_only
@log_command
async def gif_command(message: Message):
    """Handle /gif command for GIF search."""

    args = message.text.replace("/gif", "").strip()

    if not args:
        await message.answer("🎬 Please provide a search term!\n\nExample: /gif funny cats")
        return

    await message.bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_VIDEO)

    try:
        gif = await fun_service.search_gif(args)

        if gif:
            caption = f"🔍 <b>GIF: {args}</b>\n\n{gif['title']}"

            await message.answer_animation(
                animation=gif['url'],
                caption=caption
            )

            await log_bot_activity(message.from_user.id, "gif_search", True, {"query": args})
        else:
            await message.answer(f"🔍 No GIFs found for '{args}'. Try a different search!")
            await log_bot_activity(message.from_user.id, "gif_search", False)

    except Exception as e:
        logger.error(f"Error searching GIF: {e}")
        await message.answer("❌ Error searching GIFs. Please try again.")


@authorized_only
@log_command
async def trivia_command(message: Message):
    """Handle /trivia command for trivia questions."""

    args = message.text.replace("/trivia", "").strip().split()
    category = args[0] if args else "general"

    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

    try:
        question_data = await fun_service.get_trivia_question(category)

        if question_data:
            question_text = f"🧠 <b>Trivia Question</b>\n\n"
            question_text += f"📂 {question_data['category']}\n"
            question_text += f"⭐ {question_data['difficulty'].title()}\n\n"
            question_text += f"❓ <b>{question_data['question']}</b>\n\n"

            for i, answer in enumerate(question_data['all_answers']):
                question_text += f"{chr(65+i)}. {answer}\n"

            question_text += f"\n💡 Correct answer: {question_data['correct_answer']}"

            await message.answer(question_text)
            await log_bot_activity(message.from_user.id, "trivia_question", True)
        else:
            await message.answer("🧠 Couldn't get a trivia question right now.")
            await log_bot_activity(message.from_user.id, "trivia_question", False)

    except Exception as e:
        logger.error(f"Error getting trivia: {e}")
        await message.answer("❌ Error getting trivia question.")


@authorized_only
@log_command
async def joke_command(message: Message):
    """Handle /joke command for jokes."""

    try:
        # Try dad joke first, fallback to random
        joke = await fun_service.get_dad_joke()
        if not joke:
            joke = await fun_service.get_random_joke()

        await message.answer(f"😂 <b>Joke:</b>\n\n{joke}")
        await log_bot_activity(message.from_user.id, "joke_request", True)

    except Exception as e:
        logger.error(f"Error getting joke: {e}")
        await message.answer("❌ Error getting joke.")


@authorized_only
@log_command
async def fact_command(message: Message):
    """Handle /fact command for fun facts."""

    try:
        fact = await fun_service.get_fun_fact()
        await message.answer(f"🤓 <b>Fun Fact:</b>\n\n{fact}")
        await log_bot_activity(message.from_user.id, "fun_fact", True)

    except Exception as e:
        logger.error(f"Error getting fact: {e}")
        await message.answer("❌ Error getting fun fact.")


def register_handlers(dp: Dispatcher):
    """Register fun handlers."""
    dp.message.register(meme_command, Command("meme"))
    dp.message.register(gif_command, Command("gif"))
    dp.message.register(trivia_command, Command("trivia"))
    dp.message.register(joke_command, Command("joke"))
    dp.message.register(fact_command, Command("fact"))
