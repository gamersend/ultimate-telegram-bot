"""News and information feed handlers."""

import logging
from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ChatAction

from bot.services.news import news_service
from bot.services.n8n import log_bot_activity
from bot.utils.decorators import authorized_only, log_command


logger = logging.getLogger(__name__)


@authorized_only
@log_command
async def news_command(message: Message):
    """Handle /news command for latest news."""

    args = message.text.replace("/news", "").strip().split()

    if not args:
        # Show available categories
        categories = await news_service.get_feed_categories()

        news_text = "📰 <b>News & Information</b>\n\n"
        news_text += "<b>Available Categories:</b>\n"

        for category in categories:
            news_text += f"• /news {category} - {category.title()} news\n"

        news_text += "\n<b>Other Commands:</b>\n"
        news_text += "• /news search [query] - Search news\n"
        news_text += "• /news trending - Trending topics\n"
        news_text += "• /news digest - Daily digest\n"
        news_text += "• /feeds - Manage RSS feeds\n"

        # Create quick category buttons
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📱 Tech", callback_data="news_tech"),
                InlineKeyboardButton(text="🌍 News", callback_data="news_news")
            ],
            [
                InlineKeyboardButton(text="🔬 Science", callback_data="news_science"),
                InlineKeyboardButton(text="💼 Business", callback_data="news_business")
            ],
            [
                InlineKeyboardButton(text="🔥 Trending", callback_data="news_trending"),
                InlineKeyboardButton(text="📋 Digest", callback_data="news_digest")
            ]
        ])

        await message.answer(news_text, reply_markup=keyboard)
        return

    command = args[0].lower()

    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

    if command in ["tech", "news", "science", "business"]:
        # Get news by category
        try:
            articles = await news_service.get_news_by_category(command, max_items=5)

            if not articles:
                await message.answer(f"❌ No {command} news found at the moment.")
                return

            news_text = f"📰 <b>{command.title()} News</b>\n\n"

            for i, article in enumerate(articles, 1):
                title = article.get("title", "No Title")
                source = article.get("source", "Unknown")
                description = article.get("description", "")
                link = article.get("link", "")
                published = article.get("published", "")

                # Format published date
                if published:
                    try:
                        from datetime import datetime
                        pub_date = datetime.fromisoformat(published.replace('Z', '+00:00'))
                        time_str = pub_date.strftime("%H:%M")
                    except:
                        time_str = ""
                else:
                    time_str = ""

                news_text += f"{i}. <b>{title}</b>\n"
                news_text += f"   📰 {source}"
                if time_str:
                    news_text += f" • {time_str}"
                news_text += "\n"

                if description:
                    # Limit description length
                    desc = description[:150] + "..." if len(description) > 150 else description
                    news_text += f"   {desc}\n"

                if link:
                    news_text += f"   🔗 <a href='{link}'>Read more</a>\n"

                news_text += "\n"

            # Create action buttons
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔄 Refresh", callback_data=f"news_refresh_{command}"),
                    InlineKeyboardButton(text="📋 Digest", callback_data="news_digest")
                ],
                [
                    InlineKeyboardButton(text="🔍 Search", callback_data="news_search"),
                    InlineKeyboardButton(text="📡 Feeds", callback_data="news_feeds")
                ]
            ])

            await message.answer(news_text, reply_markup=keyboard, disable_web_page_preview=True)

            await log_bot_activity(
                message.from_user.id,
                "news_category",
                True,
                {"category": command, "articles_count": len(articles)}
            )

        except Exception as e:
            logger.error(f"Error getting {command} news: {e}")
            await message.answer("❌ Error retrieving news. Please try again.")
            await log_bot_activity(message.from_user.id, "news_category", False, {"error": str(e)})

    elif command == "search" and len(args) > 1:
        # Search news
        query = " ".join(args[1:])

        try:
            articles = await news_service.search_news_api(query, max_items=5)

            if not articles:
                await message.answer(f"❌ No news found for '{query}'.")
                return

            news_text = f"🔍 <b>Search Results: {query}</b>\n\n"

            for i, article in enumerate(articles, 1):
                title = article.get("title", "No Title")
                source = article.get("source", "Unknown")
                description = article.get("description", "")
                link = article.get("link", "")

                news_text += f"{i}. <b>{title}</b>\n"
                news_text += f"   📰 {source}\n"

                if description:
                    desc = description[:150] + "..." if len(description) > 150 else description
                    news_text += f"   {desc}\n"

                if link:
                    news_text += f"   🔗 <a href='{link}'>Read more</a>\n"

                news_text += "\n"

            await message.answer(news_text, disable_web_page_preview=True)

            await log_bot_activity(
                message.from_user.id,
                "news_search",
                True,
                {"query": query, "results_count": len(articles)}
            )

        except Exception as e:
            logger.error(f"Error searching news: {e}")
            await message.answer("❌ Error searching news. Please try again.")
            await log_bot_activity(message.from_user.id, "news_search", False, {"error": str(e)})

    elif command == "trending":
        # Get trending topics
        try:
            trending = await news_service.get_trending_topics()

            if not trending:
                await message.answer("❌ No trending topics available.")
                return

            trending_text = "🔥 <b>Trending Topics</b>\n\n"

            for i, topic in enumerate(trending, 1):
                trending_text += f"{i}. {topic}\n"

            trending_text += "\n💡 Use /news search [topic] to find related articles"

            await message.answer(trending_text)

            await log_bot_activity(message.from_user.id, "news_trending", True)

        except Exception as e:
            logger.error(f"Error getting trending topics: {e}")
            await message.answer("❌ Error getting trending topics.")
            await log_bot_activity(message.from_user.id, "news_trending", False, {"error": str(e)})

    elif command == "digest":
        # Create news digest
        try:
            categories = ["tech", "news", "business"]
            digest = await news_service.create_news_digest(categories, max_per_category=2)

            # Split digest if too long for Telegram
            if len(digest) > 4000:
                parts = [digest[i:i+4000] for i in range(0, len(digest), 4000)]
                for i, part in enumerate(parts):
                    if i == 0:
                        await message.answer(part, disable_web_page_preview=True)
                    else:
                        await message.answer(f"📰 <b>Digest (continued {i+1})</b>\n\n{part}", disable_web_page_preview=True)
            else:
                await message.answer(digest, disable_web_page_preview=True)

            await log_bot_activity(message.from_user.id, "news_digest", True)

        except Exception as e:
            logger.error(f"Error creating news digest: {e}")
            await message.answer("❌ Error creating news digest.")
            await log_bot_activity(message.from_user.id, "news_digest", False, {"error": str(e)})

    else:
        await message.answer("❌ Invalid news command. Use /news to see available options.")


@authorized_only
@log_command
async def feeds_command(message: Message):
    """Handle /feeds command for RSS feed management."""

    args = message.text.replace("/feeds", "").strip().split()

    if not args:
        # Show feed management options
        feeds_text = "📡 <b>RSS Feed Management</b>\n\n"
        feeds_text += "<b>Commands:</b>\n"
        feeds_text += "• /feeds list - Show available feeds\n"
        feeds_text += "• /feeds add [url] [category] - Add custom feed\n"
        feeds_text += "• /feeds test [url] - Test RSS feed\n"
        feeds_text += "• /feeds categories - Show categories\n"

        # Show default categories
        categories = await news_service.get_feed_categories()
        feeds_text += f"\n<b>Default Categories:</b>\n"
        for category in categories:
            feeds_text += f"• {category.title()}\n"

        await message.answer(feeds_text)
        return

    command = args[0].lower()

    if command == "list":
        # List available feeds
        categories = await news_service.get_feed_categories()

        feeds_text = "📡 <b>Available RSS Feeds</b>\n\n"

        for category in categories:
            feeds_text += f"<b>{category.title()}:</b>\n"
            feeds = news_service.default_feeds.get(category, [])
            for feed in feeds[:3]:  # Show first 3 feeds per category
                # Extract domain name
                try:
                    from urllib.parse import urlparse
                    domain = urlparse(feed).netloc
                    feeds_text += f"• {domain}\n"
                except:
                    feeds_text += f"• {feed[:50]}...\n"
            feeds_text += "\n"

        await message.answer(feeds_text)

    elif command == "add" and len(args) >= 2:
        # Add custom feed
        feed_url = args[1]
        category = args[2] if len(args) > 2 else "custom"

        await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

        try:
            success = await news_service.add_custom_feed(message.from_user.id, feed_url, category)

            if success:
                await message.answer(f"✅ RSS feed added successfully!\n\nURL: {feed_url}\nCategory: {category}")
                await log_bot_activity(
                    message.from_user.id,
                    "feed_add",
                    True,
                    {"url": feed_url, "category": category}
                )
            else:
                await message.answer("❌ Failed to add RSS feed. Please check the URL and try again.")
                await log_bot_activity(message.from_user.id, "feed_add", False)

        except Exception as e:
            logger.error(f"Error adding RSS feed: {e}")
            await message.answer("❌ Error adding RSS feed.")
            await log_bot_activity(message.from_user.id, "feed_add", False, {"error": str(e)})

    elif command == "test" and len(args) >= 2:
        # Test RSS feed
        feed_url = args[1]

        await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

        try:
            articles = await news_service.parse_rss_feed(feed_url, max_items=3)

            if articles:
                test_text = f"✅ <b>RSS Feed Test Successful</b>\n\n"
                test_text += f"URL: {feed_url}\n"
                test_text += f"Articles found: {len(articles)}\n\n"
                test_text += "<b>Sample Articles:</b>\n"

                for i, article in enumerate(articles, 1):
                    title = article.get("title", "No Title")
                    source = article.get("source", "Unknown")
                    test_text += f"{i}. {title} ({source})\n"

                await message.answer(test_text)
            else:
                await message.answer("❌ RSS feed test failed. No articles found or invalid feed.")

        except Exception as e:
            logger.error(f"Error testing RSS feed: {e}")
            await message.answer("❌ Error testing RSS feed.")

    elif command == "categories":
        # Show categories
        categories = await news_service.get_feed_categories()

        cat_text = "📂 <b>Feed Categories</b>\n\n"
        for category in categories:
            cat_text += f"• {category.title()}\n"

        cat_text += "\n💡 Use /news [category] to get news from that category"

        await message.answer(cat_text)

    else:
        await message.answer("❌ Invalid feeds command. Use /feeds to see available options.")


def register_handlers(dp: Dispatcher):
    """Register news handlers."""
    dp.message.register(news_command, Command("news"))
    dp.message.register(feeds_command, Command("feeds"))
