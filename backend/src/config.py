from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    CORS_ALLOWED_ORIGINS: list[str] = []
    OPENAI_API_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()