# 🤖 Ultimate Telegram Bot

> **The most comprehensive personal AI assistant bot for Telegram with enterprise-level features**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![n8n Compatible](https://img.shields.io/badge/n8n-automation-green.svg)](https://n8n.io/)

## ✨ Features Overview

### 🧠 AI Integration
- **Local OpenAI Endpoint**: `http://192.168.0.150:4000/v1` integration
- **Multiple AI Providers**: OpenAI, Anthropic Claude support
- **Smart Conversations**: Context-aware chat with memory
- **Code Assistance**: Programming help and code generation
- **Text Processing**: Summarization, explanation, and analysis

### 🏠 Smart Home Control
- **Home Assistant Integration**: Complete smart home control
- **Light Management**: Natural language light control
- **Scene Activation**: One-command scene management
- **Temperature Monitoring**: Multi-zone climate tracking

### 🚗 Tesla Integration
- **Vehicle Status**: Real-time monitoring and diagnostics
- **Climate Control**: Remote temperature management
- **Charging Management**: Battery and charging control
- **Security Features**: Lock/unlock, honk, flash lights

### 💰 Financial Tracking
- **Stock Prices**: Real-time stock market data via yfinance
- **Cryptocurrency**: Live crypto prices via pycoingecko
- **Market Analysis**: Technical indicators and charts
- **Price Alerts**: Automated notification system via n8n

### 🎵 Media & Entertainment
- **YouTube Downloads**: Video and audio downloads via yt-dlp
- **Spotify Control**: Full playback management
- **Meme Generation**: Random memes from Reddit
- **Fun Features**: Jokes, trivia, GIFs, and games

### 📰 News & Information
- **RSS Aggregation**: Multiple news sources
- **Category Filtering**: Tech, science, business news
- **AI Summarization**: Automated article summaries
- **Custom Feeds**: Personal RSS feed management

### 📝 Productivity
- **Note Management**: Local and cloud note storage
- **Notion Integration**: Create and manage Notion pages
- **Google Drive**: File upload and management
- **Voice Processing**: Speech-to-text and text-to-speech

### 🔄 Advanced Automation
- **n8n Workflows**: 8+ automated workflows
- **Activity Logging**: Comprehensive usage tracking
- **Health Monitoring**: System performance alerts
- **Cost Tracking**: AI usage and expense monitoring

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Telegram Bot Token
- OpenAI API Key (or local endpoint)
- n8n instance (optional but recommended)

### Installation

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd tele
   python3 fix_dependencies.py
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Start the Bot**
   ```bash
   # Polling mode (recommended for testing)
   python3 start_polling.py
   
   # Webhook mode (for production)
   python3 start_simple.sh
   ```

### Configuration

Edit `.env` file with your credentials:

```env
# Required
TELEGRAM_BOT_TOKEN=your_bot_token_here
OPENAI_API_KEY=your_openai_key_here
OPENAI_BASE_URL=http://192.168.0.150:4000/v1
ALLOWED_USER_IDS=your_user_id,another_user_id

# Optional Integrations
HOME_ASSISTANT_URL=http://your_ha_ip:8123
HOME_ASSISTANT_TOKEN=your_ha_token
TESLA_EMAIL=your_tesla_email
SPOTIFY_CLIENT_ID=your_spotify_id
NEWS_API_KEY=your_news_api_key
GIPHY_API_KEY=your_giphy_key
```

## 📋 Available Commands (33 Total)

### Basic Commands
- `/start` - Welcome message and feature overview
- `/help` - Complete command reference
- `/status` - Bot status and health check

### AI Commands
- `/ask [question]` - Chat with AI
- `/explain [topic]` - Get detailed explanations
- `/code [request]` - Programming assistance
- `/summarize [text]` - Text summarization
- `/generate [prompt]` - Image generation

### Fun Commands
- `/meme` - Random memes from Reddit
- `/joke` - Random jokes and dad jokes
- `/fact` - Fun facts
- `/trivia [category]` - Trivia questions
- `/gif [search]` - GIF search via Giphy

### Financial Commands
- `/stock [symbol]` - Stock prices (e.g., `/stock AAPL`)
- `/crypto [coin]` - Crypto prices (e.g., `/crypto bitcoin`)
- `/market` - Market overview

### Smart Home Commands
- `/lights [action] [room]` - Control lights
- `/scene [name]` - Activate scenes
- `/temp` - Temperature monitoring
- `/home` - Home status overview
- `/areas` - Room management

### Tesla Commands
- `/tesla status` - Vehicle status
- `/climate [action] [temp]` - Climate control
- `/charge [action] [limit]` - Charging control

### Media Commands
- `/download [url]` - YouTube downloads
- `/spotify [action]` - Spotify control
- `/tts [text]` - Text-to-speech

### News Commands
- `/news [category]` - Latest news (tech, science, business)
- `/feeds` - RSS management

### Productivity Commands
- `/note create [title]` - Create notes
- `/note list` - List notes
- `/files` - File management

### Image Commands
- `/sd [prompt]` - Stable Diffusion
- `/edit [prompt]` - Image editing
- `/upscale` - Image upscaling
- `/enhance` - Image enhancement

### Voice Commands
- Send voice messages for automatic transcription
- `/audioinfo` - Audio analysis
- `/effects [options]` - Audio effects

## 🔄 n8n Automation Workflows

The bot includes 8 pre-built n8n workflows for advanced automation:

### Available Workflows
1. **Telegram Activity Logger** - Tracks all bot interactions
2. **AI Usage Monitor** - Monitors AI costs and usage with alerts
3. **System Health Monitor** - Tracks bot performance every 5 minutes
4. **Price Alert Manager** - Automated financial alerts every 15 minutes

### Setup n8n Workflows

1. **Access n8n Dashboard**
   ```
   http://192.168.0.150:5678
   ```

2. **Import Workflows**
   - Go to n8n dashboard
   - Click "Import from file"
   - Import each JSON file from `n8n-workflows/` directory:
     - `telegram-activity-logger.json`
     - `ai-usage-monitor.json`
     - `system-health-monitor.json`
     - `price-alert-manager.json`

3. **Activate Workflows**
   - Enable each imported workflow
   - Configure webhook URLs if needed

### Webhook Endpoints
- **Telegram Activity**: `http://192.168.0.150:5678/webhook/telegram_activity`
- **AI Usage**: `http://192.168.0.150:5678/webhook/ai_usage`
- **Price Alerts**: `http://192.168.0.150:5678/webhook/price_alert`
- **Error Alerts**: `http://192.168.0.150:5678/webhook/error_alert`

## 🐳 Docker Deployment

### Development
```bash
docker-compose up -d
```

### Production with Webhook
```bash
# Set webhook URL
python3 -c "
import asyncio
from bot.core.bot import create_bot
async def set_webhook():
    bot = create_bot()
    await bot.set_webhook('https://yourdomain.com/webhook')
    await bot.session.close()
asyncio.run(set_webhook())
"

# Start with webhook
./start_simple.sh
```

### Unraid Deployment
1. Copy project to Unraid server
2. Configure `.env` file
3. Run: `docker-compose up -d`

## 📊 Monitoring & Analytics

### Built-in Monitoring
- **Prometheus Metrics**: Performance tracking
- **Grafana Dashboards**: Real-time visualization
- **Health Checks**: Automated monitoring
- **Cost Tracking**: AI usage expenses
- **User Analytics**: Command usage patterns

### Access Dashboards
- **Grafana**: `http://localhost:3000` (admin/admin)
- **Prometheus**: `http://localhost:9091`
- **n8n**: `http://192.168.0.150:5678`
- **Bot API**: `http://localhost:8000`

## 🔧 Development

### Project Structure
```
tele/
├── bot/                    # Main bot code
│   ├── core/              # Core functionality (bot, middleware, logging)
│   ├── handlers/          # Command handlers (15 modules)
│   ├── services/          # External service integrations (12 services)
│   └── utils/             # Utilities and helpers
├── n8n-workflows/         # Automation workflows (4 workflows)
├── docker-compose.yml     # Docker configuration
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
└── README.md             # This file
```

### Key Services
- **AI Service**: OpenAI/Anthropic integration
- **Home Assistant**: Smart home control
- **Tesla Service**: Vehicle integration
- **Finance Service**: Stock/crypto data
- **Media Service**: YouTube/Spotify
- **News Service**: RSS/news aggregation
- **Notes Service**: Notion/Drive integration
- **Fun Service**: Entertainment features

### Adding New Features
1. Create handler in `bot/handlers/`
2. Add service integration in `bot/services/`
3. Register handler in `bot/handlers/__init__.py`
4. Add commands to bot with `python3 set_bot_commands.py`
5. Update this README

### Testing
```bash
# Test bot functionality
python3 test_all_commands.py

# Test specific services
python3 debug_commands.py

# Test configuration
python3 final_test.py

# Fix dependencies
python3 fix_dependencies.py
```

## 🔒 Security & Authorization

### Authorization System
- **User Whitelist**: Only authorized users can access (`ALLOWED_USER_IDS`)
- **Rate Limiting**: Prevents abuse and spam
- **Input Validation**: Secure command processing
- **Error Handling**: Graceful failure management

### Security Features
- Environment variable protection
- API key encryption
- Webhook validation
- Command authorization decorators
- Comprehensive logging for audit trails

### Best Practices
- Keep API keys secure in `.env` file
- Use webhook mode for production
- Enable logging for audit trails
- Regular security updates
- Monitor usage patterns

## 🛠 Troubleshooting

### Common Issues

#### Commands Not Working
```bash
# Check authorization
python3 -c "from bot.config import settings; print(f'Allowed users: {settings.allowed_user_ids}')"

# Check handler registration
python3 debug_handlers.py

# Restart bot
python3 start_polling.py
```

#### API Errors
```bash
# Test configuration
python3 final_test.py

# Check API keys
grep -E "(OPENAI|TELEGRAM)" .env
```

#### Performance Issues
```bash
# Monitor resources
docker stats

# Check logs
tail -f logs/bot.log
```

### Getting Help
1. Check bot logs for specific errors
2. Verify API keys and endpoints
3. Test with simple commands first (`/start`, `/help`)
4. Check authorization settings
5. Review n8n workflow status

---

**🚀 Built with ❤️ for the ultimate Telegram bot experience!**

*Transform your Telegram into a powerful AI-driven command center for your digital life.*
