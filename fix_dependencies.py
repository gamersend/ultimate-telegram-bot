#!/usr/bin/env python3
"""
Fix Dependencies Script
Installs dependencies in stages to avoid version conflicts.
"""

import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_pip_install(packages, description):
    """Install packages with pip."""
    try:
        cmd = [sys.executable, "-m", "pip", "install"] + packages
        logger.info(f"Installing {description}...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(f"✅ {description} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to install {description}: {e}")
        logger.error(f"Error output: {e.stderr}")
        return False

def main():
    """Install dependencies in stages."""
    print("🔧 Fixing Dependencies for Ultimate Telegram Bot")
    print("=" * 50)
    
    # Stage 1: Core dependencies
    core_packages = [
        "aiogram>=3.3.0",
        "fastapi>=0.104.0", 
        "uvicorn[standard]>=0.24.0",
        "python-dotenv>=1.0.0",
        "httpx>=0.25.0",
        "requests>=2.31.0"
    ]
    
    if not run_pip_install(core_packages, "Core Bot Framework"):
        return 1
    
    # Stage 2: AI packages
    ai_packages = [
        "openai>=1.3.0",
        "anthropic>=0.7.0",
        "tiktoken>=0.5.0"
    ]
    
    if not run_pip_install(ai_packages, "AI & Language Models"):
        return 1
    
    # Stage 3: Database
    db_packages = [
        "asyncpg>=0.29.0",
        "sqlalchemy>=2.0.0"
    ]
    
    if not run_pip_install(db_packages, "Database Support"):
        return 1
    
    # Stage 4: Image processing
    image_packages = [
        "Pillow>=10.0.0",
        "opencv-python>=4.8.0"
    ]
    
    if not run_pip_install(image_packages, "Image Processing"):
        return 1
    
    # Stage 5: Utilities
    util_packages = [
        "beautifulsoup4>=4.12.0",
        "feedparser>=6.0.10",
        "python-dateutil>=2.8.0",
        "pytz>=2023.3",
        "pyyaml>=6.0",
        "aiofiles>=23.2.0",
        "prometheus-client>=0.19.0"
    ]
    
    if not run_pip_install(util_packages, "Utilities"):
        return 1
    
    # Stage 6: Optional packages (install individually)
    optional_packages = [
        ("homeassistant-api>=5.0.2", "Home Assistant Integration"),
        ("teslapy>=2.8.0", "Tesla Integration"),
        ("yt-dlp>=2023.11.16", "YouTube Downloads"),
        ("spotipy>=2.23.0", "Spotify Integration"),
        ("yfinance>=0.2.28", "Financial Data"),
        ("pycoingecko>=3.1.0", "Cryptocurrency Data"),
        ("pydub>=0.25.1", "Audio Processing"),
        ("SpeechRecognition>=3.10.0", "Speech Recognition")
    ]
    
    print("\n📦 Installing Optional Packages...")
    success_count = 0
    
    for package, description in optional_packages:
        if run_pip_install([package], description):
            success_count += 1
        else:
            logger.warning(f"⚠️ {description} failed - continuing without it")
    
    print(f"\n🎉 Installation Complete!")
    print(f"✅ Core packages: Installed")
    print(f"📦 Optional packages: {success_count}/{len(optional_packages)} installed")
    
    if success_count >= len(optional_packages) // 2:
        print("\n✅ Sufficient packages installed. Bot should work!")
        return 0
    else:
        print("\n⚠️ Some optional packages failed. Basic functionality available.")
        return 0

if __name__ == "__main__":
    exit(main())
