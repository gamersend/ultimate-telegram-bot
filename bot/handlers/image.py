"""Image processing and generation handlers."""

import logging
import tempfile
import os
from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, PhotoSize, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ChatAction

from bot.services.image_generation import image_processor
from bot.services.n8n import log_bot_activity
from bot.utils.decorators import authorized_only, log_command
from bot.utils.metrics import images_generated


logger = logging.getLogger(__name__)


@authorized_only
@log_command
async def generate_sd_command(message: Message):
    """Handle /sd command for local Stable Diffusion generation."""

    # Parse command arguments
    args = message.text.replace("/sd", "").strip()

    if not args:
        await message.answer(
            "🎨 <b>Stable Diffusion Image Generation</b>\n\n"
            "Usage: /sd [options] <prompt>\n\n"
            "Options:\n"
            "• --size <width>x<height> (default: 512x512)\n"
            "• --steps <10-50> (default: 20)\n"
            "• --cfg <1-20> (default: 7.0)\n"
            "• --negative <negative prompt>\n"
            "• --sampler <sampler name>\n\n"
            "Examples:\n"
            "• /sd a beautiful sunset over mountains\n"
            "• /sd --size 768x768 --steps 30 cyberpunk city\n"
            "• /sd --negative blurry, low quality a portrait"
        )
        return

    # Check if SD is available
    if not await image_processor.check_sd_availability():
        await message.answer(
            "❌ Local Stable Diffusion is not available.\n"
            "Use /generate for cloud-based image generation."
        )
        return

    await message.bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)

    try:
        # Parse options
        parts = args.split()
        options = {}
        prompt_parts = []

        i = 0
        while i < len(parts):
            if parts[i] == "--size" and i + 1 < len(parts):
                try:
                    size = parts[i + 1].split('x')
                    options["width"] = int(size[0])
                    options["height"] = int(size[1])
                except (ValueError, IndexError):
                    pass
                i += 2
            elif parts[i] == "--steps" and i + 1 < len(parts):
                try:
                    options["steps"] = max(10, min(50, int(parts[i + 1])))
                except ValueError:
                    pass
                i += 2
            elif parts[i] == "--cfg" and i + 1 < len(parts):
                try:
                    options["cfg_scale"] = max(1.0, min(20.0, float(parts[i + 1])))
                except ValueError:
                    pass
                i += 2
            elif parts[i] == "--negative" and i + 1 < len(parts):
                # Collect negative prompt until next option
                neg_parts = []
                j = i + 1
                while j < len(parts) and not parts[j].startswith("--"):
                    neg_parts.append(parts[j])
                    j += 1
                options["negative_prompt"] = " ".join(neg_parts)
                i = j
            elif parts[i] == "--sampler" and i + 1 < len(parts):
                options["sampler"] = parts[i + 1]
                i += 2
            else:
                prompt_parts.append(parts[i])
                i += 1

        prompt = " ".join(prompt_parts)
        if not prompt:
            await message.answer("❌ Please provide a prompt for image generation.")
            return

        # Generate image
        image_data = await image_processor.generate_image_sd(prompt, **options)

        if image_data:
            # Create inline keyboard for actions
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔄 Regenerate", callback_data=f"regen_sd:{prompt[:50]}"),
                    InlineKeyboardButton(text="📈 Upscale", callback_data=f"upscale:{prompt[:50]}")
                ],
                [
                    InlineKeyboardButton(text="✏️ Edit", callback_data=f"edit_img:{prompt[:50]}"),
                    InlineKeyboardButton(text="ℹ️ Info", callback_data=f"img_info:{prompt[:50]}")
                ]
            ])

            caption = f"🎨 <b>Generated with Stable Diffusion:</b>\n<i>{prompt}</i>"
            if options:
                settings_text = ", ".join([f"{k}: {v}" for k, v in options.items() if k != "negative_prompt"])
                if settings_text:
                    caption += f"\n\n⚙️ Settings: {settings_text}"

            await message.answer_photo(
                photo=image_data,
                caption=caption,
                reply_markup=keyboard
            )

            await log_bot_activity(
                message.from_user.id,
                "sd_generation",
                True,
                {"prompt": prompt, "options": options}
            )
        else:
            await message.answer("❌ Failed to generate image. Please try again.")
            await log_bot_activity(message.from_user.id, "sd_generation", False)

    except Exception as e:
        logger.error(f"Error in SD generation: {e}")
        await message.answer("❌ Sorry, I couldn't generate the image.")
        await log_bot_activity(message.from_user.id, "sd_generation", False, {"error": str(e)})


@authorized_only
@log_command
async def edit_image_command(message: Message):
    """Handle /edit command for image editing."""

    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.answer(
            "✏️ <b>Image Editing</b>\n\n"
            "Reply to an image with /edit [prompt] to modify it\n\n"
            "Examples:\n"
            "• /edit make it more colorful\n"
            "• /edit add a sunset background\n"
            "• /edit convert to black and white"
        )
        return

    prompt = message.text.replace("/edit", "").strip()
    if not prompt:
        await message.answer("❌ Please provide editing instructions.")
        return

    await message.bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)

    try:
        # Get the largest photo
        photo = message.reply_to_message.photo[-1]
        file_info = await message.bot.get_file(photo.file_id)

        # Download image
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            await message.bot.download_file(file_info.file_path, temp_file.name)
            temp_path = temp_file.name

        try:
            with open(temp_path, "rb") as f:
                image_data = f.read()

            # Try img2img with SD first
            if await image_processor.check_sd_availability():
                result = await image_processor.img2img_sd(image_data, prompt)
            else:
                # Fallback to basic enhancement
                result = await image_processor.enhance_image(image_data)

            if result:
                await message.answer_photo(
                    photo=result,
                    caption=f"✏️ <b>Edited Image:</b>\n<i>{prompt}</i>"
                )

                await log_bot_activity(
                    message.from_user.id,
                    "image_edit",
                    True,
                    {"prompt": prompt}
                )
            else:
                await message.answer("❌ Failed to edit the image.")
                await log_bot_activity(message.from_user.id, "image_edit", False)

        finally:
            os.unlink(temp_path)

    except Exception as e:
        logger.error(f"Error editing image: {e}")
        await message.answer("❌ Sorry, I couldn't edit the image.")
        await log_bot_activity(message.from_user.id, "image_edit", False, {"error": str(e)})


@authorized_only
@log_command
async def upscale_command(message: Message):
    """Handle /upscale command for image upscaling."""

    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.answer("📈 Please reply to an image with /upscale")
        return

    await message.bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)

    try:
        # Get the largest photo
        photo = message.reply_to_message.photo[-1]
        file_info = await message.bot.get_file(photo.file_id)

        # Download image
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            await message.bot.download_file(file_info.file_path, temp_file.name)
            temp_path = temp_file.name

        try:
            with open(temp_path, "rb") as f:
                image_data = f.read()

            # Get original image info
            original_info = await image_processor.get_image_info(image_data)

            # Try SD upscaling first
            if await image_processor.check_sd_availability():
                result = await image_processor.upscale_image_sd(image_data)
            else:
                # Fallback to basic resize
                new_width = original_info.get("width", 512) * 2
                new_height = original_info.get("height", 512) * 2
                result = await image_processor.resize_image(image_data, new_width, new_height)

            if result:
                new_info = await image_processor.get_image_info(result)

                caption = (
                    f"📈 <b>Upscaled Image:</b>\n"
                    f"Original: {original_info.get('width', 0)}x{original_info.get('height', 0)}\n"
                    f"Upscaled: {new_info.get('width', 0)}x{new_info.get('height', 0)}"
                )

                await message.answer_photo(photo=result, caption=caption)
                await log_bot_activity(message.from_user.id, "image_upscale", True)
            else:
                await message.answer("❌ Failed to upscale the image.")
                await log_bot_activity(message.from_user.id, "image_upscale", False)

        finally:
            os.unlink(temp_path)

    except Exception as e:
        logger.error(f"Error upscaling image: {e}")
        await message.answer("❌ Sorry, I couldn't upscale the image.")
        await log_bot_activity(message.from_user.id, "image_upscale", False, {"error": str(e)})


@authorized_only
@log_command
async def enhance_image_command(message: Message):
    """Handle /enhance command for image enhancement."""

    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.answer(
            "✨ <b>Image Enhancement</b>\n\n"
            "Reply to an image with /enhance [options]\n\n"
            "Options:\n"
            "• --brightness <0.1-3.0> (default: 1.0)\n"
            "• --contrast <0.1-3.0> (default: 1.0)\n"
            "• --saturation <0.1-3.0> (default: 1.0)\n"
            "• --sharpness <0.1-3.0> (default: 1.0)\n"
            "• --filter <blur|sharpen|smooth|edge_enhance>\n\n"
            "Examples:\n"
            "• /enhance --brightness 1.2 --contrast 1.1\n"
            "• /enhance --filter sharpen\n"
            "• /enhance --saturation 1.5 --sharpness 1.2"
        )
        return

    # Parse enhancement options
    args = message.text.replace("/enhance", "").strip().split()
    options = {}
    filters = []

    i = 0
    while i < len(args):
        if args[i] == "--brightness" and i + 1 < len(args):
            try:
                options["brightness"] = max(0.1, min(3.0, float(args[i + 1])))
            except ValueError:
                pass
            i += 2
        elif args[i] == "--contrast" and i + 1 < len(args):
            try:
                options["contrast"] = max(0.1, min(3.0, float(args[i + 1])))
            except ValueError:
                pass
            i += 2
        elif args[i] == "--saturation" and i + 1 < len(args):
            try:
                options["saturation"] = max(0.1, min(3.0, float(args[i + 1])))
            except ValueError:
                pass
            i += 2
        elif args[i] == "--sharpness" and i + 1 < len(args):
            try:
                options["sharpness"] = max(0.1, min(3.0, float(args[i + 1])))
            except ValueError:
                pass
            i += 2
        elif args[i] == "--filter" and i + 1 < len(args):
            filter_name = args[i + 1]
            if filter_name in ["blur", "sharpen", "smooth", "edge_enhance"]:
                filters.append(filter_name)
            i += 2
        else:
            i += 1

    if filters:
        options["apply_filters"] = filters

    await message.bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)

    try:
        # Get the largest photo
        photo = message.reply_to_message.photo[-1]
        file_info = await message.bot.get_file(photo.file_id)

        # Download image
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            await message.bot.download_file(file_info.file_path, temp_file.name)
            temp_path = temp_file.name

        try:
            with open(temp_path, "rb") as f:
                image_data = f.read()

            # Apply enhancements
            result = await image_processor.enhance_image(image_data, **options)

            if result:
                # Create description of applied enhancements
                enhancements = []
                for key, value in options.items():
                    if key != "apply_filters" and value != 1.0:
                        enhancements.append(f"{key}: {value}")
                if filters:
                    enhancements.append(f"filters: {', '.join(filters)}")

                caption = "✨ <b>Enhanced Image</b>"
                if enhancements:
                    caption += f"\n<i>{', '.join(enhancements)}</i>"

                await message.answer_photo(photo=result, caption=caption)
                await log_bot_activity(message.from_user.id, "image_enhance", True, options)
            else:
                await message.answer("❌ Failed to enhance the image.")
                await log_bot_activity(message.from_user.id, "image_enhance", False)

        finally:
            os.unlink(temp_path)

    except Exception as e:
        logger.error(f"Error enhancing image: {e}")
        await message.answer("❌ Sorry, I couldn't enhance the image.")
        await log_bot_activity(message.from_user.id, "image_enhance", False, {"error": str(e)})


@authorized_only
@log_command
async def image_info_command(message: Message):
    """Handle /imginfo command for image information."""

    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.answer("ℹ️ Please reply to an image with /imginfo")
        return

    try:
        # Get the largest photo
        photo = message.reply_to_message.photo[-1]
        file_info = await message.bot.get_file(photo.file_id)

        # Download image
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            await message.bot.download_file(file_info.file_path, temp_file.name)
            temp_path = temp_file.name

        try:
            with open(temp_path, "rb") as f:
                image_data = f.read()

            # Get image information
            info = await image_processor.get_image_info(image_data)

            info_text = f"ℹ️ <b>Image Information:</b>\n\n"
            info_text += f"📏 Dimensions: {info.get('width', 0)}x{info.get('height', 0)}\n"
            info_text += f"📁 Format: {info.get('format', 'Unknown')}\n"
            info_text += f"🎨 Mode: {info.get('mode', 'Unknown')}\n"
            info_text += f"💾 Size: {info.get('size_mb', 0):.2f} MB\n"
            info_text += f"🔍 Transparency: {'Yes' if info.get('has_transparency') else 'No'}"

            await message.answer(info_text)

        finally:
            os.unlink(temp_path)

    except Exception as e:
        logger.error(f"Error getting image info: {e}")
        await message.answer("❌ Sorry, I couldn't analyze the image.")


@authorized_only
@log_command
async def sd_models_command(message: Message):
    """Handle /models command to list available SD models."""

    if not await image_processor.check_sd_availability():
        await message.answer("❌ Local Stable Diffusion is not available.")
        return

    try:
        models = await image_processor.get_sd_models()

        if models:
            models_text = "🎨 <b>Available Stable Diffusion Models:</b>\n\n"
            for i, model in enumerate(models[:10], 1):  # Limit to first 10
                models_text += f"{i}. <code>{model}</code>\n"

            if len(models) > 10:
                models_text += f"\n... and {len(models) - 10} more models"

            await message.answer(models_text)
        else:
            await message.answer("❌ No models found.")

    except Exception as e:
        logger.error(f"Error getting SD models: {e}")
        await message.answer("❌ Sorry, I couldn't retrieve the model list.")


def register_handlers(dp: Dispatcher):
    """Register image handlers."""
    dp.message.register(generate_sd_command, Command("sd"))
    dp.message.register(edit_image_command, Command("edit"))
    dp.message.register(upscale_command, Command("upscale"))
    dp.message.register(enhance_image_command, Command("enhance"))
    dp.message.register(image_info_command, Command("imginfo"))
    dp.message.register(sd_models_command, Command("models"))
