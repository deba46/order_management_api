"""Application configuration."""
import os


class Settings:
    """Application settings."""
    APP_NAME: str = "Order Management API"
    APP_VERSION: str = "1.0.0"
    
    # PostgreSQL
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "orders")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "PrefectPassword123")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "orders-server-postgresql.orders-api.svc.cluster.local")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "server")


settings = Settings()
