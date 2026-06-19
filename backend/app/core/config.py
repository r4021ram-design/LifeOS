import os
from typing import Optional
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"  # development, testing, staging, production
    SECRET_KEY: str = "super_secret_institutional_grade_lifeos_key_1234567890"
    DATABASE_URL: str = "sqlite:///./lifeos.db"
    REDIS_URL: str = "redis://redis:6379/0"
    CORS_ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://app.lifeos-ai.com",
        "https://lifeos-ai.com",
        "https://life-os-kohl-ten.vercel.app"
    ]
    
    # AI Credentials
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    
    # Sentry
    SENTRY_DSN: Optional[str] = None
    
    # Notifications
    FCM_SERVER_KEY: Optional[str] = None
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SENDER_EMAIL: str = "no-reply@lifeos-ai.com"
    
    # Broker Connectors
    KOTAK_API_KEY: Optional[str] = None
    FYERS_API_KEY: Optional[str] = None
    
    # Feature Flags
    enable_trading: bool = True
    enable_ai: bool = True
    enable_panchang: bool = True
    enable_beta_features: bool = False
 
    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        if self.ENVIRONMENT in ["staging", "production"]:
            if self.SECRET_KEY == "super_secret_institutional_grade_lifeos_key_1234567890":
                raise ValueError("SECRET_KEY must be changed in staging/production environments!")
            if not self.DATABASE_URL.startswith(("postgresql://", "postgresql+psycopg2://")):
                raise ValueError("DATABASE_URL must be a PostgreSQL connection string in staging/production!")
            if not self.SENTRY_DSN:
                # We can log or raise a warning instead of erroring, but the user expects production readiness
                print("[Warning] SENTRY_DSN is not configured in staging/production environment.")
        return self
 
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)
 
settings = Settings()
