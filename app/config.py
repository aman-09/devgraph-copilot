from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "DevGraph Copilot"
    environment: str = "local"

    # LLM-related
    openai_api_key: str | None = None
    llm_model_name: str = "gpt-4o-mini"  # or any compatible model id
    use_llm: bool = False  # <-- new

    class Config:
        env_file = ".env"


settings = Settings()


# This lets you load environment variables later.
# For now it just gives settings.app_name and settings.environment.
# Now settings.openai_api_key and settings.llm_model_name are available.
