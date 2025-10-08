"""Smart home integration handlers."""

import logging
from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ChatAction

from bot.services.home_assistant import ha_service
from bot.services.n8n import log_bot_activity
from bot.utils.decorators import authorized_only, log_command
from bot.utils.metrics import smart_home_commands


logger = logging.getLogger(__name__)


@authorized_only
@log_command
async def lights_command(message: Message):
    """Handle /lights command for light control."""

    if not await ha_service.check_connection():
        await message.answer("❌ Home Assistant is not available. Please check your configuration.")
        return

    # Parse command arguments
    args = message.text.replace("/lights", "").strip().split()

    if not args:
        # Show available lights
        await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

        lights = await ha_service.get_entities_by_domain("light")

        if not lights:
            await message.answer("💡 No lights found in Home Assistant.")
            return

        lights_text = "💡 <b>Available Lights:</b>\n\n"
        for light in lights[:10]:  # Limit to first 10
            entity_id = light.get("entity_id", "")
            friendly_name = light.get("attributes", {}).get("friendly_name", entity_id)
            state = light.get("state", "unknown")

            status_emoji = "🟢" if state == "on" else "🔴"
            lights_text += f"{status_emoji} <code>{entity_id}</code> - {friendly_name}\n"

        if len(lights) > 10:
            lights_text += f"\n... and {len(lights) - 10} more lights"

        lights_text += "\n\n<b>Usage:</b>\n"
        lights_text += "• /lights on [name] - Turn on light(s)\n"
        lights_text += "• /lights off [name] - Turn off light(s)\n"
        lights_text += "• /lights toggle [name] - Toggle light(s)\n"
        lights_text += "• /lights dim [name] [0-100] - Set brightness\n"
        lights_text += "• /lights color [name] [r,g,b] - Set RGB color"

        await message.answer(lights_text)
        return

    action = args[0].lower()

    if action in ["on", "off", "toggle"]:
        # Light control
        if len(args) < 2:
            await message.answer("❌ Please specify which light(s) to control.")
            return

        light_name = " ".join(args[1:])

        # Find matching lights
        lights = await ha_service.find_entities(light_name, "light")

        if not lights:
            await message.answer(f"❌ No lights found matching '{light_name}'.")
            return

        success_count = 0
        for light in lights:
            entity_id = light["entity_id"]

            if action == "on":
                success = await ha_service.turn_on_entity(entity_id)
            elif action == "off":
                success = await ha_service.turn_off_entity(entity_id)
            else:  # toggle
                success = await ha_service.toggle_entity(entity_id)

            if success:
                success_count += 1

        if success_count > 0:
            await message.answer(f"💡 Successfully {action}ed {success_count} light(s).")
            await log_bot_activity(
                message.from_user.id,
                "lights_control",
                True,
                {"action": action, "count": success_count}
            )
        else:
            await message.answer("❌ Failed to control lights.")
            await log_bot_activity(message.from_user.id, "lights_control", False)

    elif action == "dim" and len(args) >= 3:
        # Brightness control
        light_name = " ".join(args[1:-1])
        try:
            brightness_percent = int(args[-1])
            brightness_255 = int((brightness_percent / 100) * 255)
        except ValueError:
            await message.answer("❌ Invalid brightness value. Use 0-100.")
            return

        lights = await ha_service.find_entities(light_name, "light")

        if not lights:
            await message.answer(f"❌ No lights found matching '{light_name}'.")
            return

        success_count = 0
        for light in lights:
            success = await ha_service.set_light_brightness(light["entity_id"], brightness_255)
            if success:
                success_count += 1

        if success_count > 0:
            await message.answer(f"💡 Set brightness to {brightness_percent}% for {success_count} light(s).")
        else:
            await message.answer("❌ Failed to set brightness.")

    elif action == "color" and len(args) >= 3:
        # Color control
        light_name = " ".join(args[1:-1])
        try:
            rgb_str = args[-1]
            rgb_values = [int(x.strip()) for x in rgb_str.split(",")]
            if len(rgb_values) != 3:
                raise ValueError
        except ValueError:
            await message.answer("❌ Invalid RGB values. Use format: r,g,b (0-255)")
            return

        lights = await ha_service.find_entities(light_name, "light")

        if not lights:
            await message.answer(f"❌ No lights found matching '{light_name}'.")
            return

        success_count = 0
        for light in lights:
            success = await ha_service.set_light_color(light["entity_id"], rgb_values)
            if success:
                success_count += 1

        if success_count > 0:
            await message.answer(f"🎨 Set color to RGB({rgb_values[0]},{rgb_values[1]},{rgb_values[2]}) for {success_count} light(s).")
        else:
            await message.answer("❌ Failed to set color.")

    else:
        await message.answer("❌ Invalid command. Use: on, off, toggle, dim, or color")


@authorized_only
@log_command
async def scene_command(message: Message):
    """Handle /scene command for scene activation."""

    if not await ha_service.check_connection():
        await message.answer("❌ Home Assistant is not available.")
        return

    args = message.text.replace("/scene", "").strip()

    if not args:
        # Show available scenes
        scenes = await ha_service.get_entities_by_domain("scene")

        if not scenes:
            await message.answer("🏠 No scenes found in Home Assistant.")
            return

        scenes_text = "🏠 <b>Available Scenes:</b>\n\n"
        for scene in scenes[:15]:  # Limit to first 15
            entity_id = scene.get("entity_id", "")
            friendly_name = scene.get("attributes", {}).get("friendly_name", entity_id)
            scenes_text += f"• <code>{entity_id}</code> - {friendly_name}\n"

        if len(scenes) > 15:
            scenes_text += f"\n... and {len(scenes) - 15} more scenes"

        scenes_text += "\n\n<b>Usage:</b> /scene [scene_name]"

        await message.answer(scenes_text)
        return

    # Find and activate scene
    scenes = await ha_service.find_entities(args, "scene")

    if not scenes:
        await message.answer(f"❌ No scene found matching '{args}'.")
        return

    scene = scenes[0]  # Use first match
    success = await ha_service.activate_scene(scene["entity_id"])

    if success:
        await message.answer(f"🏠 Activated scene: {scene['friendly_name']}")
        await log_bot_activity(
            message.from_user.id,
            "scene_activation",
            True,
            {"scene": scene["entity_id"]}
        )
    else:
        await message.answer("❌ Failed to activate scene.")
        await log_bot_activity(message.from_user.id, "scene_activation", False)


@authorized_only
@log_command
async def temp_command(message: Message):
    """Handle /temp command for temperature monitoring."""

    if not await ha_service.check_connection():
        await message.answer("❌ Home Assistant is not available.")
        return

    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

    # Get temperature sensors
    sensors = await ha_service.get_entities_by_domain("sensor")
    temp_sensors = [
        s for s in sensors
        if "temperature" in s.get("entity_id", "").lower() or
           "temp" in s.get("attributes", {}).get("friendly_name", "").lower()
    ]

    if not temp_sensors:
        await message.answer("🌡️ No temperature sensors found.")
        return

    temp_text = "🌡️ <b>Temperature Readings:</b>\n\n"

    for sensor in temp_sensors[:10]:  # Limit to first 10
        entity_id = sensor.get("entity_id", "")
        friendly_name = sensor.get("attributes", {}).get("friendly_name", entity_id)
        state = sensor.get("state", "unknown")
        unit = sensor.get("attributes", {}).get("unit_of_measurement", "")

        if state != "unknown" and state != "unavailable":
            temp_text += f"📍 {friendly_name}: {state}{unit}\n"

    # Also get climate entities
    climate_entities = await ha_service.get_entities_by_domain("climate")

    if climate_entities:
        temp_text += "\n🏠 <b>Climate Control:</b>\n\n"

        for climate in climate_entities[:5]:
            entity_id = climate.get("entity_id", "")
            friendly_name = climate.get("attributes", {}).get("friendly_name", entity_id)
            current_temp = climate.get("attributes", {}).get("current_temperature")
            target_temp = climate.get("attributes", {}).get("temperature")

            if current_temp is not None:
                temp_text += f"🏠 {friendly_name}:\n"
                temp_text += f"   Current: {current_temp}°C\n"
                if target_temp is not None:
                    temp_text += f"   Target: {target_temp}°C\n"
                temp_text += "\n"

    await message.answer(temp_text)


@authorized_only
@log_command
async def home_status_command(message: Message):
    """Handle /home command for overall home status."""

    if not await ha_service.check_connection():
        await message.answer("❌ Home Assistant is not available.")
        return

    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

    try:
        # Get system info
        system_info = await ha_service.get_system_info()

        status_text = "🏠 <b>Home Status</b>\n\n"

        if system_info:
            status_text += f"🏠 Home Assistant: {system_info.get('version', 'Unknown')}\n"
            status_text += f"📍 Location: {system_info.get('location_name', 'Unknown')}\n\n"

        # Quick summary of key entities
        lights = await ha_service.get_entities_by_domain("light")
        switches = await ha_service.get_entities_by_domain("switch")
        sensors = await ha_service.get_entities_by_domain("sensor")
        climate = await ha_service.get_entities_by_domain("climate")

        # Count states
        lights_on = sum(1 for light in lights if light.get("state") == "on")
        switches_on = sum(1 for switch in switches if switch.get("state") == "on")

        status_text += f"💡 Lights: {lights_on}/{len(lights)} on\n"
        status_text += f"🔌 Switches: {switches_on}/{len(switches)} on\n"
        status_text += f"📊 Sensors: {len(sensors)} active\n"
        status_text += f"🌡️ Climate zones: {len(climate)}\n\n"

        # Recent activity (simplified)
        status_text += "<b>Quick Actions:</b>\n"
        status_text += "• /lights - Control lighting\n"
        status_text += "• /scene - Activate scenes\n"
        status_text += "• /temp - Check temperatures\n"

        # Create quick action keyboard
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="💡 All Lights Off", callback_data="ha_all_lights_off"),
                InlineKeyboardButton(text="🌙 Good Night", callback_data="ha_goodnight")
            ],
            [
                InlineKeyboardButton(text="🏠 Home Scene", callback_data="ha_scene_home"),
                InlineKeyboardButton(text="🔒 Lock All", callback_data="ha_lock_all")
            ]
        ])

        await message.answer(status_text, reply_markup=keyboard)

    except Exception as e:
        logger.error(f"Error getting home status: {e}")
        await message.answer("❌ Error getting home status.")


@authorized_only
@log_command
async def areas_command(message: Message):
    """Handle /areas command to show home areas."""

    if not await ha_service.check_connection():
        await message.answer("❌ Home Assistant is not available.")
        return

    areas = await ha_service.get_areas()

    if not areas:
        await message.answer("🏠 No areas configured in Home Assistant.")
        return

    areas_text = "🏠 <b>Home Areas:</b>\n\n"

    for area in areas[:20]:  # Limit to first 20
        area_name = area.get("name", "Unknown")
        area_id = area.get("area_id", "")

        areas_text += f"📍 {area_name} (<code>{area_id}</code>)\n"

    if len(areas) > 20:
        areas_text += f"\n... and {len(areas) - 20} more areas"

    await message.answer(areas_text)


def register_handlers(dp: Dispatcher):
    """Register smart home handlers."""
    dp.message.register(lights_command, Command("lights"))
    dp.message.register(scene_command, Command("scene"))
    dp.message.register(temp_command, Command("temp"))
    dp.message.register(home_status_command, Command("home"))
    dp.message.register(areas_command, Command("areas"))
