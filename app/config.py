from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "DevGraph Copilot"
    environment: str = "local"

    class Config:
        env_file = ".env"


settings = Settings()

# This lets you load environment variables later.
# For now it just gives settings.app_name and settings.environment.
