#!/usr/bin/env python3
"""
Complete Setup Script for Ultimate Telegram Bot
This script performs a full setup and deployment of the bot with all features.
"""

import asyncio
import subprocess
import sys
import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UltimateBotSetup:
    """Complete setup class for the Ultimate Telegram Bot."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.success_count = 0
        self.total_steps = 10
    
    def print_header(self, text: str):
        """Print a formatted header."""
        print(f"\n{'='*60}")
        print(f"🤖 {text}")
        print(f"{'='*60}")
    
    def print_step(self, step: int, text: str):
        """Print a step with formatting."""
        print(f"\n📋 Step {step}/{self.total_steps}: {text}")
        print("-" * 50)
    
    def run_command(self, command: str, description: str) -> bool:
        """Run a shell command and return success status."""
        try:
            logger.info(f"Running: {description}")
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            logger.info(f"✅ {description} completed successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ {description} failed: {e}")
            logger.error(f"Error output: {e.stderr}")
            return False
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are installed."""
        self.print_step(1, "Checking Prerequisites")
        
        prerequisites = [
            ("python3", "Python 3.11+"),
            ("pip", "Python Package Manager"),
            ("docker", "Docker"),
            ("docker-compose", "Docker Compose")
        ]
        
        all_good = True
        for cmd, name in prerequisites:
            if self.run_command(f"which {cmd}", f"Checking {name}"):
                print(f"✅ {name} found")
            else:
                print(f"❌ {name} not found")
                all_good = False
        
        if all_good:
            self.success_count += 1
        
        return all_good
    
    def setup_environment(self) -> bool:
        """Setup Python environment and install dependencies."""
        self.print_step(2, "Setting up Python Environment")
        
        commands = [
            ("python3 -m pip install --upgrade pip", "Upgrading pip"),
            ("pip install -r requirements.txt", "Installing Python dependencies")
        ]
        
        all_success = True
        for cmd, desc in commands:
            if not self.run_command(cmd, desc):
                all_success = False
        
        if all_success:
            self.success_count += 1
        
        return all_success
    
    def check_configuration(self) -> bool:
        """Check if configuration files are properly set up."""
        self.print_step(3, "Checking Configuration")
        
        config_files = [
            (".env", "Environment variables"),
            ("docker-compose.yml", "Docker configuration"),
            ("bot/config.py", "Bot configuration")
        ]
        
        all_good = True
        for file_path, description in config_files:
            if os.path.exists(file_path):
                print(f"✅ {description} found")
            else:
                print(f"❌ {description} missing: {file_path}")
                all_good = False
        
        # Check if .env has required variables
        if os.path.exists(".env"):
            with open(".env", "r") as f:
                env_content = f.read()
                required_vars = ["TELEGRAM_BOT_TOKEN", "OPENAI_API_KEY"]
                
                for var in required_vars:
                    if var in env_content and not env_content.count(f"{var}=") == 0:
                        print(f"✅ {var} configured")
                    else:
                        print(f"❌ {var} not configured in .env")
                        all_good = False
        
        if all_good:
            self.success_count += 1
        
        return all_good
    
    def setup_directories(self) -> bool:
        """Create necessary directories."""
        self.print_step(4, "Creating Directories")
        
        directories = [
            "data/notes",
            "data/files",
            "media/downloads",
            "logs",
            "backups"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        
        self.success_count += 1
        return True
    
    async def setup_n8n_workflows(self) -> bool:
        """Setup n8n workflows."""
        self.print_step(5, "Setting up n8n Workflows")
        
        try:
            # Import and run the n8n setup
            sys.path.append(str(self.project_root))
            from setup_n8n_automation import N8NAutomationSetup
            
            setup = N8NAutomationSetup()
            success = await setup.setup_all_workflows()
            
            if success:
                print("✅ n8n workflows created successfully")
                self.success_count += 1
                return True
            else:
                print("❌ n8n workflow setup failed")
                return False
                
        except Exception as e:
            logger.error(f"Error setting up n8n workflows: {e}")
            print("⚠️ n8n setup skipped (optional)")
            return True  # Don't fail the entire setup for n8n
    
    def test_bot_import(self) -> bool:
        """Test if the bot can be imported successfully."""
        self.print_step(6, "Testing Bot Import")
        
        try:
            # Test importing the main bot module
            import bot.main
            print("✅ Bot import successful")
            self.success_count += 1
            return True
        except Exception as e:
            print(f"❌ Bot import failed: {e}")
            return False
    
    def build_docker_images(self) -> bool:
        """Build Docker images."""
        self.print_step(7, "Building Docker Images")
        
        if self.run_command("docker-compose build --no-cache", "Building Docker images"):
            print("✅ Docker images built successfully")
            self.success_count += 1
            return True
        else:
            print("❌ Docker build failed")
            return False
    
    def test_services(self) -> bool:
        """Test individual services."""
        self.print_step(8, "Testing Services")
        
        try:
            # Test AI service
            from bot.services.ai import ai_service
            print("✅ AI service imported")
            
            # Test other services
            from bot.services.media import media_service
            print("✅ Media service imported")
            
            from bot.services.finance import finance_service
            print("✅ Finance service imported")
            
            from bot.services.fun import fun_service
            print("✅ Fun service imported")
            
            self.success_count += 1
            return True
            
        except Exception as e:
            print(f"❌ Service test failed: {e}")
            return False
    
    def create_startup_scripts(self) -> bool:
        """Create convenient startup scripts."""
        self.print_step(9, "Creating Startup Scripts")
        
        # Create a simple start script
        start_script = """#!/bin/bash
# Ultimate Telegram Bot Startup Script

echo "🤖 Starting Ultimate Telegram Bot..."

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please copy .env.example to .env and configure your API keys"
    exit 1
fi

# Start with Docker Compose
echo "🐳 Starting with Docker Compose..."
docker-compose up -d

echo "✅ Bot started successfully!"
echo "📊 View logs: docker-compose logs -f"
echo "🛑 Stop bot: docker-compose down"
"""
        
        with open("start_bot.sh", "w") as f:
            f.write(start_script)
        
        os.chmod("start_bot.sh", 0o755)
        print("✅ Created start_bot.sh")
        
        # Create status check script
        status_script = """#!/bin/bash
# Bot Status Check Script

echo "🤖 Ultimate Telegram Bot Status"
echo "================================"

docker-compose ps
echo ""
echo "📊 Recent logs:"
docker-compose logs --tail=10
"""
        
        with open("check_status.sh", "w") as f:
            f.write(status_script)
        
        os.chmod("check_status.sh", 0o755)
        print("✅ Created check_status.sh")
        
        self.success_count += 1
        return True
    
    def display_summary(self) -> bool:
        """Display setup summary and next steps."""
        self.print_step(10, "Setup Summary")
        
        print(f"\n📊 Setup Results: {self.success_count}/{self.total_steps} steps completed")
        
        if self.success_count >= 8:  # Allow some optional steps to fail
            print("\n🎉 Setup completed successfully!")
            
            print("\n🚀 Next Steps:")
            print("1. Configure your API keys in .env file")
            print("2. Start the bot: ./start_bot.sh")
            print("3. Check status: ./check_status.sh")
            print("4. Test bot features in Telegram")
            print("5. Set up webhook: ./run.sh webhook https://yourdomain.com/webhook")
            
            print("\n📋 Available Commands:")
            print("• /start - Welcome message")
            print("• /ask [question] - Chat with AI")
            print("• /generate [prompt] - Generate images")
            print("• /stock AAPL - Get stock prices")
            print("• /crypto bitcoin - Get crypto prices")
            print("• /meme - Random memes")
            print("• /joke - Random jokes")
            print("• /news tech - Latest news")
            
            print("\n🔗 Useful Links:")
            print("• n8n Dashboard: http://192.168.0.150:5678")
            print("• Grafana (when running): http://localhost:3000")
            print("• Bot API: http://localhost:8000")
            
            self.success_count += 1
            return True
        else:
            print("\n❌ Setup incomplete. Please fix the errors above and try again.")
            return False


async def main():
    """Main setup function."""
    setup = UltimateBotSetup()
    
    setup.print_header("Ultimate Telegram Bot - Complete Setup")
    print("This script will set up your Ultimate Telegram Bot with all features.")
    print("Please ensure you have configured your .env file with API keys.")
    
    input("\nPress Enter to continue...")
    
    # Run all setup steps
    steps = [
        setup.check_prerequisites,
        setup.setup_environment,
        setup.check_configuration,
        setup.setup_directories,
        lambda: asyncio.create_task(setup.setup_n8n_workflows()),
        setup.test_bot_import,
        setup.build_docker_images,
        setup.test_services,
        setup.create_startup_scripts,
        setup.display_summary
    ]
    
    for i, step in enumerate(steps, 1):
        try:
            if asyncio.iscoroutine(step()) or hasattr(step(), '__await__'):
                result = await step()
            else:
                result = step()
            
            if not result and i <= 7:  # Critical steps
                print(f"\n❌ Critical step {i} failed. Aborting setup.")
                return 1
                
        except Exception as e:
            logger.error(f"Error in step {i}: {e}")
            if i <= 7:  # Critical steps
                print(f"\n❌ Critical step {i} failed. Aborting setup.")
                return 1
    
    if setup.success_count >= 8:
        print("\n🎉 Ultimate Telegram Bot setup completed successfully!")
        print("Your bot is ready to use! 🤖⚡")
        return 0
    else:
        print("\n❌ Setup failed. Please check the errors and try again.")
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
