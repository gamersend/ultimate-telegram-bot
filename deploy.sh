#!/bin/bash

# Ultimate Telegram Bot Deployment Script
# This script deploys the bot to your Unraid server with full monitoring

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
UNRAID_HOST="${UNRAID_HOST:-192.168.0.100}"
UNRAID_USER="${UNRAID_USER:-root}"
DEPLOY_PATH="/mnt/user/appdata/telebot"
BACKUP_PATH="/mnt/user/backups/telebot"

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

# Check prerequisites
check_prerequisites() {
    print_header "🔍 Checking Prerequisites"
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        print_error ".env file not found!"
        print_status "Creating .env from template..."
        cp .env.example .env
        print_warning "Please edit .env file with your configuration before continuing"
        exit 1
    fi
    
    # Check if Docker is available
    if ! command -v docker &> /dev/null; then
        print_error "Docker not found! Please install Docker first."
        exit 1
    fi
    
    # Check if docker-compose is available
    if ! command -v docker-compose &> /dev/null; then
        print_error "docker-compose not found! Please install docker-compose first."
        exit 1
    fi
    
    print_status "Prerequisites check passed ✓"
}

# Validate configuration
validate_config() {
    print_header "⚙️ Validating Configuration"
    
    # Source .env file
    source .env
    
    # Check required variables
    required_vars=(
        "TELEGRAM_BOT_TOKEN"
        "OPENAI_API_KEY"
        "DATABASE_URL"
    )
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            print_error "Required environment variable $var is not set!"
            exit 1
        fi
    done
    
    print_status "Configuration validation passed ✓"
}

# Deploy to local Docker
deploy_local() {
    print_header "🐳 Deploying Locally with Docker"
    
    # Build and start containers
    print_status "Building Docker images..."
    docker-compose build --no-cache
    
    print_status "Starting services..."
    docker-compose up -d
    
    # Wait for services to start
    print_status "Waiting for services to start..."
    sleep 30
    
    # Check service health
    print_status "Checking service health..."
    docker-compose ps
    
    # Test bot connectivity
    print_status "Testing bot connectivity..."
    if docker-compose exec -T telebot python -c "from bot.main import main; print('Bot import successful')"; then
        print_status "Bot deployment successful ✓"
    else
        print_error "Bot deployment failed!"
        exit 1
    fi
}

# Deploy to Unraid
deploy_unraid() {
    print_header "🚀 Deploying to Unraid Server"
    
    if [ -z "$UNRAID_HOST" ]; then
        print_error "UNRAID_HOST not set!"
        exit 1
    fi
    
    print_status "Connecting to Unraid server: $UNRAID_HOST"
    
    # Create backup of existing deployment
    print_status "Creating backup..."
    ssh $UNRAID_USER@$UNRAID_HOST "mkdir -p $BACKUP_PATH"
    ssh $UNRAID_USER@$UNRAID_HOST "if [ -d '$DEPLOY_PATH' ]; then cp -r $DEPLOY_PATH $BACKUP_PATH/telebot-$(date +%Y%m%d-%H%M%S); fi"
    
    # Create deployment directory
    ssh $UNRAID_USER@$UNRAID_HOST "mkdir -p $DEPLOY_PATH"
    
    # Copy files to Unraid
    print_status "Copying files to Unraid..."
    rsync -avz --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' \
          --exclude='logs/*' --exclude='data/*' --exclude='media/*' \
          ./ $UNRAID_USER@$UNRAID_HOST:$DEPLOY_PATH/
    
    # Set permissions
    ssh $UNRAID_USER@$UNRAID_HOST "chmod +x $DEPLOY_PATH/run.sh $DEPLOY_PATH/setup.py"
    
    # Deploy with Docker Compose
    print_status "Starting services on Unraid..."
    ssh $UNRAID_USER@$UNRAID_HOST "cd $DEPLOY_PATH && docker-compose down && docker-compose up -d --build"
    
    # Wait and check status
    sleep 30
    ssh $UNRAID_USER@$UNRAID_HOST "cd $DEPLOY_PATH && docker-compose ps"
    
    print_status "Unraid deployment completed ✓"
}

# Setup n8n workflows
setup_n8n() {
    print_header "🔄 Setting up n8n Workflows"
    
    # Check if n8n is accessible
    if curl -s "http://192.168.0.150:5678/healthz" > /dev/null; then
        print_status "n8n is accessible ✓"
    else
        print_warning "n8n is not accessible at http://192.168.0.150:5678"
        print_status "Please ensure n8n is running and accessible"
        return
    fi
    
    print_status "n8n workflows are ready to import"
    print_status "Import files:"
    echo "  • n8n-workflows/telegram-bot-workflows.json"
    echo "  • n8n-workflows/advanced-automation-workflows.json"
    print_status "Database schema: n8n-workflows/database-schema.sql"
}

# Setup monitoring
setup_monitoring() {
    print_header "📊 Setting up Monitoring"
    
    # Check if Grafana is accessible
    if curl -s "http://localhost:3000" > /dev/null; then
        print_status "Grafana is accessible at http://localhost:3000"
        print_status "Default credentials: admin/admin"
    else
        print_status "Grafana will be available at http://localhost:3000 after deployment"
    fi
    
    # Check if Prometheus is accessible
    if curl -s "http://localhost:9091" > /dev/null; then
        print_status "Prometheus is accessible at http://localhost:9091"
    else
        print_status "Prometheus will be available at http://localhost:9091 after deployment"
    fi
}

# Test deployment
test_deployment() {
    print_header "🧪 Testing Deployment"
    
    # Test bot API endpoint
    print_status "Testing bot API..."
    if curl -s "http://localhost:8000/health" > /dev/null; then
        print_status "Bot API is responding ✓"
    else
        print_warning "Bot API is not responding"
    fi
    
    # Test webhook endpoint
    print_status "Testing webhook..."
    webhook_response=$(curl -s -X POST "http://localhost:8000/webhook" \
        -H "Content-Type: application/json" \
        -d '{"test": true}' || echo "failed")
    
    if [ "$webhook_response" != "failed" ]; then
        print_status "Webhook is responding ✓"
    else
        print_warning "Webhook test failed"
    fi
    
    # Test database connection
    print_status "Testing database connection..."
    if docker-compose exec -T postgres psql -U telebot -d telebot -c "SELECT 1;" > /dev/null 2>&1; then
        print_status "Database connection successful ✓"
    else
        print_warning "Database connection failed"
    fi
}

# Show deployment summary
show_summary() {
    print_header "🎉 Deployment Summary"
    
    echo ""
    print_status "Services:"
    echo "  • Bot API: http://localhost:8000"
    echo "  • Webhook: http://localhost:8000/webhook"
    echo "  • Grafana: http://localhost:3000 (admin/admin)"
    echo "  • Prometheus: http://localhost:9091"
    echo ""
    
    print_status "n8n Integration:"
    echo "  • n8n URL: http://192.168.0.150:5678"
    echo "  • Webhooks: See n8n-workflows/N8N_SETUP_GUIDE.md"
    echo ""
    
    print_status "Management Commands:"
    echo "  • View logs: docker-compose logs -f"
    echo "  • Restart: docker-compose restart"
    echo "  • Stop: docker-compose down"
    echo "  • Update: git pull && docker-compose up -d --build"
    echo ""
    
    print_status "Next Steps:"
    echo "  1. Import n8n workflows from n8n-workflows/ directory"
    echo "  2. Set up Grafana dashboards"
    echo "  3. Configure webhook URL with @BotFather"
    echo "  4. Test all bot features"
    echo ""
    
    print_status "Documentation:"
    echo "  • Setup Guide: docs/setup.md"
    echo "  • Features: docs/features.md"
    echo "  • n8n Setup: n8n-workflows/N8N_SETUP_GUIDE.md"
}

# Main deployment function
main() {
    print_header "🤖 Ultimate Telegram Bot Deployment"
    echo ""
    
    # Parse command line arguments
    DEPLOY_TARGET="${1:-local}"
    
    case $DEPLOY_TARGET in
        "local")
            print_status "Deploying locally with Docker"
            check_prerequisites
            validate_config
            deploy_local
            setup_monitoring
            test_deployment
            ;;
        "unraid")
            print_status "Deploying to Unraid server"
            check_prerequisites
            validate_config
            deploy_unraid
            ;;
        "n8n")
            print_status "Setting up n8n workflows only"
            setup_n8n
            ;;
        "test")
            print_status "Testing existing deployment"
            test_deployment
            ;;
        *)
            print_error "Invalid deployment target: $DEPLOY_TARGET"
            echo "Usage: $0 [local|unraid|n8n|test]"
            echo ""
            echo "Targets:"
            echo "  local  - Deploy locally with Docker (default)"
            echo "  unraid - Deploy to Unraid server"
            echo "  n8n    - Setup n8n workflows only"
            echo "  test   - Test existing deployment"
            exit 1
            ;;
    esac
    
    setup_n8n
    show_summary
    
    print_header "🚀 Deployment Complete!"
    print_status "Your Ultimate Telegram Bot is ready to use!"
}

# Run main function
main "$@"
