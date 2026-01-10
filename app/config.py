from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # General
    app_name: str = "DevGraph Copilot"   # <-- add this

    # LLM config
    use_llm: bool = False
    llm_model_name: str = "llama-3.3-70b-versatile"
    llm_base_url: str = "https://api.groq.com/openai/v1"
    groq_api_key: str = ""

    class Config:
        env_file = ".env"

settings = Settings()





# This lets you load environment variables later.
# For now it just gives settings.app_name and settings.environment.
# Now settings.openai_api_key and settings.llm_model_name are available.
