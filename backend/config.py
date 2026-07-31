import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./swiggy.db")

    # JWT Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-change-in-production-please-use-a-long-random-string")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))  # 7 days

    # App Settings
    APP_NAME: str = os.getenv("APP_NAME", "Swiggy Clone API")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"


settings = Settings()