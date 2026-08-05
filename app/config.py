from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    DATABASE_URL: str
    DATABASE_PASSWORD: str
    TEST_DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env")


    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """Convert the DATABASE_URL to use async driver.""" # For deployment
        url = self.DATABASE_URL
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+asyncpg://",1)

        return url

    
    @property
    def TEST_ASYNC_DATABASE_URL(self) -> str:
        """Convert the TEST_DATABASE_URL to use async driver."""
        url = self.TEST_DATABASE_URL
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+asyncpg://",1)

        return url
settings = Settings()  # type: ignore
