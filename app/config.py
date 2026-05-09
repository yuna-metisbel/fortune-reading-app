from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    stripe_secret_key: str = ""
    base_url: str = "https://fortune-reading-app.onrender.com"
    database_url: str = "sqlite+aiosqlite:///./fortune.db"

    model_config = {"env_file": ".env"}


settings = Settings()
