# 🤖 Ultimate Telegram Bot

> **The most comprehensive personal AI assistant bot for Telegram with enterprise-level features**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![n8n Compatible](https://img.shields.io/badge/n8n-automation-green.svg)](https://n8n.io/)

## 📑 Table of Contents

- [Features Overview](#-features-overview)
- [Quick Start](#-quick-start)
- [Installation Guide](#-installation-guide-expanded-section)
- [Configuration](#configuration)
- [Available Commands](#-available-commands-33-total)
- [Architecture](#-architecture-overview-expanded-section)
- [Development](#-development)
- [Deployment](#-docker-deployment)
- [Monitoring](#-monitoring--analytics)
- [Security](#-security--authorization)
- [Troubleshooting](#-troubleshooting)
- [API Reference](#-api-endpoints-expanded-section)
- [Contributing](#-contributing-expanded-section)
- [License](#-license-expanded-section)

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
   cd ultimate-telegram-bot
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

## 📦 Installation Guide *(Expanded Section)*

### System Requirements

**Minimum:**
- CPU: 2 cores
- RAM: 2GB
- Storage: 5GB
- OS: Linux, macOS, or Windows (WSL2)
- Python: 3.11 or higher

**Recommended:**
- CPU: 4 cores
- RAM: 4GB+
- Storage: 10GB+
- SSD for database performance

### Step-by-Step Installation

#### 1. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip git ffmpeg postgresql redis-server
```

**macOS:**
```bash
brew install python@3.11 ffmpeg postgresql redis git
```

**Windows (WSL2):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip git ffmpeg
```

#### 2. Clone Repository

```bash
git clone https://github.com/yourusername/ultimate-telegram-bot.git
cd ultimate-telegram-bot
```

#### 3. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

#### 4. Install Python Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Or use the dependency fixer
python3 fix_dependencies.py
```

#### 5. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit with your favorite editor
nano .env  # or vim, code, etc.
```

See [Complete Environment Variables Reference](#complete-environment-variables-reference-expanded-section) for all options.

#### 6. Initialize Database

```bash
# For SQLite (default, no setup needed)
mkdir -p data

# For PostgreSQL (optional, better for production)
# 1. Create database
createdb telebot

# 2. Update DATABASE_URL in .env
# DATABASE_URL=postgresql://user:password@localhost:5432/telebot
```

#### 7. Get Your Telegram User ID

```bash
# Start the bot temporarily
python3 start_polling.py

# Send any message to your bot
# Check logs for your user ID, or use:
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates"
```

Add your user ID to `ALLOWED_USER_IDS` in `.env`

#### 8. Run Initial Setup

```bash
# Register bot commands with Telegram
python3 set_bot_commands.py

# Test configuration
python3 test_config.sh
```

#### 9. Start the Bot

```bash
# Development (polling mode)
python3 start_polling.py

# Production (webhook mode)
python3 bot/main.py
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

### Complete Environment Variables Reference *(Expanded Section)*

#### Telegram Configuration
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | - | Your Telegram bot token from @BotFather |
| `TELEGRAM_WEBHOOK_URL` | No | - | Webhook URL for production (e.g., https://yourdomain.com/webhook) |
| `TELEGRAM_WEBHOOK_SECRET` | No | - | Secret token for webhook validation |
| `ALLOWED_USER_IDS` | Yes | - | Comma-separated list of authorized Telegram user IDs |

#### AI Configuration
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key or local endpoint key |
| `OPENAI_BASE_URL` | No | https://api.openai.com/v1 | API endpoint (supports local LiteLLM proxy) |
| `ANTHROPIC_API_KEY` | No | - | Anthropic Claude API key (optional) |

#### Database Configuration
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | No | sqlite:///./data/telebot.db | Database connection string |
| `REDIS_URL` | No | redis://localhost:6379/0 | Redis connection for caching |

#### Smart Home Integration
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `HOME_ASSISTANT_URL` | No | - | Home Assistant instance URL |
| `HOME_ASSISTANT_TOKEN` | No | - | Long-lived access token |

#### Tesla Integration
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TESLA_EMAIL` | No | - | Tesla account email |
| `TESLA_REFRESH_TOKEN` | No | - | Tesla API refresh token |

#### Financial APIs
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ALPHA_VANTAGE_API_KEY` | No | - | Alpha Vantage API for advanced stock data |
| `TRADINGVIEW_WEBHOOK_SECRET` | No | - | TradingView webhook secret for alerts |

#### Media APIs
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SPOTIFY_CLIENT_ID` | No | - | Spotify app client ID |
| `SPOTIFY_CLIENT_SECRET` | No | - | Spotify app client secret |
| `SPOTIFY_REDIRECT_URI` | No | http://localhost:8000/callback/spotify | OAuth redirect URI |

#### News & Entertainment
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEWS_API_KEY` | No | - | NewsAPI.org API key |
| `IMGFLIP_USERNAME` | No | - | Imgflip username for meme generation |
| `IMGFLIP_PASSWORD` | No | - | Imgflip password |
| `TENOR_API_KEY` | No | - | Tenor GIF API key |
| `GIPHY_API_KEY` | No | - | Giphy API key |

#### Productivity
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NOTION_TOKEN` | No | - | Notion integration token |
| `GOOGLE_CREDENTIALS_FILE` | No | - | Path to Google service account JSON |

#### n8n Integration
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `N8N_URL` | No | - | n8n instance URL |
| `N8N_TOKEN` | No | - | n8n API authentication token |

#### Security
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `JWT_SECRET_KEY` | No | your-secret-key-change-this | JWT signing key (change in production!) |
| `WEBHOOK_SECRET` | No | your-webhook-secret | Webhook validation secret |

#### Monitoring
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PROMETHEUS_PORT` | No | 9090 | Prometheus metrics port |
| `GRAFANA_PORT` | No | 3000 | Grafana dashboard port |

#### Application Settings
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DEBUG` | No | false | Enable debug mode |
| `LOG_LEVEL` | No | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `ENVIRONMENT` | No | development | Environment name |
| `HOST` | No | 0.0.0.0 | Server host address |
| `PORT` | No | 8000 | Server port |

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

## 🏗 Architecture Overview *(Expanded Section)*

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Telegram Bot API                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Webhook/Polling
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Application                       │
│  ┌────────────┬─────────────┬──────────────┬─────────────┐ │
│  │ Middleware │  Handlers   │   Services   │   Utils     │ │
│  └────────────┴─────────────┴──────────────┴─────────────┘ │
└───────────┬─────────────┬──────────────┬───────────────────┘
            │             │              │
            ▼             ▼              ▼
    ┌──────────┐   ┌──────────┐  ┌──────────────┐
    │PostgreSQL│   │  Redis   │  │ External APIs│
    │/SQLite   │   │  Cache   │  │ (AI, HA, etc)│
    └──────────┘   └──────────┘  └──────────────┘
            │             │              │
            ▼             ▼              ▼
    ┌──────────────────────────────────────┐
    │         Monitoring Stack             │
    │   Prometheus │ Grafana │ n8n        │
    └──────────────────────────────────────┘
```

### Core Components

#### 1. Bot Core (`bot/core/`)
- **bot.py**: Bot and dispatcher creation
- **database.py**: SQLAlchemy models and async database management
- **logging.py**: Structured logging with structlog
- **middleware.py**: Request processing pipeline

#### 2. Handlers (`bot/handlers/`)
The bot includes 13 specialized handler modules:

| Handler | File | Purpose | Commands |
|---------|------|---------|----------|
| Basic | `basic.py` | Core bot commands | /start, /help, /status |
| AI | `ai.py` | AI chat and processing | /ask, /explain, /code, /summarize |
| Voice | `voice.py` | Audio processing | Voice message handling, /tts |
| Image | `image.py` | Image generation/editing | /generate, /edit, /upscale, /sd |
| Smart Home | `smart_home.py` | Home Assistant control | /lights, /scene, /temp, /home |
| Tesla | `tesla.py` | Vehicle control | /tesla, /climate, /charge |
| Finance | `finance.py` | Market data | /stock, /crypto, /market |
| Media | `media.py` | Media downloads/control | /download, /spotify |
| News | `news.py` | News aggregation | /news, /feeds |
| Notes | `notes.py` | Note management | /note, /files |
| Fun | `fun.py` | Entertainment | /meme, /joke, /fact, /trivia, /gif |
| Admin | `admin.py` | Administrative functions | System management |

#### 3. Services (`bot/services/`)
12 service integrations providing external functionality:

| Service | File | Purpose |
|---------|------|---------|
| AI | `ai.py` | OpenAI & Anthropic integration |
| Audio | `audio.py` | Whisper transcription & TTS |
| Image Gen | `image_generation.py` | DALL-E & Stable Diffusion |
| Home Assistant | `home_assistant.py` | Smart home REST API |
| Tesla | `tesla.py` | TeslaPy vehicle control |
| Finance | `finance.py` | yfinance & pycoingecko |
| Media | `media.py` | yt-dlp & Spotipy |
| News | `news.py` | NewsAPI & feedparser |
| Notes | `notes.py` | Notion & Google Drive |
| Fun | `fun.py` | Reddit, Giphy, trivia APIs |
| Scheduler | `scheduler.py` | APScheduler task scheduling |
| n8n | `n8n.py` | Workflow automation webhooks |

#### 4. Middleware Pipeline

The bot uses a middleware pipeline for request processing:

```python
Request → AuthMiddleware → LoggingMiddleware → RateLimitMiddleware → Handler
```

- **AuthMiddleware**: Validates user against whitelist
- **LoggingMiddleware**: Records all interactions and metrics
- **RateLimitMiddleware**: Prevents abuse (10 requests/minute per user)

#### 5. Database Schema

**Users Table:**
- Stores user preferences and settings
- Tracks user activity and permissions

**ChatHistory Table:**
- Maintains conversation context
- Enables AI memory across sessions

**UserSessions Table:**
- Manages temporary session data
- Handles OAuth flows

#### 6. Scheduled Tasks

The bot runs automated tasks via APScheduler:

| Task | Schedule | Purpose |
|------|----------|---------|
| Market Open Alert | Weekdays 9:30 AM EST | Stock market notifications |
| Portfolio Update | Weekdays 6:00 PM EST | Daily portfolio summary |
| News Digest | Daily 8:00 AM | Curated news summary |
| Data Backup | Sundays 2:00 AM | Automated backups |

### Deployment Modes

#### Polling Mode (Development)
```bash
python3 start_polling.py
```
- Long-polling connection to Telegram
- No webhook configuration needed
- Easier for local development
- Higher latency

#### Webhook Mode (Production)
```bash
python3 bot/main.py
```
- FastAPI server on port 8000
- Receives push notifications from Telegram
- Lower latency
- Requires HTTPS endpoint
- Production-ready

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

### Docker Compose Services

The `docker-compose.yml` file includes the following services:

| Service | Port | Purpose |
|---------|------|---------|
| telebot | 8000 | Main bot application |
| postgres | 5432 | PostgreSQL database |
| redis | 6379 | Cache and session store |
| prometheus | 9091 | Metrics collection |
| grafana | 3000 | Monitoring dashboards |
| nginx | 80, 443 | Reverse proxy with SSL |

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

### Available Metrics

The bot exposes Prometheus metrics at `/metrics`:

- `telegram_bot_requests_total` - Total requests processed
- `telegram_bot_request_duration_seconds` - Request latency
- `telegram_bot_active_users` - Current active users
- `telegram_bot_commands_total{command}` - Commands by type
- `telegram_bot_errors_total{error_type}` - Error counts
- `telegram_bot_ai_requests_total{provider}` - AI API calls
- `telegram_bot_ai_tokens_total{provider,type}` - Token usage
- `telegram_bot_ai_cost_total{provider}` - AI costs in USD

## 🔧 Development

### Project Structure
```
ultimate-telegram-bot/
├── bot/                    # Main bot code
│   ├── core/              # Core functionality
│   │   ├── bot.py         # Bot instance creation
│   │   ├── database.py    # Database models & connection
│   │   ├── logging.py     # Logging configuration
│   │   └── middleware.py  # Request middleware
│   ├── handlers/          # Command handlers (13 modules)
│   │   ├── __init__.py    # Handler registration
│   │   ├── basic.py       # /start, /help, /status
│   │   ├── ai.py          # AI commands
│   │   ├── voice.py       # Voice processing
│   │   ├── image.py       # Image generation
│   │   ├── smart_home.py  # Home Assistant
│   │   ├── tesla.py       # Tesla control
│   │   ├── finance.py     # Market data
│   │   ├── media.py       # Media downloads
│   │   ├── news.py        # News aggregation
│   │   ├── notes.py       # Note management
│   │   ├── fun.py         # Entertainment
│   │   └── admin.py       # Admin commands
│   ├── services/          # External service integrations (12 services)
│   │   ├── ai.py          # OpenAI/Anthropic
│   │   ├── audio.py       # Whisper/TTS
│   │   ├── image_generation.py  # DALL-E/SD
│   │   ├── home_assistant.py    # Smart home
│   │   ├── tesla.py       # Vehicle API
│   │   ├── finance.py     # Stock/crypto
│   │   ├── media.py       # YouTube/Spotify
│   │   ├── news.py        # RSS/News
│   │   ├── notes.py       # Notion/Drive
│   │   ├── fun.py         # Entertainment APIs
│   │   ├── scheduler.py   # Task scheduling
│   │   └── n8n.py         # Workflow automation
│   ├── utils/             # Utilities and helpers
│   │   ├── decorators.py  # Auth/logging decorators
│   │   └── metrics.py     # Prometheus metrics
│   ├── config.py          # Configuration management
│   └── main.py            # Application entry point
├── n8n-workflows/         # Automation workflows
│   ├── telegram-activity-logger.json
│   ├── ai-usage-monitor.json
│   ├── system-health-monitor.json
│   └── price-alert-manager.json
├── monitoring/            # Monitoring configs
│   ├── prometheus.yml
│   └── grafana/
├── nginx/                 # Nginx configuration
│   └── nginx.conf
├── docs/                  # Documentation
│   ├── features.md        # Feature documentation
│   └── setup.md           # Setup guide
├── logs/                  # Application logs
├── data/                  # SQLite database (default)
├── docker-compose.yml     # Docker orchestration
├── Dockerfile             # Container definition
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── .env                  # Your configuration (not in git)
├── .gitignore            # Git ignore rules
├── start_polling.py       # Polling mode starter
├── set_bot_commands.py    # Register commands
├── fix_dependencies.py    # Dependency fixer
├── deploy.sh             # Deployment script
├── run.sh                # Run script
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

#### 1. Create a New Handler

```python
# bot/handlers/myfeature.py
from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from bot.utils.decorators import authorized_only

@authorized_only
async def my_command(message: Message):
    """Handle /mycommand"""
    await message.answer("Hello from my feature!")

def register_handlers(dp: Dispatcher):
    """Register handlers"""
    dp.message.register(my_command, Command("mycommand"))
```

#### 2. Create a Service Integration

```python
# bot/services/myservice.py
import logging
from bot.config import settings

logger = logging.getLogger(__name__)

class MyService:
    """Service for my feature"""

    def __init__(self):
        self.api_key = settings.my_api_key

    async def do_something(self):
        """Do something useful"""
        pass

my_service = MyService()
```

#### 3. Register the Handler

```python
# bot/handlers/__init__.py
from bot.handlers import myfeature

def register_handlers(dp: Dispatcher):
    # ... existing handlers ...
    myfeature.register_handlers(dp)
```

#### 4. Update Bot Commands

```bash
python3 set_bot_commands.py
```

#### 5. Update Documentation

Add your feature to this README and `docs/features.md`

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
- **Rate Limiting**: Prevents abuse and spam (10 requests/minute per user)
- **Input Validation**: Secure command processing
- **Error Handling**: Graceful failure management

### Security Features
- Environment variable protection
- API key encryption
- Webhook validation with secret tokens
- Command authorization decorators
- Comprehensive logging for audit trails

### Best Practices
- Keep API keys secure in `.env` file (never commit!)
- Use webhook mode with HTTPS for production
- Enable logging for audit trails
- Regular security updates
- Monitor usage patterns for anomalies
- Rotate API keys periodically
- Use strong webhook secrets

### Authorization Decorators

```python
from bot.utils.decorators import authorized_only, admin_only, log_command

@authorized_only  # Checks against ALLOWED_USER_IDS
@log_command      # Logs command execution
async def my_command(message: Message):
    pass

@admin_only       # Only first user in ALLOWED_USER_IDS
async def admin_command(message: Message):
    pass
```

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

#### Database Connection Errors

**SQLite (default):**
```bash
# Check if data directory exists
ls -la data/

# Check file permissions
chmod 755 data/
```

**PostgreSQL:**
```bash
# Test connection
psql postgresql://user:password@localhost:5432/telebot

# Check if database exists
docker-compose exec postgres psql -U telebot -l
```

#### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or use the fixer
python3 fix_dependencies.py
```

### Known Issues & Fixes *(Expanded Section)*

Based on the comprehensive audit performed on this codebase:

#### 1. Missing Dependencies (FIXED)
- **Issue**: `asyncpg` and `aiosqlite` were missing
- **Fix**: Added to `requirements.txt`
- **Impact**: Database connections now work correctly

#### 2. Database URL Conversion Bug (FIXED)
- **Issue**: SQLite URLs would crash the bot
- **Fix**: Updated `bot/core/database.py` to handle both PostgreSQL and SQLite
- **Impact**: Both database types now work seamlessly

#### 3. Hardcoded Credentials (FIXED)
- **Issue**: API keys were hardcoded in `config.py`
- **Fix**: Removed hardcoded values, made them optional
- **Impact**: Improved security, no credentials in code

#### 4. Pydantic v2 Compatibility (FIXED)
- **Issue**: Using deprecated Pydantic v1 `Config` class
- **Fix**: Updated to Pydantic v2 `model_config`
- **Impact**: Compatible with Pydantic 2.5.0+

#### 5. N8N Service Crash (FIXED)
- **Issue**: Bot would crash if n8n not configured
- **Fix**: Added graceful degradation in `bot/services/n8n.py`
- **Impact**: Bot runs without n8n integration

#### 6. Empty User List Handling (FIXED)
- **Issue**: `admin_only` decorator would cause IndexError
- **Fix**: Added proper empty list checking
- **Impact**: Safe handling of missing configuration

See `FIXES_AND_IMPROVEMENTS.md` for complete details.

### Getting Help
1. Check bot logs for specific errors: `tail -f logs/bot.log`
2. Verify API keys and endpoints in `.env`
3. Test with simple commands first (`/start`, `/help`)
4. Check authorization settings (`ALLOWED_USER_IDS`)
5. Review n8n workflow status (if using n8n)
6. Check the [documentation](docs/)
7. Review [known issues](#known-issues--fixes-expanded-section)

## 📚 API Endpoints *(Expanded Section)*

When running in webhook mode, the bot exposes several HTTP endpoints:

### Health & Status

**GET `/health`**
- **Description**: Health check endpoint
- **Response**: `{"status": "healthy", "mode": "webhook"}`
- **Use**: Monitoring and uptime checks

**GET `/status`**
- **Description**: Detailed bot status
- **Response**: System metrics, uptime, service status
- **Authentication**: None required

### Metrics

**GET `/metrics`**
- **Description**: Prometheus metrics endpoint
- **Format**: Prometheus text format
- **Use**: Scraping by Prometheus for monitoring

### Webhooks

**POST `/webhook`**
- **Description**: Telegram webhook endpoint
- **Authentication**: Secret token in header
- **Body**: Telegram Update object
- **Use**: Receives updates from Telegram

### Callbacks

**GET `/callback/spotify`**
- **Description**: Spotify OAuth callback
- **Parameters**: `code`, `state`
- **Use**: OAuth flow completion

## 🤝 Contributing *(Expanded Section)*

Contributions are welcome! Here's how you can help:

### Ways to Contribute

1. **Report Bugs**: Open an issue with details and reproduction steps
2. **Suggest Features**: Propose new features or improvements
3. **Submit Pull Requests**: Fix bugs or implement features
4. **Improve Documentation**: Help make the docs better
5. **Share Ideas**: Discuss architecture and design decisions

### Development Setup

```bash
# Fork and clone
git clone https://github.com/yourusername/ultimate-telegram-bot.git
cd ultimate-telegram-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create feature branch
git checkout -b feature/my-feature

# Make changes and test
python3 start_polling.py

# Commit and push
git add .
git commit -m "Add my feature"
git push origin feature/my-feature
```

### Code Standards

- Follow PEP 8 style guide
- Use type hints where possible
- Add docstrings to all functions
- Write tests for new features
- Keep handlers focused and simple
- Use async/await consistently
- Log important events

### Pull Request Process

1. Update documentation for new features
2. Add tests if applicable
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Request review from maintainers

## 📄 License *(Expanded Section)*

This project is licensed under the MIT License.

### MIT License

```
MIT License

Copyright (c) 2024 Ultimate Telegram Bot Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### Third-Party Licenses

This project uses several open-source libraries. See their respective licenses:

- **aiogram** - BSD 3-Clause License
- **FastAPI** - MIT License
- **SQLAlchemy** - MIT License
- **OpenAI Python Client** - Apache 2.0 License
- **Anthropic Python SDK** - Apache 2.0 License

## 📖 Additional Documentation

- **[Feature Documentation](docs/features.md)** - Detailed feature specifications and roadmap
- **[Setup Guide](docs/setup.md)** - Comprehensive setup and deployment guide
- **[Fixes & Improvements](FIXES_AND_IMPROVEMENTS.md)** - Recent bug fixes and improvements

## 🔄 Backup & Recovery *(Expanded Section)*

### Automated Backups

The bot includes automated backup functionality via APScheduler:

```python
# Runs every Sunday at 2:00 AM
# Backs up: database, configuration, user data
```

### Manual Backup

**SQLite Database:**
```bash
# Backup database
cp data/telebot.db backups/telebot-$(date +%Y%m%d).db

# Restore database
cp backups/telebot-20240112.db data/telebot.db
```

**PostgreSQL Database:**
```bash
# Backup
docker-compose exec postgres pg_dump -U telebot telebot > backup.sql

# Restore
docker-compose exec -T postgres psql -U telebot telebot < backup.sql
```

**Configuration & Logs:**
```bash
# Create full backup
tar -czf telebot-backup-$(date +%Y%m%d).tar.gz \
    .env data/ logs/ n8n-workflows/

# Restore
tar -xzf telebot-backup-20240112.tar.gz
```

### Backup Schedule

| Component | Frequency | Retention | Location |
|-----------|-----------|-----------|----------|
| Database | Weekly | 4 weeks | `backups/` |
| Logs | Daily | 7 days | `logs/` |
| Config | On change | Forever | `.env` |
| User Data | Weekly | 4 weeks | `data/` |

## 🎯 Performance Tuning *(Expanded Section)*

### Optimization Tips

#### 1. Database Optimization

**Use PostgreSQL for Production:**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/telebot
```

**Enable Connection Pooling:**
```python
# Already configured in bot/core/database.py
# AsyncSessionLocal handles connection pooling
```

#### 2. Redis Caching

Enable Redis for better performance:
```env
REDIS_URL=redis://localhost:6379/0
```

#### 3. Rate Limiting

Adjust rate limits in `bot/core/middleware.py`:
```python
# Default: 10 requests per minute
RateLimitMiddleware(rate_limit=20)  # Increase to 20
```

#### 4. Resource Limits

**Docker Compose:**
```yaml
services:
  telebot:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

#### 5. Async Operations

All I/O operations are async - keep it that way!
- Never use `time.sleep()` - use `asyncio.sleep()`
- Always use async database sessions
- Use `httpx.AsyncClient` for HTTP requests

### Performance Benchmarks

Expected performance metrics:

| Metric | Target | Typical |
|--------|--------|---------|
| Response Time | <500ms | ~200ms |
| Commands/sec | 10+ | ~15 |
| AI Requests | <3s | ~1-2s |
| Memory Usage | <500MB | ~300MB |
| CPU Usage | <50% | ~20% |

---

## 🎉 What's New

### Recent Updates

- ✅ Fixed database URL handling for SQLite and PostgreSQL
- ✅ Added missing async database dependencies
- ✅ Removed hardcoded credentials for better security
- ✅ Updated Pydantic v2 compatibility
- ✅ Added graceful degradation for optional services
- ✅ Improved error handling in decorators
- ✅ Created required directories (logs/, data/)
- ✅ Comprehensive documentation updates

### Coming Soon

- 🔄 Advanced AI conversation memory
- 🔄 Multi-language support
- 🔄 Custom command aliases
- 🔄 Enhanced media processing
- 🔄 Mobile app integration
- 🔄 Voice command support
- 🔄 Advanced scheduling features

---

**🚀 Built with ❤️ for the ultimate Telegram bot experience!**

*Transform your Telegram into a powerful AI-driven command center for your digital life.*

---

**Project Status**: ✅ Production Ready | **Version**: 1.0.0 | **Last Updated**: 2024-11-12
