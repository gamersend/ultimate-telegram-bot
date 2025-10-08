"""Configuration management for the Ultimate Telegram Bot."""

import os
from typing import List, Optional, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Telegram Configuration
    telegram_bot_token: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    telegram_webhook_url: Optional[str] = Field(None, env="TELEGRAM_WEBHOOK_URL")
    telegram_webhook_secret: Optional[str] = Field(None, env="TELEGRAM_WEBHOOK_SECRET")
    allowed_user_ids: Union[str, List[int]] = Field(default="", env="ALLOWED_USER_IDS")

    @field_validator('allowed_user_ids', mode='after')
    @classmethod
    def parse_allowed_user_ids(cls, v):
        if isinstance(v, str):
            if not v:
                return []
            # Handle comma-separated string
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        elif isinstance(v, list):
            # Already a list
            return v
        return []
    
    # AI Configuration
    openai_api_key: str = Field("sk-KAIMgP6rzU1aRfxeLV6chA", env="OPENAI_API_KEY")
    openai_base_url: str = Field("http://192.168.0.150:4000/v1", env="OPENAI_BASE_URL")
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    
    # Database Configuration
    database_url: str = Field("sqlite:///./data/telebot.db", env="DATABASE_URL")
    redis_url: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    
    # Smart Home Integration
    home_assistant_url: Optional[str] = Field(None, env="HOME_ASSISTANT_URL")
    home_assistant_token: Optional[str] = Field(None, env="HOME_ASSISTANT_TOKEN")
    
    # Tesla Integration
    tesla_email: Optional[str] = Field(None, env="TESLA_EMAIL")
    tesla_refresh_token: Optional[str] = Field(None, env="TESLA_REFRESH_TOKEN")
    
    # Financial APIs
    alpha_vantage_api_key: Optional[str] = Field(None, env="ALPHA_VANTAGE_API_KEY")
    tradingview_webhook_secret: Optional[str] = Field(None, env="TRADINGVIEW_WEBHOOK_SECRET")
    
    # Media APIs
    spotify_client_id: Optional[str] = Field(None, env="SPOTIFY_CLIENT_ID")
    spotify_client_secret: Optional[str] = Field(None, env="SPOTIFY_CLIENT_SECRET")
    spotify_redirect_uri: str = Field("http://localhost:8000/callback/spotify", env="SPOTIFY_REDIRECT_URI")
    
    # Productivity APIs
    notion_token: Optional[str] = Field(None, env="NOTION_TOKEN")
    google_credentials_file: Optional[str] = Field(None, env="GOOGLE_CREDENTIALS_FILE")
    
    # News APIs
    news_api_key: Optional[str] = Field(None, env="NEWS_API_KEY")
    
    # Entertainment APIs
    imgflip_username: Optional[str] = Field(None, env="IMGFLIP_USERNAME")
    imgflip_password: Optional[str] = Field(None, env="IMGFLIP_PASSWORD")
    tenor_api_key: Optional[str] = Field(None, env="TENOR_API_KEY")
    giphy_api_key: Optional[str] = Field(None, env="GIPHY_API_KEY")

    # n8n Integration
    n8n_url: str = Field("http://192.168.0.150:5678", env="N8N_URL")
    n8n_token: str = Field("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4YTFjYWYwOS0xODg5LTQxZDAtYTY3My00MzVkZjliNmUxMDEiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU5OTIxMTYxfQ.bslOmS0kywILrReGkUMo5x9XtYLT4qMXe6DLTRrmYvU", env="N8N_TOKEN")
    
    # Security
    jwt_secret_key: str = Field("your-secret-key-change-this", env="JWT_SECRET_KEY")
    webhook_secret: str = Field("your-webhook-secret", env="WEBHOOK_SECRET")
    
    # Monitoring
    prometheus_port: int = Field(9090, env="PROMETHEUS_PORT")
    grafana_port: int = Field(3000, env="GRAFANA_PORT")
    
    # Application Settings
    debug: bool = Field(False, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    environment: str = Field("development", env="ENVIRONMENT")
    
    # Server Settings
    host: str = Field("0.0.0.0", env="HOST")
    port: int = Field(8000, env="PORT")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str):
            if field_name == "allowed_user_ids":
                # Handle both comma-separated and JSON list formats
                if raw_val.startswith('[') and raw_val.endswith(']'):
                    # JSON format
                    import json
                    return json.loads(raw_val)
                else:
                    # Comma-separated format
                    return [int(x.strip()) for x in raw_val.split(",") if x.strip()]
            return cls.json_loads(raw_val)


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the current settings instance."""
    return settings
