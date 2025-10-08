# n8n Integration Setup Guide for Ultimate Telegram Bot

## 🎯 Overview

This guide will help you set up comprehensive n8n workflows to enhance your Ultimate Telegram Bot with:
- **Activity Logging & Analytics**
- **Smart Home Automation**
- **Price Alert Management**
- **Tesla Command Logging**
- **User Behavior Analytics**
- **System Monitoring**

## 📋 Prerequisites

1. **n8n Instance Running**: `http://192.168.0.150:5678`
2. **PostgreSQL Database** (for logging and analytics)
3. **API Token**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (already configured)
4. **Home Assistant** (optional, for smart home features)

## 🚀 Step 1: Database Setup

### 1.1 Create Database Tables

Connect to your PostgreSQL database and run:

```bash
# Connect to PostgreSQL
psql -h your-postgres-host -U your-username -d your-database

# Run the schema file
\i n8n-workflows/database-schema.sql
```

### 1.2 Verify Tables Created

```sql
-- Check if tables were created
\dt

-- Should show:
-- telegram_activity_log
-- price_alerts
-- tesla_command_log
-- user_activity_log
-- smart_home_log
-- ai_usage_log
-- media_downloads_log
-- user_preferences
-- system_metrics
```

## 🔧 Step 2: n8n Configuration

### 2.1 Import Workflows

1. **Open n8n**: Navigate to `http://192.168.0.150:5678`
2. **Go to Workflows**: Click "Workflows" in the sidebar
3. **Import**: Click "Import from file" or "Import from URL"
4. **Upload**: Select `n8n-workflows/telegram-bot-workflows.json`

### 2.2 Configure Database Credentials

1. **Go to Credentials**: Click "Credentials" in the sidebar
2. **Add New Credential**: Click "Add Credential"
3. **Select PostgreSQL**: Choose "Postgres" from the list
4. **Configure**:
   ```
   Host: your-postgres-host
   Database: your-database-name
   User: your-username
   Password: your-password
   Port: 5432
   SSL: false (or true if using SSL)
   ```
5. **Save**: Name it "PostgreSQL Main"

### 2.3 Configure Environment Variables

Add these environment variables to your n8n instance:

```bash
# Home Assistant (if using)
HOME_ASSISTANT_URL=http://192.168.0.100:8123
HOME_ASSISTANT_TOKEN=your_ha_token_here

# Database
DATABASE_URL=postgresql://user:password@host:5432/database

# API Keys (if needed for price checking)
ALPHA_VANTAGE_API_KEY=your_key_here
COINGECKO_API_KEY=your_key_here
```

## 📡 Step 3: Webhook Endpoints

Your n8n workflows will create these webhook endpoints:

### 3.1 Available Webhooks

| Webhook | URL | Purpose |
|---------|-----|---------|
| `telegram_activity` | `http://192.168.0.150:5678/webhook/telegram_activity` | Log bot commands and responses |
| `smart_home` | `http://192.168.0.150:5678/webhook/smart_home` | Process smart home commands |
| `price_alert` | `http://192.168.0.150:5678/webhook/price_alert` | Create and manage price alerts |
| `tesla_command` | `http://192.168.0.150:5678/webhook/tesla_command` | Log Tesla vehicle commands |
| `user_activity` | `http://192.168.0.150:5678/webhook/user_activity` | Track detailed user behavior |

### 3.2 Test Webhooks

Test each webhook with curl:

```bash
# Test telegram activity webhook
curl -X POST http://192.168.0.150:5678/webhook/telegram_activity \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 123456789,
    "command": "test",
    "success": true,
    "metadata": {"test": true}
  }'

# Test smart home webhook
curl -X POST http://192.168.0.150:5678/webhook/smart_home \
  -H "Content-Type: application/json" \
  -d '{
    "command": "light.turn_on",
    "entity": "light.living_room",
    "value": {"brightness": 255}
  }'
```

## 🔄 Step 4: Bot Integration

Your Telegram bot is already configured to use these webhooks. The integration points are:

### 4.1 Activity Logging
- **File**: `bot/services/n8n.py`
- **Function**: `log_bot_activity()`
- **Triggers**: Every bot command and response

### 4.2 Smart Home Commands
- **File**: `bot/services/n8n.py`
- **Function**: `process_smart_home_command()`
- **Triggers**: Home Assistant API calls

### 4.3 Price Alerts
- **File**: `bot/services/finance.py`
- **Function**: `create_price_alert()`
- **Triggers**: `/stock` and `/crypto` alert creation

## 📊 Step 5: Analytics & Monitoring

### 5.1 Built-in Views

The database schema includes helpful views:

```sql
-- Daily user activity summary
SELECT * FROM daily_user_activity 
WHERE activity_date = CURRENT_DATE;

-- AI usage summary
SELECT * FROM ai_usage_summary 
WHERE usage_date = CURRENT_DATE;

-- Most used commands
SELECT command, COUNT(*) as usage_count
FROM telegram_activity_log 
WHERE timestamp >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY command 
ORDER BY usage_count DESC;
```

### 5.2 Grafana Dashboard (Optional)

Create Grafana dashboards using these queries:

```sql
-- Bot usage over time
SELECT 
  DATE_TRUNC('hour', timestamp) as time,
  COUNT(*) as commands_per_hour
FROM telegram_activity_log 
WHERE timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY time 
ORDER BY time;

-- Success rate
SELECT 
  DATE_TRUNC('hour', timestamp) as time,
  AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) * 100 as success_rate
FROM telegram_activity_log 
WHERE timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY time 
ORDER BY time;
```

## 🔧 Step 6: Advanced Workflows

### 6.1 Price Alert Automation

The workflow includes a cron job that runs every 5 minutes to check price alerts:

1. **Fetches active alerts** from the database
2. **Checks current prices** (you'll need to implement actual price fetching)
3. **Triggers notifications** when conditions are met
4. **Updates alert status** in the database

### 6.2 Smart Home Automation

The smart home webhook can:

1. **Route commands** to Home Assistant
2. **Log all actions** for audit trails
3. **Create custom automations** based on Telegram commands
4. **Send status updates** back to users

### 6.3 User Behavior Analytics

Track detailed user patterns:

```sql
-- Most active users
SELECT 
  user_id,
  COUNT(*) as total_commands,
  COUNT(DISTINCT DATE(timestamp)) as active_days
FROM telegram_activity_log 
GROUP BY user_id 
ORDER BY total_commands DESC;

-- Peak usage hours
SELECT 
  EXTRACT(hour FROM timestamp) as hour,
  COUNT(*) as command_count
FROM telegram_activity_log 
GROUP BY hour 
ORDER BY hour;
```

## 🛠 Step 7: Customization

### 7.1 Add Custom Workflows

Create additional workflows for:

- **Backup automation**
- **Error alerting**
- **Performance monitoring**
- **Custom integrations**

### 7.2 Extend Database Schema

Add custom tables for your specific needs:

```sql
-- Example: Custom automation rules
CREATE TABLE automation_rules (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    trigger_type VARCHAR(50) NOT NULL,
    trigger_conditions JSONB NOT NULL,
    actions JSONB NOT NULL,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🔍 Step 8: Troubleshooting

### 8.1 Common Issues

1. **Webhook not receiving data**:
   - Check n8n workflow is active
   - Verify webhook URL is correct
   - Check network connectivity

2. **Database connection errors**:
   - Verify PostgreSQL credentials
   - Check database permissions
   - Ensure tables exist

3. **Home Assistant integration**:
   - Verify HA URL and token
   - Check entity IDs are correct
   - Ensure HA is accessible from n8n

### 8.2 Debug Commands

```bash
# Check n8n logs
docker logs n8n-container

# Test database connection
psql -h host -U user -d database -c "SELECT NOW();"

# Test webhook manually
curl -X POST http://192.168.0.150:5678/webhook/test \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

## 📈 Step 9: Monitoring & Maintenance

### 9.1 Regular Maintenance

```sql
-- Clean up old logs (run weekly)
SELECT cleanup_old_logs(90); -- Keep 90 days

-- Check database size
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 9.2 Performance Monitoring

Monitor these metrics:
- **Webhook response times**
- **Database query performance**
- **Bot command success rates**
- **User engagement patterns**

## 🎉 Conclusion

Your n8n integration is now set up to provide:

✅ **Comprehensive logging** of all bot activities  
✅ **Smart home automation** through Home Assistant  
✅ **Price alert management** for financial tracking  
✅ **Tesla command logging** for vehicle analytics  
✅ **User behavior analytics** for insights  
✅ **System monitoring** and performance tracking  

The workflows will automatically start processing data as soon as your Telegram bot begins sending webhook requests!

## 🔗 Next Steps

1. **Test all webhooks** with sample data
2. **Configure Grafana dashboards** for visualization
3. **Set up alerting** for system issues
4. **Create custom workflows** for your specific needs
5. **Monitor performance** and optimize as needed

Your Ultimate Telegram Bot now has enterprise-level analytics and automation capabilities! 🚀
