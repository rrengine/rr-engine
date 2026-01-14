from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://bam@localhost/rr_engine"
    redis_url: str = "redis://localhost:6379/0"
    api_keys: str = "dev-key-change-me"
    debug: bool = True

    def api_key_set(self) -> set[str]:
        return {k.strip() for k in self.api_keys.split(",") if k.strip()}

settings = Settings()
