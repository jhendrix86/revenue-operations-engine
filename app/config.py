"""
Configuration management for Revenue Operations Engine
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Payment Processing
    stripe_secret_key: str = os.getenv("STRIPE_SECRET_KEY", "")
    stripe_webhook_secret: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    paypal_client_id: str = os.getenv("PAYPAL_CLIENT_ID", "")
    paypal_client_secret: str = os.getenv("PAYPAL_CLIENT_SECRET", "")
    paypal_mode: str = os.getenv("PAYPAL_MODE", "sandbox")
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://localhost/revenue")
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Tax
    tax_api_key: str = os.getenv("TAX_API_KEY", "")
    
    # Currency
    default_currency: str = os.getenv("DEFAULT_CURRENCY", "USD")
    
    # Invoice Settings
    invoice_days_until_due: int = int(os.getenv("INVOICE_DAYS_UNTIL_DUE", "30"))
    invoice_prefix: str = os.getenv("INVOICE_PREFIX", "INV-")
    
    # Dunning Settings
    dunning_max_attempts: int = int(os.getenv("DUNNING_MAX_ATTEMPTS", "3"))
    dunning_retry_days: list = [1, 3, 7, 14]
    
    # Email
    sendgrid_api_key: str = os.getenv("SENDGRID_API_KEY", "")
    from_email: str = os.getenv("FROM_EMAIL", "billing@company.com")
    
    # Application
    app_name: str = "Revenue Operations Engine"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Integration
    global_state_manager_url: str = os.getenv("GLOBAL_STATE_MANAGER_URL", "http://localhost:8035")
    governance_engine_url: str = os.getenv("GOVERNANCE_ENGINE_URL", "http://localhost:8033")
    knowledge_graph_url: str = os.getenv("KNOWLEDGE_GRAPH_URL", "http://localhost:8034")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
