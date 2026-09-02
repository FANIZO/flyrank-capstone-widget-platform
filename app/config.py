from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./widget_platform.db"
    jwt_secret: str = "development-only-change-me"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60
    allowed_origins: str = "*"
    public_base_url: str = "http://localhost:8000"
    rate_limit_requests: int = 5
    rate_limit_window_seconds: int = 60
    max_body_bytes: int = 8192
    geo_provider_a_mode: str = "success"
    geo_provider_b_mode: str = "success"
    side_effect_force_failure: bool = False
    background_job_max_attempts: int = 2

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def allowed_origin_list(self) -> list[str]:
        return [item.strip() for item in self.allowed_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
