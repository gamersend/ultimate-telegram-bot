# n8n Workflows for Ultimate Telegram Bot

This directory contains pre-built n8n workflows for automating various aspects of the Telegram bot.

## Available Workflows

### 1. Telegram Activity Logger (`telegram-activity-logger.json`)
**Purpose**: Tracks all bot interactions and user activities
**Trigger**: Webhook (`/webhook/telegram_activity`)
**Features**:
- Logs all commands and responses
- Tracks user engagement metrics
- Calculates response times
- Categorizes activities

### 2. AI Usage Monitor (`ai-usage-monitor.json`)
**Purpose**: Monitors AI API usage and costs
**Trigger**: Webhook (`/webhook/ai_usage`)
**Features**:
- Tracks token usage per model
- Calculates costs based on model pricing
- Sends alerts for high usage
- Monitors response times

### 3. System Health Monitor (`system-health-monitor.json`)
**Purpose**: Monitors bot system health and performance
**Trigger**: Cron (every 5 minutes)
**Features**:
- Checks memory and CPU usage
- Monitors error rates
- Tracks active users
- Sends health alerts

### 4. Price Alert Manager (`price-alert-manager.json`)
**Purpose**: Manages financial price alerts
**Trigger**: Webhook + Cron (every 15 minutes)
**Features**:
- Processes price alert requests
- Checks current prices against targets
- Sends notifications when triggered
- Manages alert lifecycle

## Setup Instructions

### 1. Access n8n Dashboard
Navigate to your n8n instance:
```
http://192.168.0.150:5678
```

### 2. Import Workflows
1. Click on "Workflows" in the left sidebar
2. Click the "+" button to create a new workflow
3. Click the "..." menu and select "Import from file"
4. Select one of the JSON files from this directory
5. Repeat for each workflow

### 3. Configure Webhooks
After importing, each webhook-triggered workflow will have a unique URL:
- Copy the webhook URL from each workflow
- Configure your bot to send data to these endpoints

### 4. Activate Workflows
1. Open each imported workflow
2. Click the "Active" toggle in the top right
3. Save the workflow

## Webhook Endpoints

Once imported and activated, your workflows will be available at:

```
# Telegram Activity Logger
http://192.168.0.150:5678/webhook/telegram_activity

# AI Usage Monitor  
http://192.168.0.150:5678/webhook/ai_usage

# Price Alert Manager
http://192.168.0.150:5678/webhook/price_alert

# Error Alert System
http://192.168.0.150:5678/webhook/error_alert
```

## Data Flow

### Telegram Activity Logger
```
Bot Command → Webhook → Process Activity → Log to Database
```

### AI Usage Monitor
```
AI Request → Webhook → Calculate Costs → Check Thresholds → Alert if High
```

### System Health Monitor
```
Cron Trigger → Check Metrics → Evaluate Health → Alert if Issues
```

### Price Alert Manager
```
Alert Request → Webhook → Store Alert
Cron Trigger → Check Prices → Compare → Notify if Triggered
```

## Customization

### Modifying Workflows
1. Open the workflow in n8n
2. Click on any node to edit its configuration
3. Modify the JavaScript code in Function nodes
4. Adjust cron schedules in Cron nodes
5. Save and test the workflow

### Adding New Workflows
1. Create a new workflow in n8n
2. Add appropriate trigger nodes (Webhook, Cron, etc.)
3. Add processing logic with Function nodes
4. Configure output actions (Database, Notifications, etc.)
5. Export and save to this directory

## Monitoring

### Workflow Execution
- Check the "Executions" tab in n8n to see workflow runs
- Monitor for failed executions
- Review execution logs for debugging

### Performance
- Monitor webhook response times
- Check for failed webhook calls
- Ensure cron jobs are running on schedule

## Troubleshooting

### Common Issues

#### Webhook Not Receiving Data
1. Check if workflow is active
2. Verify webhook URL is correct
3. Check bot configuration for webhook endpoints
4. Review n8n logs for errors

#### Cron Jobs Not Running
1. Verify cron expression syntax
2. Check if workflow is active
3. Review execution history
4. Check n8n system time

#### Function Node Errors
1. Check JavaScript syntax in Function nodes
2. Verify input data structure
3. Add console.log statements for debugging
4. Test with sample data

### Getting Help
1. Check n8n documentation: https://docs.n8n.io/
2. Review workflow execution logs
3. Test individual nodes
4. Check bot logs for webhook calls

## Security Notes

- Webhook endpoints are public by default
- Consider adding authentication if needed
- Monitor for unusual webhook activity
- Keep n8n instance updated

## Future Enhancements

Potential additional workflows:
- User behavior analytics
- Automated backup system
- Performance optimization alerts
- Integration with external monitoring tools
- Custom notification channels
- Advanced reporting dashboards
