# Ultimate Telegram Bot Setup Guide

## Prerequisites

- Python 3.8+
- Docker and Docker Compose (for production)
- Telegram Bot Token from @BotFather
- Unraid server (for deployment)

## Quick Start

1. **Clone and Setup**
   ```bash
   git clone <your-repo>
   cd tele
   python setup.py
   ```

2. **Configure Environment**
   - Edit `.env` file with your API keys
   - Edit `.env.docker` with secure passwords

3. **Get Telegram Bot Token**
   - Message @BotFather on Telegram
   - Create new bot: `/newbot`
   - Save the token to `.env` file

4. **Run Development Mode**
   ```bash
   python -m bot.main
   ```

## Production Deployment on Unraid

### 1. Unraid Setup

1. Install Community Applications plugin
2. Install Docker Compose Manager plugin
3. Create share for bot data: `/mnt/user/appdata/telebot/`

### 2. Deploy with Docker

```bash
# Copy project to Unraid
scp -r . root@your-unraid-ip:/mnt/user/appdata/telebot/

# SSH to Unraid
ssh root@your-unraid-ip
cd /mnt/user/appdata/telebot/

# Start services
docker-compose up -d
```

### 3. Configure Reverse Proxy

#### Option A: Nginx Proxy Manager
1. Install from Community Applications
2. Add proxy host:
   - Domain: `telebot.yourdomain.com`
   - Forward to: `telebot:8000`
   - Enable SSL with Let's Encrypt

#### Option B: SWAG
1. Install SWAG container
2. Configure subdomain: `telebot`
3. Copy nginx config to SWAG

### 4. Set Webhook

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://telebot.yourdomain.com/webhook"}'
```

## Configuration

### Required API Keys

1. **Telegram Bot Token** (Required)
   - Get from @BotFather
   - Add to `TELEGRAM_BOT_TOKEN` in `.env`

2. **OpenAI API** (Your Local Endpoint)
   - Already configured for `http://192.168.0.150:4000/v1`
   - API key: `sk-KAIMgP6rzU1aRfxeLV6chA`

3. **Anthropic Claude** (Optional)
   - Get from https://console.anthropic.com/
   - Add to `ANTHROPIC_API_KEY` in `.env`

### Optional Integrations

4. **Home Assistant**
   - URL: Your HA instance
   - Token: Long-lived access token

5. **Tesla**
   - Email and refresh token
   - Use Tesla API documentation

6. **Financial APIs**
   - Alpha Vantage: Free tier available
   - TradingView: For webhook alerts

7. **Media APIs**
   - Spotify: Developer app required
   - News API: Free tier available

8. **Productivity**
   - Notion: Integration token
   - Google Drive: Service account

## Security

### User Authorization

Add your Telegram user ID to `ALLOWED_USER_IDS`:

```bash
# Get your user ID
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates"
```

### Webhook Security

- Use HTTPS only
- Set webhook secret
- Validate requests

### API Keys

- Never commit API keys to git
- Use environment variables
- Rotate keys regularly

## Monitoring

### Grafana Dashboards

Access at `http://your-unraid-ip:3000`
- Username: `admin`
- Password: Set in `.env.docker`

### Prometheus Metrics

Available at `/metrics` endpoint:
- Request counts
- Response times
- AI usage
- Error rates

### Logs

- Application logs: `logs/bot.log`
- Docker logs: `docker-compose logs -f`

## Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check webhook URL
   - Verify bot token
   - Check logs

2. **AI not working**
   - Verify OpenAI endpoint
   - Check API key
   - Test connectivity

3. **Database errors**
   - Check PostgreSQL container
   - Verify connection string
   - Check permissions

### Debug Mode

Enable debug logging:
```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
python -m bot.main
```

## Backup

### Automated Backups

Scheduled weekly via cron:
- Database dump
- Configuration files
- User data

### Manual Backup

```bash
# Database
docker-compose exec postgres pg_dump -U telebot telebot > backup.sql

# Files
tar -czf telebot-backup.tar.gz data/ logs/ config/
```

## Updates

### Update Bot

```bash
git pull
docker-compose build
docker-compose up -d
```

### Database Migrations

Handled automatically on startup.

## Support

- Check logs first
- Review configuration
- Test individual components
- Check network connectivity

For detailed feature documentation, see `docs/features.md`.
