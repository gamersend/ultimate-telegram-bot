#!/usr/bin/env python3
"""Setup script for the Ultimate Telegram Bot."""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, check=True):
    """Run a shell command."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, check=check)
    return result.returncode == 0


def create_env_file():
    """Create .env file from template."""
    if not os.path.exists(".env"):
        shutil.copy(".env.example", ".env")
        print("✅ Created .env file from template")
        print("⚠️  Please edit .env file with your actual API keys and configuration")
    else:
        print("ℹ️  .env file already exists")


def setup_directories():
    """Create necessary directories."""
    directories = [
        "data", "logs", "media", "config",
        "monitoring/grafana/dashboards",
        "monitoring/grafana/datasources",
        "nginx/ssl"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")


def install_dependencies():
    """Install Python dependencies."""
    print("Installing Python dependencies...")
    if run_command("pip install -r requirements.txt"):
        print("✅ Python dependencies installed")
    else:
        print("❌ Failed to install Python dependencies")
        return False
    return True


def setup_database():
    """Initialize database."""
    print("Setting up database...")
    # This would be handled by the application on first run
    print("✅ Database setup will be handled on first run")


def generate_ssl_certificates():
    """Generate self-signed SSL certificates for development."""
    ssl_dir = Path("nginx/ssl")
    cert_file = ssl_dir / "cert.pem"
    key_file = ssl_dir / "key.pem"
    
    if not cert_file.exists() or not key_file.exists():
        print("Generating self-signed SSL certificates...")
        command = (
            f"openssl req -x509 -newkey rsa:4096 -keyout {key_file} "
            f"-out {cert_file} -days 365 -nodes -subj '/CN=localhost'"
        )
        if run_command(command, check=False):
            print("✅ SSL certificates generated")
        else:
            print("⚠️  Failed to generate SSL certificates (openssl not found?)")
    else:
        print("ℹ️  SSL certificates already exist")


def create_docker_env():
    """Create Docker environment file."""
    docker_env_content = """# Docker Environment Variables
DB_PASSWORD=your_secure_db_password_here
GRAFANA_PASSWORD=your_grafana_password_here
"""
    
    if not os.path.exists(".env.docker"):
        with open(".env.docker", "w") as f:
            f.write(docker_env_content)
        print("✅ Created .env.docker file")
        print("⚠️  Please edit .env.docker with secure passwords")
    else:
        print("ℹ️  .env.docker file already exists")


def main():
    """Main setup function."""
    print("🤖 Setting up Ultimate Telegram Bot...")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    # Setup steps
    create_env_file()
    setup_directories()
    
    if "--docker" not in sys.argv:
        if not install_dependencies():
            sys.exit(1)
    
    create_docker_env()
    generate_ssl_certificates()
    setup_database()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed!")
    print("\nNext steps:")
    print("1. Edit .env file with your API keys and configuration")
    print("2. Edit .env.docker with secure passwords")
    print("3. Get your Telegram bot token from @BotFather")
    print("4. Configure your webhook URL or use polling mode")
    print("5. Run the bot:")
    print("   - Development: python -m bot.main")
    print("   - Production: docker-compose up -d")
    print("\nFor detailed setup instructions, see docs/setup.md")


if __name__ == "__main__":
    main()
