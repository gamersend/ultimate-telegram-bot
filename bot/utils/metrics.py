"""Prometheus metrics for monitoring."""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Define metrics
request_counter = Counter('telegram_bot_requests_total', 'Total number of requests')
request_duration = Histogram('telegram_bot_request_duration_seconds', 'Request duration')
active_users = Gauge('telegram_bot_active_users', 'Number of active users')
command_counter = Counter('telegram_bot_commands_total', 'Total commands executed', ['command'])
error_counter = Counter('telegram_bot_errors_total', 'Total errors', ['error_type'])

# AI-specific metrics
ai_requests = Counter('telegram_bot_ai_requests_total', 'AI requests', ['provider'])
ai_tokens = Counter('telegram_bot_ai_tokens_total', 'AI tokens used', ['provider', 'type'])
ai_cost = Counter('telegram_bot_ai_cost_total', 'AI cost in USD', ['provider'])

# Feature-specific metrics
voice_messages = Counter('telegram_bot_voice_messages_total', 'Voice messages processed')
images_generated = Counter('telegram_bot_images_generated_total', 'Images generated')
smart_home_commands = Counter('telegram_bot_smart_home_commands_total', 'Smart home commands')
tesla_commands = Counter('telegram_bot_tesla_commands_total', 'Tesla commands')
finance_requests = Counter('telegram_bot_finance_requests_total', 'Finance requests')


def setup_metrics():
    """Initialize metrics collection."""
    pass


def generate_metrics():
    """Generate metrics in Prometheus format."""
    return generate_latest()
