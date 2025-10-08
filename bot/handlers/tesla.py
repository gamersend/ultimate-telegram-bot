"""Tesla integration handlers."""

import logging
from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ChatAction

from bot.services.tesla import tesla_service
from bot.services.n8n import log_bot_activity
from bot.utils.decorators import authorized_only, log_command
from bot.utils.metrics import tesla_commands


logger = logging.getLogger(__name__)


@authorized_only
@log_command
async def tesla_command(message: Message):
    """Handle /tesla command for vehicle status and control."""

    args = message.text.replace("/tesla", "").strip().split()

    if not args or args[0] == "status":
        # Show vehicle status
        await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

        vehicles = await tesla_service.get_vehicles()

        if not vehicles:
            await message.answer(
                "🚗 No Tesla vehicles found.\n\n"
                "Please check your Tesla API configuration:\n"
                "• Email and refresh token in .env file\n"
                "• Tesla API access enabled"
            )
            return

        for vehicle in vehicles:
            vehicle_id = vehicle["id"]
            display_name = vehicle["display_name"]
            state = vehicle["state"]

            status_text = f"🚗 <b>{display_name}</b>\n\n"
            status_text += f"📍 State: {state.title()}\n"
            status_text += f"🆔 ID: {vehicle_id}\n"
            status_text += f"🎨 Color: {vehicle.get('color', 'Unknown')}\n"

            if state == "online":
                # Get detailed data
                vehicle_data = await tesla_service.get_vehicle_data(vehicle_id)

                if vehicle_data:
                    charge_state = vehicle_data.get("charge_state", {})
                    climate_state = vehicle_data.get("climate_state", {})
                    vehicle_state = vehicle_data.get("vehicle_state", {})

                    # Battery info
                    battery_level = charge_state.get("battery_level")
                    charging_state = charge_state.get("charging_state")

                    if battery_level is not None:
                        status_text += f"🔋 Battery: {battery_level}%"
                        if charging_state:
                            status_text += f" ({charging_state})"
                        status_text += "\n"

                    # Climate info
                    inside_temp = climate_state.get("inside_temp")
                    outside_temp = climate_state.get("outside_temp")
                    is_climate_on = climate_state.get("is_climate_on")

                    if inside_temp is not None:
                        status_text += f"🌡️ Inside: {inside_temp}°C"
                        if outside_temp is not None:
                            status_text += f" | Outside: {outside_temp}°C"
                        status_text += "\n"

                    if is_climate_on is not None:
                        climate_status = "On" if is_climate_on else "Off"
                        status_text += f"❄️ Climate: {climate_status}\n"

                    # Lock status
                    locked = vehicle_state.get("locked")
                    if locked is not None:
                        lock_status = "🔒 Locked" if locked else "🔓 Unlocked"
                        status_text += f"{lock_status}\n"

            # Create control keyboard
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="❄️ Climate", callback_data=f"tesla_climate:{vehicle_id}"),
                    InlineKeyboardButton(text="🔋 Charge", callback_data=f"tesla_charge:{vehicle_id}")
                ],
                [
                    InlineKeyboardButton(text="🔒 Lock", callback_data=f"tesla_lock:{vehicle_id}"),
                    InlineKeyboardButton(text="🔓 Unlock", callback_data=f"tesla_unlock:{vehicle_id}")
                ],
                [
                    InlineKeyboardButton(text="📯 Honk", callback_data=f"tesla_honk:{vehicle_id}"),
                    InlineKeyboardButton(text="💡 Flash", callback_data=f"tesla_flash:{vehicle_id}")
                ]
            ])

            await message.answer(status_text, reply_markup=keyboard)

    elif args[0] == "wake" and len(args) > 1:
        # Wake up vehicle
        try:
            vehicle_id = int(args[1])
            success = await tesla_service.wake_up_vehicle(vehicle_id)

            if success:
                await message.answer("🚗 Vehicle is waking up...")
                await log_bot_activity(message.from_user.id, "tesla_wake", True)
            else:
                await message.answer("❌ Failed to wake up vehicle.")
                await log_bot_activity(message.from_user.id, "tesla_wake", False)
        except ValueError:
            await message.answer("❌ Invalid vehicle ID.")

    else:
        await message.answer(
            "🚗 <b>Tesla Commands:</b>\n\n"
            "• /tesla status - Show vehicle status\n"
            "• /tesla wake [vehicle_id] - Wake up vehicle\n"
            "• /climate - Climate control\n"
            "• /charge - Charging control"
        )


@authorized_only
@log_command
async def climate_command(message: Message):
    """Handle /climate command for climate control."""

    args = message.text.replace("/climate", "").strip().split()

    if not args:
        await message.answer(
            "❄️ <b>Climate Control:</b>\n\n"
            "• /climate on [vehicle_id] - Start climate\n"
            "• /climate off [vehicle_id] - Stop climate\n"
            "• /climate temp [vehicle_id] [temperature] - Set temperature\n\n"
            "Use /tesla status to get vehicle IDs"
        )
        return

    action = args[0].lower()

    if len(args) < 2:
        await message.answer("❌ Please specify vehicle ID.")
        return

    try:
        vehicle_id = int(args[1])
    except ValueError:
        await message.answer("❌ Invalid vehicle ID.")
        return

    if action == "on":
        success = await tesla_service.start_climate(vehicle_id)
        if success:
            await message.answer("❄️ Climate control started.")
            await log_bot_activity(message.from_user.id, "tesla_climate_on", True)
        else:
            await message.answer("❌ Failed to start climate control.")
            await log_bot_activity(message.from_user.id, "tesla_climate_on", False)

    elif action == "off":
        success = await tesla_service.stop_climate(vehicle_id)
        if success:
            await message.answer("❄️ Climate control stopped.")
            await log_bot_activity(message.from_user.id, "tesla_climate_off", True)
        else:
            await message.answer("❌ Failed to stop climate control.")
            await log_bot_activity(message.from_user.id, "tesla_climate_off", False)

    elif action == "temp" and len(args) > 2:
        try:
            temperature = float(args[2])
            success = await tesla_service.set_temperature(vehicle_id, temperature)
            if success:
                await message.answer(f"🌡️ Temperature set to {temperature}°C.")
                await log_bot_activity(
                    message.from_user.id,
                    "tesla_temp_set",
                    True,
                    {"temperature": temperature}
                )
            else:
                await message.answer("❌ Failed to set temperature.")
                await log_bot_activity(message.from_user.id, "tesla_temp_set", False)
        except ValueError:
            await message.answer("❌ Invalid temperature value.")

    else:
        await message.answer("❌ Invalid climate command.")


@authorized_only
@log_command
async def charge_command(message: Message):
    """Handle /charge command for charging control."""

    args = message.text.replace("/charge", "").strip().split()

    if not args:
        await message.answer(
            "🔋 <b>Charging Control:</b>\n\n"
            "• /charge start [vehicle_id] - Start charging\n"
            "• /charge stop [vehicle_id] - Stop charging\n"
            "• /charge limit [vehicle_id] [percentage] - Set charge limit\n\n"
            "Use /tesla status to get vehicle IDs"
        )
        return

    action = args[0].lower()

    if len(args) < 2:
        await message.answer("❌ Please specify vehicle ID.")
        return

    try:
        vehicle_id = int(args[1])
    except ValueError:
        await message.answer("❌ Invalid vehicle ID.")
        return

    if action == "start":
        success = await tesla_service.start_charging(vehicle_id)
        if success:
            await message.answer("🔋 Charging started.")
            await log_bot_activity(message.from_user.id, "tesla_charge_start", True)
        else:
            await message.answer("❌ Failed to start charging.")
            await log_bot_activity(message.from_user.id, "tesla_charge_start", False)

    elif action == "stop":
        success = await tesla_service.stop_charging(vehicle_id)
        if success:
            await message.answer("🔋 Charging stopped.")
            await log_bot_activity(message.from_user.id, "tesla_charge_stop", True)
        else:
            await message.answer("❌ Failed to stop charging.")
            await log_bot_activity(message.from_user.id, "tesla_charge_stop", False)

    elif action == "limit" and len(args) > 2:
        try:
            limit = int(args[2])
            success = await tesla_service.set_charge_limit(vehicle_id, limit)
            if success:
                await message.answer(f"🔋 Charge limit set to {limit}%.")
                await log_bot_activity(
                    message.from_user.id,
                    "tesla_charge_limit",
                    True,
                    {"limit": limit}
                )
            else:
                await message.answer("❌ Failed to set charge limit.")
                await log_bot_activity(message.from_user.id, "tesla_charge_limit", False)
        except ValueError:
            await message.answer("❌ Invalid percentage value.")

    else:
        await message.answer("❌ Invalid charging command.")


def register_handlers(dp: Dispatcher):
    """Register Tesla handlers."""
    dp.message.register(tesla_command, Command("tesla"))
    dp.message.register(climate_command, Command("climate"))
    dp.message.register(charge_command, Command("charge"))
