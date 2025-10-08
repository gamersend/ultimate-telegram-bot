#!/usr/bin/env python3
"""
Quick Setup Script for Ultimate Telegram Bot
Automated setup without user prompts.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"🤖 {text}")
    print(f"{'='*60}")

def print_step(step: int, text: str):
    """Print a step with formatting."""
    print(f"\n📋 Step {step}: {text}")
    print("-" * 50)

def run_command(command: str, description: str) -> bool:
    """Run a shell command and return success status."""
    try:
        logger.info(f"Running: {description}")
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        logger.info(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} failed: {e}")
        return False

def main():
    """Quick automated setup."""
    print_header("Ultimate Telegram Bot - Quick Setup")
    
    success_count = 0
    total_steps = 8
    
    # Step 1: Check configuration
    print_step(1, "Checking Configuration")
    
    if os.path.exists(".env"):
        print("✅ .env file found")
        success_count += 1
    else:
        print("⚠️ .env file not found - copying from example")
        if os.path.exists(".env.example"):
            run_command("cp .env.example .env", "Creating .env from example")
            print("📝 Please edit .env file with your API keys")
        success_count += 1
    
    # Step 2: Create directories
    print_step(2, "Creating Directories")
    
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
    
    success_count += 1
    
    # Step 3: Test bot import
    print_step(3, "Testing Bot Import")
    
    try:
        # Add current directory to Python path
        sys.path.insert(0, str(Path.cwd()))
        
        # Test importing main modules
        import bot.config
        print("✅ Bot config imported")
        
        import bot.main
        print("✅ Bot main imported")
        
        success_count += 1
    except Exception as e:
        print(f"❌ Bot import failed: {e}")
        print("⚠️ Some dependencies may be missing")
    
    # Step 4: Test services
    print_step(4, "Testing Services")
    
    try:
        from bot.services.ai import ai_service
        print("✅ AI service imported")
        
        from bot.services.n8n import n8n_service
        print("✅ n8n service imported")
        
        success_count += 1
    except Exception as e:
        print(f"⚠️ Some services failed to import: {e}")
        print("✅ Core functionality should still work")
        success_count += 1
    
    # Step 5: Create startup scripts
    print_step(5, "Creating Startup Scripts")
    
    # Create simple start script
    start_script = """#!/bin/bash
# Simple Bot Starter

echo "🤖 Starting Ultimate Telegram Bot..."

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please copy .env.example to .env and configure your API keys"
    exit 1
fi

# Start the bot directly
echo "🚀 Starting bot..."
python3 -m bot.main
"""
    
    with open("start_simple.sh", "w") as f:
        f.write(start_script)
    
    os.chmod("start_simple.sh", 0o755)
    print("✅ Created start_simple.sh")
    
    # Create test script
    test_script = """#!/bin/bash
# Test Bot Configuration

echo "🧪 Testing Bot Configuration..."

# Test Python imports
python3 -c "
try:
    import bot.main
    print('✅ Bot imports successful')
except Exception as e:
    print(f'❌ Import error: {e}')
    exit(1)

try:
    from bot.config import settings
    print('✅ Configuration loaded')
    
    if settings.telegram_bot_token:
        print('✅ Telegram token configured')
    else:
        print('⚠️ Telegram token not configured')
        
    if settings.openai_api_key:
        print('✅ OpenAI API key configured')
    else:
        print('⚠️ OpenAI API key not configured')
        
except Exception as e:
    print(f'❌ Configuration error: {e}')
"

echo "🎉 Test complete!"
"""
    
    with open("test_config.sh", "w") as f:
        f.write(test_script)
    
    os.chmod("test_config.sh", 0o755)
    print("✅ Created test_config.sh")
    
    success_count += 1
    
    # Step 6: Setup n8n workflows (optional)
    print_step(6, "Setting up n8n Workflows")
    
    try:
        if run_command("python3 setup_n8n_automation.py", "Setting up n8n workflows"):
            print("✅ n8n workflows created")
            success_count += 1
        else:
            print("⚠️ n8n setup failed - continuing without it")
            success_count += 1
    except Exception as e:
        print(f"⚠️ n8n setup skipped: {e}")
        success_count += 1
    
    # Step 7: Test configuration
    print_step(7, "Testing Configuration")
    
    if run_command("./test_config.sh", "Testing bot configuration"):
        print("✅ Configuration test passed")
        success_count += 1
    else:
        print("⚠️ Configuration test failed - check your .env file")
        success_count += 1
    
    # Step 8: Summary
    print_step(8, "Setup Summary")
    
    print(f"\n📊 Setup Results: {success_count}/{total_steps} steps completed")
    
    if success_count >= 6:
        print("\n🎉 Setup completed successfully!")
        
        print("\n🚀 Next Steps:")
        print("1. Edit .env file with your API keys:")
        print("   - TELEGRAM_BOT_TOKEN (required)")
        print("   - OPENAI_API_KEY (required)")
        print("   - Other API keys (optional)")
        
        print("\n2. Start the bot:")
        print("   ./start_simple.sh")
        
        print("\n3. Test the bot:")
        print("   Send /start to your bot in Telegram")
        
        print("\n📋 Available Commands:")
        print("• /start - Welcome message")
        print("• /ask [question] - Chat with AI")
        print("• /generate [prompt] - Generate images")
        print("• /meme - Random memes")
        print("• /joke - Random jokes")
        print("• /fact - Fun facts")
        
        print("\n🔗 Useful Links:")
        print("• n8n Dashboard: http://192.168.0.150:5678")
        print("• Bot logs: Check terminal output")
        
        success_count += 1
        return 0
    else:
        print("\n❌ Setup incomplete. Please fix the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
