from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Onetrail API"
    # Development fallback only; production must supply APP_SECRET_KEY from a secret manager.
    app_secret_key: str = "development-only-secret-key-replace-before-production"
    # PostgreSQL is the application database. SQLite is supported only for isolated tests.
    database_url: str = "postgresql+psycopg://hiking_app:change-me@localhost:5433/hiking_decision"
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    amap_api_base_url: str = "https://restapi.amap.com"
    amap_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        origins = [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
        # Capacitor 安卓/iOS 壳内 WebView 的固定来源，始终放行
        for capacitor_origin in ("http://localhost", "https://localhost", "capacitor://localhost"):
            if capacitor_origin not in origins:
                origins.append(capacitor_origin)
        return origins


@lru_cache
def get_settings() -> Settings:
    return Settings()
