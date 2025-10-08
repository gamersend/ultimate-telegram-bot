-- Database Schema for Ultimate Telegram Bot n8n Integration
-- Run this in your PostgreSQL database to create the required tables

-- Telegram Activity Log Table
CREATE TABLE IF NOT EXISTS telegram_activity_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    user_id BIGINT NOT NULL,
    command VARCHAR(100),
    success BOOLEAN NOT NULL DEFAULT false,
    metadata JSONB DEFAULT '{}',
    category VARCHAR(50),
    response_time INTEGER DEFAULT 0, -- milliseconds
    tokens_used INTEGER DEFAULT 0,
    cost_usd DECIMAL(10,6) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_telegram_activity_user_id ON telegram_activity_log(user_id);
CREATE INDEX IF NOT EXISTS idx_telegram_activity_timestamp ON telegram_activity_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_telegram_activity_command ON telegram_activity_log(command);
CREATE INDEX IF NOT EXISTS idx_telegram_activity_success ON telegram_activity_log(success);

-- Price Alerts Table
CREATE TABLE IF NOT EXISTS price_alerts (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    target_price DECIMAL(15,6) NOT NULL,
    condition VARCHAR(10) NOT NULL CHECK (condition IN ('above', 'below')),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    active BOOLEAN NOT NULL DEFAULT true,
    triggered BOOLEAN NOT NULL DEFAULT false,
    triggered_at TIMESTAMP WITH TIME ZONE,
    current_price DECIMAL(15,6),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for price alerts
CREATE INDEX IF NOT EXISTS idx_price_alerts_user_id ON price_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_price_alerts_symbol ON price_alerts(symbol);
CREATE INDEX IF NOT EXISTS idx_price_alerts_active ON price_alerts(active);
CREATE INDEX IF NOT EXISTS idx_price_alerts_triggered ON price_alerts(triggered);

-- Tesla Command Log Table
CREATE TABLE IF NOT EXISTS tesla_command_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    vehicle_id BIGINT,
    command VARCHAR(100) NOT NULL,
    result JSONB DEFAULT '{}',
    user_source VARCHAR(50) DEFAULT 'telegram_bot',
    success BOOLEAN,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for Tesla logs
CREATE INDEX IF NOT EXISTS idx_tesla_log_vehicle_id ON tesla_command_log(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_tesla_log_command ON tesla_command_log(command);
CREATE INDEX IF NOT EXISTS idx_tesla_log_timestamp ON tesla_command_log(timestamp);

-- User Activity Log Table (for detailed analytics)
CREATE TABLE IF NOT EXISTS user_activity_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    user_id BIGINT NOT NULL,
    activity_type VARCHAR(100) NOT NULL,
    metadata JSONB DEFAULT '{}',
    session_id VARCHAR(100),
    ip_address INET,
    user_agent TEXT,
    hour_of_day INTEGER,
    day_of_week INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for user activity
CREATE INDEX IF NOT EXISTS idx_user_activity_user_id ON user_activity_log(user_id);
CREATE INDEX IF NOT EXISTS idx_user_activity_type ON user_activity_log(activity_type);
CREATE INDEX IF NOT EXISTS idx_user_activity_timestamp ON user_activity_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_user_activity_hour ON user_activity_log(hour_of_day);
CREATE INDEX IF NOT EXISTS idx_user_activity_day ON user_activity_log(day_of_week);

-- Smart Home Command Log Table
CREATE TABLE IF NOT EXISTS smart_home_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    user_id BIGINT,
    domain VARCHAR(50) NOT NULL,
    service VARCHAR(50) NOT NULL,
    entity_id VARCHAR(200) NOT NULL,
    service_data JSONB DEFAULT '{}',
    success BOOLEAN,
    response JSONB DEFAULT '{}',
    source VARCHAR(50) DEFAULT 'telegram_bot',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for smart home logs
CREATE INDEX IF NOT EXISTS idx_smart_home_user_id ON smart_home_log(user_id);
CREATE INDEX IF NOT EXISTS idx_smart_home_domain ON smart_home_log(domain);
CREATE INDEX IF NOT EXISTS idx_smart_home_entity ON smart_home_log(entity_id);
CREATE INDEX IF NOT EXISTS idx_smart_home_timestamp ON smart_home_log(timestamp);

-- AI Usage Log Table
CREATE TABLE IF NOT EXISTS ai_usage_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    user_id BIGINT NOT NULL,
    provider VARCHAR(50) NOT NULL, -- 'openai', 'anthropic', etc.
    model VARCHAR(100),
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    cost_usd DECIMAL(10,6) DEFAULT 0.00,
    request_type VARCHAR(50), -- 'chat', 'image', 'audio', etc.
    success BOOLEAN NOT NULL DEFAULT true,
    error_message TEXT,
    response_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for AI usage
CREATE INDEX IF NOT EXISTS idx_ai_usage_user_id ON ai_usage_log(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_usage_provider ON ai_usage_log(provider);
CREATE INDEX IF NOT EXISTS idx_ai_usage_timestamp ON ai_usage_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_ai_usage_request_type ON ai_usage_log(request_type);

-- Media Downloads Log Table
CREATE TABLE IF NOT EXISTS media_downloads_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    user_id BIGINT NOT NULL,
    url TEXT NOT NULL,
    title TEXT,
    duration_seconds INTEGER,
    file_size_bytes BIGINT,
    format VARCHAR(20),
    audio_only BOOLEAN DEFAULT false,
    success BOOLEAN NOT NULL DEFAULT true,
    error_message TEXT,
    download_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for media downloads
CREATE INDEX IF NOT EXISTS idx_media_downloads_user_id ON media_downloads_log(user_id);
CREATE INDEX IF NOT EXISTS idx_media_downloads_timestamp ON media_downloads_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_media_downloads_success ON media_downloads_log(success);

-- User Preferences Table
CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE,
    telegram_username VARCHAR(100),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    language_code VARCHAR(10) DEFAULT 'en',
    timezone VARCHAR(50) DEFAULT 'UTC',
    preferences JSONB DEFAULT '{}',
    ai_provider_preference VARCHAR(50) DEFAULT 'openai',
    voice_preference VARCHAR(50) DEFAULT 'alloy',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for user preferences
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);

-- System Metrics Table
CREATE TABLE IF NOT EXISTS system_metrics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,6) NOT NULL,
    metric_unit VARCHAR(20),
    tags JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for system metrics
CREATE INDEX IF NOT EXISTS idx_system_metrics_name ON system_metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics(timestamp);

-- Create a view for daily user activity summary
CREATE OR REPLACE VIEW daily_user_activity AS
SELECT 
    DATE(timestamp) as activity_date,
    user_id,
    COUNT(*) as total_commands,
    COUNT(CASE WHEN success THEN 1 END) as successful_commands,
    COUNT(CASE WHEN NOT success THEN 1 END) as failed_commands,
    ROUND(AVG(response_time), 2) as avg_response_time_ms,
    SUM(tokens_used) as total_tokens,
    SUM(cost_usd) as total_cost_usd,
    ARRAY_AGG(DISTINCT command) as commands_used
FROM telegram_activity_log
GROUP BY DATE(timestamp), user_id
ORDER BY activity_date DESC, user_id;

-- Create a view for AI usage summary
CREATE OR REPLACE VIEW ai_usage_summary AS
SELECT 
    DATE(timestamp) as usage_date,
    provider,
    model,
    COUNT(*) as total_requests,
    SUM(prompt_tokens) as total_prompt_tokens,
    SUM(completion_tokens) as total_completion_tokens,
    SUM(total_tokens) as total_tokens,
    SUM(cost_usd) as total_cost_usd,
    ROUND(AVG(response_time_ms), 2) as avg_response_time_ms,
    COUNT(CASE WHEN success THEN 1 END) as successful_requests,
    COUNT(CASE WHEN NOT success THEN 1 END) as failed_requests
FROM ai_usage_log
GROUP BY DATE(timestamp), provider, model
ORDER BY usage_date DESC, provider, model;

-- Create a function to clean up old logs (optional)
CREATE OR REPLACE FUNCTION cleanup_old_logs(days_to_keep INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER := 0;
    cutoff_date TIMESTAMP WITH TIME ZONE;
BEGIN
    cutoff_date := NOW() - INTERVAL '1 day' * days_to_keep;
    
    -- Clean up old activity logs
    DELETE FROM telegram_activity_log WHERE created_at < cutoff_date;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Clean up old user activity logs
    DELETE FROM user_activity_log WHERE created_at < cutoff_date;
    
    -- Clean up old media download logs
    DELETE FROM media_downloads_log WHERE created_at < cutoff_date;
    
    -- Clean up old system metrics (keep longer - 1 year)
    DELETE FROM system_metrics WHERE created_at < (NOW() - INTERVAL '365 days');
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Create a trigger to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply the trigger to user_preferences
CREATE TRIGGER update_user_preferences_updated_at
    BEFORE UPDATE ON user_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Apply the trigger to price_alerts
CREATE TRIGGER update_price_alerts_updated_at
    BEFORE UPDATE ON price_alerts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert some sample data for testing (optional)
-- INSERT INTO user_preferences (user_id, telegram_username, first_name, preferences) 
-- VALUES (123456789, 'testuser', 'Test User', '{"theme": "dark", "notifications": true}');

COMMENT ON TABLE telegram_activity_log IS 'Logs all Telegram bot command activity and responses';
COMMENT ON TABLE price_alerts IS 'Stores user-created price alerts for stocks and crypto';
COMMENT ON TABLE tesla_command_log IS 'Logs all Tesla vehicle commands executed through the bot';
COMMENT ON TABLE user_activity_log IS 'Detailed user activity tracking for analytics';
COMMENT ON TABLE smart_home_log IS 'Logs all smart home commands sent to Home Assistant';
COMMENT ON TABLE ai_usage_log IS 'Tracks AI API usage, tokens, and costs';
COMMENT ON TABLE media_downloads_log IS 'Logs all media downloads (YouTube, etc.)';
COMMENT ON TABLE user_preferences IS 'Stores user preferences and settings';
COMMENT ON TABLE system_metrics IS 'System performance and usage metrics';
