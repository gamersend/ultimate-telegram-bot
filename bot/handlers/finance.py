"""Financial and market data handlers."""

import logging
from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ChatAction

from bot.services.finance import finance_service
from bot.services.n8n import log_bot_activity
from bot.utils.decorators import authorized_only, log_command
from bot.utils.metrics import finance_requests


logger = logging.getLogger(__name__)


@authorized_only
@log_command
async def stock_command(message: Message):
    """Handle /stock command for stock prices."""

    args = message.text.replace("/stock", "").strip()

    if not args:
        await message.answer(
            "📈 <b>Stock Price Lookup</b>\n\n"
            "Usage: /stock [symbol]\n\n"
            "Examples:\n"
            "• /stock AAPL - Apple Inc.\n"
            "• /stock TSLA - Tesla Inc.\n"
            "• /stock SPY - SPDR S&P 500 ETF\n\n"
            "You can also use /market for market overview."
        )
        return

    symbol = args.upper()

    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

    try:
        stock_data = await finance_service.get_stock_price(symbol)

        if not stock_data:
            await message.answer(f"❌ Could not find stock data for {symbol}")
            await log_bot_activity(message.from_user.id, "stock_lookup", False, {"symbol": symbol})
            return

        # Format stock information
        price = stock_data.get("price", 0)
        change = stock_data.get("change", 0)
        change_percent = stock_data.get("change_percent", 0)

        # Determine trend emoji
        trend_emoji = "📈" if change >= 0 else "📉"
        change_color = "🟢" if change >= 0 else "🔴"

        stock_text = f"📊 <b>{stock_data.get('name', symbol)} ({symbol})</b>\n\n"
        stock_text += f"💰 Price: ${price:.2f}\n"
        stock_text += f"{change_color} Change: ${change:.2f} ({change_percent:.2f}%)\n\n"

        # Additional info
        if stock_data.get("volume"):
            volume = stock_data["volume"]
            stock_text += f"📊 Volume: {volume:,}\n"

        if stock_data.get("market_cap"):
            market_cap = stock_data["market_cap"]
            stock_text += f"🏢 Market Cap: ${market_cap:,}\n"

        if stock_data.get("pe_ratio"):
            pe_ratio = stock_data["pe_ratio"]
            stock_text += f"📊 P/E Ratio: {pe_ratio:.2f}\n"

        if stock_data.get("52_week_high") and stock_data.get("52_week_low"):
            high_52 = stock_data["52_week_high"]
            low_52 = stock_data["52_week_low"]
            stock_text += f"📈 52W High: ${high_52:.2f}\n"
            stock_text += f"📉 52W Low: ${low_52:.2f}\n"

        if stock_data.get("sector"):
            stock_text += f"🏭 Sector: {stock_data['sector']}\n"

        if stock_data.get("exchange"):
            stock_text += f"🏛️ Exchange: {stock_data['exchange']}\n"

        # Create action keyboard
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Chart", callback_data=f"stock_chart:{symbol}"),
                InlineKeyboardButton(text="📈 Indicators", callback_data=f"stock_indicators:{symbol}")
            ],
            [
                InlineKeyboardButton(text="🔔 Set Alert", callback_data=f"stock_alert:{symbol}"),
                InlineKeyboardButton(text="🔄 Refresh", callback_data=f"stock_refresh:{symbol}")
            ]
        ])

        await message.answer(stock_text, reply_markup=keyboard)

        await log_bot_activity(
            message.from_user.id,
            "stock_lookup",
            True,
            {"symbol": symbol, "price": price}
        )

    except Exception as e:
        logger.error(f"Error in stock command: {e}")
        await message.answer("❌ Error retrieving stock data. Please try again.")
        await log_bot_activity(message.from_user.id, "stock_lookup", False, {"error": str(e)})


@authorized_only
@log_command
async def crypto_command(message: Message):
    """Handle /crypto command for crypto prices."""

    args = message.text.replace("/crypto", "").strip()

    if not args:
        await message.answer(
            "₿ <b>Cryptocurrency Price Lookup</b>\n\n"
            "Usage: /crypto [coin]\n\n"
            "Examples:\n"
            "• /crypto bitcoin\n"
            "• /crypto ethereum\n"
            "• /crypto BTC (searches for Bitcoin)\n"
            "• /crypto cardano\n\n"
            "You can also use /market for market overview."
        )
        return

    query = args.lower()

    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

    try:
        # First, search for the coin if it's not a direct ID
        if query in ["btc", "bitcoin"]:
            coin_id = "bitcoin"
        elif query in ["eth", "ethereum"]:
            coin_id = "ethereum"
        elif query in ["ada", "cardano"]:
            coin_id = "cardano"
        elif query in ["dot", "polkadot"]:
            coin_id = "polkadot"
        else:
            # Search for the coin
            search_results = await finance_service.search_crypto(query)

            if not search_results:
                await message.answer(f"❌ Could not find cryptocurrency matching '{query}'")
                return

            coin_id = search_results[0]["id"]

        # Get crypto data
        crypto_data = await finance_service.get_crypto_price(coin_id)

        if not crypto_data:
            await message.answer(f"❌ Could not get price data for {coin_id}")
            await log_bot_activity(message.from_user.id, "crypto_lookup", False, {"coin": coin_id})
            return

        # Format crypto information
        price = crypto_data.get("price", 0)
        change_24h = crypto_data.get("change_24h", 0)

        # Determine trend emoji
        trend_emoji = "📈" if change_24h >= 0 else "📉"
        change_color = "🟢" if change_24h >= 0 else "🔴"

        crypto_text = f"₿ <b>{crypto_data.get('name', coin_id)} ({crypto_data.get('symbol', '')})</b>\n\n"
        crypto_text += f"💰 Price: ${price:.6f}\n"
        crypto_text += f"{change_color} 24h Change: {change_24h:.2f}%\n\n"

        # Additional info
        if crypto_data.get("market_cap"):
            market_cap = crypto_data["market_cap"]
            crypto_text += f"🏢 Market Cap: ${market_cap:,.0f}\n"

        if crypto_data.get("volume_24h"):
            volume = crypto_data["volume_24h"]
            crypto_text += f"📊 24h Volume: ${volume:,.0f}\n"

        if crypto_data.get("rank"):
            rank = crypto_data["rank"]
            crypto_text += f"🏆 Rank: #{rank}\n"

        if crypto_data.get("ath"):
            ath = crypto_data["ath"]
            crypto_text += f"📈 All-Time High: ${ath:.6f}\n"

        if crypto_data.get("atl"):
            atl = crypto_data["atl"]
            crypto_text += f"📉 All-Time Low: ${atl:.6f}\n"

        if crypto_data.get("circulating_supply"):
            supply = crypto_data["circulating_supply"]
            crypto_text += f"🔄 Circulating Supply: {supply:,.0f}\n"

        # Create action keyboard
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Chart", callback_data=f"crypto_chart:{coin_id}"),
                InlineKeyboardButton(text="🔔 Set Alert", callback_data=f"crypto_alert:{coin_id}")
            ],
            [
                InlineKeyboardButton(text="🔄 Refresh", callback_data=f"crypto_refresh:{coin_id}"),
                InlineKeyboardButton(text="ℹ️ More Info", callback_data=f"crypto_info:{coin_id}")
            ]
        ])

        await message.answer(crypto_text, reply_markup=keyboard)

        await log_bot_activity(
            message.from_user.id,
            "crypto_lookup",
            True,
            {"coin": coin_id, "price": price}
        )

    except Exception as e:
        logger.error(f"Error in crypto command: {e}")
        await message.answer("❌ Error retrieving crypto data. Please try again.")
        await log_bot_activity(message.from_user.id, "crypto_lookup", False, {"error": str(e)})


@authorized_only
@log_command
async def market_command(message: Message):
    """Handle /market command for market overview."""

    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

    try:
        market_data = await finance_service.get_market_overview()

        if not market_data:
            await message.answer("❌ Could not retrieve market data.")
            return

        market_text = "📊 <b>Market Overview</b>\n\n"

        # Stock indices
        market_text += "<b>📈 Stock Indices:</b>\n"

        indices_map = {
            "^GSPC": "S&P 500",
            "^DJI": "Dow Jones",
            "^IXIC": "NASDAQ",
            "^VIX": "VIX (Fear Index)"
        }

        for symbol, data in market_data.items():
            if symbol.startswith("^"):
                name = indices_map.get(symbol, symbol)
                price = data.get("price", 0)
                change = data.get("change", 0)
                change_percent = data.get("change_percent", 0)

                trend_emoji = "🟢" if change >= 0 else "🔴"
                market_text += f"{trend_emoji} {name}: {price:.2f} ({change_percent:.2f}%)\n"

        # Crypto market
        if "crypto" in market_data:
            crypto = market_data["crypto"]
            market_text += "\n<b>₿ Crypto Market:</b>\n"

            if crypto.get("total_market_cap"):
                total_cap = crypto["total_market_cap"]
                market_text += f"🏢 Total Market Cap: ${total_cap:,.0f}\n"

            if crypto.get("total_volume"):
                total_vol = crypto["total_volume"]
                market_text += f"📊 24h Volume: ${total_vol:,.0f}\n"

            if crypto.get("bitcoin_dominance"):
                btc_dom = crypto["bitcoin_dominance"]
                market_text += f"₿ Bitcoin Dominance: {btc_dom:.1f}%\n"

        # Create quick action keyboard
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📈 Stocks", callback_data="market_stocks"),
                InlineKeyboardButton(text="₿ Crypto", callback_data="market_crypto")
            ],
            [
                InlineKeyboardButton(text="🔄 Refresh", callback_data="market_refresh"),
                InlineKeyboardButton(text="📊 Charts", callback_data="market_charts")
            ]
        ])

        await message.answer(market_text, reply_markup=keyboard)

        await log_bot_activity(message.from_user.id, "market_overview", True)

    except Exception as e:
        logger.error(f"Error in market command: {e}")
        await message.answer("❌ Error retrieving market overview.")
        await log_bot_activity(message.from_user.id, "market_overview", False, {"error": str(e)})


def register_handlers(dp: Dispatcher):
    """Register finance handlers."""
    dp.message.register(stock_command, Command("stock"))
    dp.message.register(crypto_command, Command("crypto"))
    dp.message.register(market_command, Command("market"))
