#!/bin/bash
# Simple Bot Starter

echo "🤖 Starting Ultimate Telegram Bot..."

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please copy .env.example to .env and configure your API keys"
    exit 1
fi

# Start the bot directly
echo "🚀 Starting bot..."
python3 -m bot.main
