import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Supabase Settings
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "your-supabase-url")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "your-supabase-anon-key")
    
    # Evolution API Settings
    EVOLUTION_API_URL: str = os.getenv("EVOLUTION_API_URL", "your-evolution-api-url")
    EVOLUTION_API_KEY: str = os.getenv("EVOLUTION_API_KEY", "your-evolution-api-key")
    EVOLUTION_INSTANCE_NAME: str = os.getenv("EVOLUTION_INSTANCE_NAME", "your-instance-name")
    
    # AI / LLM Settings
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "your-groq-api-key")
    HUGGINGFACE_TOKEN: str = os.getenv("HUGGINGFACE_TOKEN", "your-hf-token")
    
    class Config:
        env_file = ".env"

settings = Settings()
