"""AI-related command handlers."""

import logging
from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile
from aiogram.enums import ChatAction

from bot.services.ai import get_ai_response, ai_service
from bot.utils.decorators import authorized_only, log_command
from bot.utils.metrics import command_counter


logger = logging.getLogger(__name__)


@authorized_only
@log_command
async def ask_command(message: Message):
    """Handle /ask command for AI chat."""
    command_counter.labels(command="ask").inc()
    
    # Extract question from command
    question = message.text.replace("/ask", "").strip()
    if not question:
        await message.answer("❓ Please provide a question after /ask\n\nExample: /ask What is the weather like?")
        return
    
    # Show typing indicator
    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    
    try:
        # Get AI response
        response = await get_ai_response(
            user_message=question,
            system_prompt="You are a helpful AI assistant. Provide clear, concise answers with emojis when appropriate."
        )
        
        await message.answer(f"🤖 <b>AI Response:</b>\n\n{response}")
        
    except Exception as e:
        logger.error(f"Error in ask command: {e}")
        await message.answer("❌ Sorry, I encountered an error while processing your question.")


@authorized_only
@log_command
async def explain_command(message: Message):
    """Handle /explain command for detailed explanations."""
    command_counter.labels(command="explain").inc()
    
    topic = message.text.replace("/explain", "").strip()
    if not topic:
        await message.answer("📚 Please provide a topic to explain after /explain\n\nExample: /explain quantum computing")
        return
    
    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    
    try:
        response = await get_ai_response(
            user_message=f"Please provide a detailed explanation of: {topic}",
            system_prompt="You are an expert educator. Provide comprehensive, well-structured explanations "
                         "that are easy to understand. Use examples and break down complex concepts."
        )
        
        await message.answer(f"📚 <b>Explanation: {topic}</b>\n\n{response}")
        
    except Exception as e:
        logger.error(f"Error in explain command: {e}")
        await message.answer("❌ Sorry, I couldn't generate an explanation right now.")


@authorized_only
@log_command
async def code_command(message: Message):
    """Handle /code command for coding assistance."""
    command_counter.labels(command="code").inc()
    
    request = message.text.replace("/code", "").strip()
    if not request:
        await message.answer(
            "💻 Please provide a coding request after /code\n\n"
            "Examples:\n"
            "• /code python function to sort a list\n"
            "• /code javascript async/await example\n"
            "• /code fix this bug: [paste code]"
        )
        return
    
    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    
    try:
        response = await get_ai_response(
            user_message=request,
            system_prompt="You are an expert programmer. Provide clean, well-commented code with explanations. "
                         "Include best practices and explain the solution step by step."
        )
        
        await message.answer(f"💻 <b>Code Solution:</b>\n\n{response}")
        
    except Exception as e:
        logger.error(f"Error in code command: {e}")
        await message.answer("❌ Sorry, I couldn't help with coding right now.")


@authorized_only
@log_command
async def summarize_command(message: Message):
    """Handle /summarize command for text summarization."""
    command_counter.labels(command="summarize").inc()
    
    # Check if replying to a message
    if message.reply_to_message and message.reply_to_message.text:
        text_to_summarize = message.reply_to_message.text
    else:
        text_to_summarize = message.text.replace("/summarize", "").strip()
    
    if not text_to_summarize:
        await message.answer(
            "📝 Please provide text to summarize or reply to a message with /summarize\n\n"
            "Examples:\n"
            "• /summarize [long text]\n"
            "• Reply to a message with /summarize"
        )
        return
    
    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    
    try:
        response = await get_ai_response(
            user_message=f"Please provide a concise summary of this text:\n\n{text_to_summarize}",
            system_prompt="You are a skilled summarizer. Create clear, concise summaries that capture "
                         "the key points and main ideas. Use bullet points when appropriate."
        )
        
        await message.answer(f"📝 <b>Summary:</b>\n\n{response}")
        
    except Exception as e:
        logger.error(f"Error in summarize command: {e}")
        await message.answer("❌ Sorry, I couldn't create a summary right now.")


@authorized_only
@log_command
async def generate_image_command(message: Message):
    """Handle /generate command for image generation."""
    command_counter.labels(command="generate").inc()
    
    prompt = message.text.replace("/generate", "").strip()
    if not prompt:
        await message.answer(
            "🎨 Please provide an image description after /generate\n\n"
            "Example: /generate a futuristic city at sunset"
        )
        return
    
    await message.bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)
    
    try:
        # Generate image
        image_urls = await ai_service.generate_image(prompt)
        
        if image_urls:
            await message.answer_photo(
                photo=image_urls[0],
                caption=f"🎨 <b>Generated Image:</b>\n<i>{prompt}</i>"
            )
        else:
            await message.answer("❌ Failed to generate image.")
            
    except Exception as e:
        logger.error(f"Error in generate image command: {e}")
        await message.answer("❌ Sorry, I couldn't generate an image right now.")


@authorized_only
async def chat_handler(message: Message):
    """Handle general chat messages for AI conversation."""
    
    # Only respond to direct messages or mentions
    if message.chat.type != "private":
        return
    
    # Skip if message starts with /
    if message.text and message.text.startswith("/"):
        return
    
    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    
    try:
        response = await get_ai_response(
            user_message=message.text,
            system_prompt="You are a friendly AI assistant in a Telegram chat. "
                         "Be conversational, helpful, and use emojis appropriately. "
                         "Keep responses concise but informative."
        )
        
        await message.answer(response)
        
    except Exception as e:
        logger.error(f"Error in chat handler: {e}")
        await message.answer("🤔 Sorry, I didn't quite catch that. Could you try again?")


def register_handlers(dp: Dispatcher):
    """Register AI handlers."""
    dp.message.register(ask_command, Command("ask"))
    dp.message.register(explain_command, Command("explain"))
    dp.message.register(code_command, Command("code"))
    dp.message.register(summarize_command, Command("summarize"))
    dp.message.register(generate_image_command, Command("generate"))
    
    # General chat handler (should be registered last, exclude commands)
    dp.message.register(chat_handler, F.text & F.chat.type == "private" & ~F.text.startswith("/"))
