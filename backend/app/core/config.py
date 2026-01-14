from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg://localhost/rr_system"
    ENV: str = "dev"

settings = Settings()
