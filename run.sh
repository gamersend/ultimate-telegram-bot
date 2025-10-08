#!/bin/bash

# Ultimate Telegram Bot Runner Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

# Check if .env file exists
check_env() {
    if [ ! -f ".env" ]; then
        print_error ".env file not found!"
        print_status "Creating .env from template..."
        cp .env.example .env
        print_warning "Please edit .env file with your configuration before running again"
        exit 1
    fi
}

# Check if required directories exist
check_directories() {
    directories=("data" "logs" "media" "config")
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            print_status "Creating directory: $dir"
            mkdir -p "$dir"
        fi
    done
}

# Install Python dependencies
install_deps() {
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
}

# Run database migrations
setup_database() {
    print_status "Setting up database..."
    # Database setup is handled by the application
}

# Start the bot in development mode
start_dev() {
    print_header "🤖 Starting Ultimate Telegram Bot (Development Mode)"
    check_env
    check_directories
    
    if [ "$1" = "--install" ]; then
        install_deps
    fi
    
    setup_database
    
    print_status "Starting bot..."
    export PYTHONPATH="${PWD}"
    python -m bot.main
}

# Start with Docker Compose
start_docker() {
    print_header "🐳 Starting Ultimate Telegram Bot (Docker Mode)"
    check_env
    
    if [ ! -f ".env.docker" ]; then
        print_error ".env.docker file not found!"
        print_status "Creating .env.docker from template..."
        cat > .env.docker << EOF
DB_PASSWORD=secure_db_password_change_this
GRAFANA_PASSWORD=secure_grafana_password_change_this
EOF
        print_warning "Please edit .env.docker with secure passwords"
        exit 1
    fi
    
    print_status "Building and starting containers..."
    docker-compose up -d --build
    
    print_status "Waiting for services to start..."
    sleep 10
    
    print_status "Checking service health..."
    docker-compose ps
    
    print_header "🎉 Bot started successfully!"
    print_status "Services available at:"
    echo "  • Bot API: http://localhost:8000"
    echo "  • Grafana: http://localhost:3000"
    echo "  • Prometheus: http://localhost:9091"
    echo ""
    print_status "View logs with: docker-compose logs -f"
}

# Stop Docker services
stop_docker() {
    print_header "🛑 Stopping Ultimate Telegram Bot"
    docker-compose down
    print_status "All services stopped"
}

# Show logs
show_logs() {
    if [ "$1" = "docker" ]; then
        docker-compose logs -f
    else
        tail -f logs/bot.log
    fi
}

# Setup webhook
setup_webhook() {
    if [ -z "$1" ]; then
        print_error "Please provide webhook URL"
        echo "Usage: $0 webhook https://yourdomain.com/webhook"
        exit 1
    fi
    
    source .env
    if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
        print_error "TELEGRAM_BOT_TOKEN not found in .env"
        exit 1
    fi
    
    print_status "Setting webhook to: $1"
    curl -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook" \
         -H "Content-Type: application/json" \
         -d "{\"url\": \"$1\"}"
    echo ""
    print_status "Webhook set successfully"
}

# Delete webhook (use polling)
delete_webhook() {
    source .env
    if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
        print_error "TELEGRAM_BOT_TOKEN not found in .env"
        exit 1
    fi
    
    print_status "Deleting webhook..."
    curl -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/deleteWebhook"
    echo ""
    print_status "Webhook deleted - bot will use polling"
}

# Show help
show_help() {
    print_header "🤖 Ultimate Telegram Bot Runner"
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  dev [--install]     Start in development mode"
    echo "  docker              Start with Docker Compose"
    echo "  stop                Stop Docker services"
    echo "  logs [docker]       Show logs"
    echo "  webhook <url>       Set webhook URL"
    echo "  polling             Delete webhook (use polling)"
    echo "  setup               Run initial setup"
    echo "  help                Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 dev --install                           # Install deps and start dev"
    echo "  $0 docker                                  # Start with Docker"
    echo "  $0 webhook https://bot.example.com/webhook # Set webhook"
    echo "  $0 logs docker                             # Show Docker logs"
}

# Main script logic
case "$1" in
    "dev")
        start_dev "$2"
        ;;
    "docker")
        start_docker
        ;;
    "stop")
        stop_docker
        ;;
    "logs")
        show_logs "$2"
        ;;
    "webhook")
        setup_webhook "$2"
        ;;
    "polling")
        delete_webhook
        ;;
    "setup")
        python setup.py
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
