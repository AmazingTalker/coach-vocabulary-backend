from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database - direct URL (for local development)
    database_url: str = ""

    # Cloud SQL specific (for Cloud Run deployment)
    db_host: str = ""  # Cloud SQL instance connection name
    db_name: str = "coach_vocabulary"
    db_user: str = "postgres"
    db_password: str = ""

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # JWT Settings
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_days: int = 30

    # Static files (Cloud Storage)
    static_base_url: str = ""  # Empty = local /static, set for GCS URL

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def get_database_url(self) -> str:
        """Get database URL, supporting both local and Cloud SQL connections."""
        if self.database_url:
            return self.database_url
        if self.db_host and self.db_password:
            # Cloud SQL Unix socket connection
            return f"postgresql+psycopg2://{self.db_user}:{self.db_password}@/{self.db_name}?host=/cloudsql/{self.db_host}"
        # Fallback for local development
        return "postgresql://postgres:postgres@localhost:5432/coach_vocabulary"


settings = Settings()
