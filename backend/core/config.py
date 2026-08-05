from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Onetrail API"
    environment: str = "development"
    # Development fallback only; production must supply APP_SECRET_KEY from a secret manager.
    app_secret_key: str = "dev-only-secret"
    # PostgreSQL is the application database. SQLite is supported only for isolated tests.
    database_url: str = "postgresql+psycopg://hiking_app:change-me@localhost:5433/hiking_decision"
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    allowed_hosts: str = "localhost,127.0.0.1,testserver"
    auto_create_schema: bool = True
    access_token_expire_minutes: int = 30
    jwt_issuer: str = "onetrail-api"
    jwt_audience: str = "onetrail-client"
    amap_api_base_url: str = "https://restapi.amap.com"
    amap_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        origins = [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
        # 本地壳开发时兼容 Capacitor；生产环境必须在 CORS_ORIGINS 中显式配置。
        if self.environment.lower() in {"development", "dev", "test"}:
            for capacitor_origin in ("http://localhost", "https://localhost", "capacitor://localhost"):
                if capacitor_origin not in origins:
                    origins.append(capacitor_origin)
        return origins

    @property
    def allowed_host_list(self) -> list[str]:
        return [host.strip() for host in self.allowed_hosts.split(",") if host.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() in {"production", "prod"}


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if settings.is_production:
        if len(settings.app_secret_key) < 32 or settings.app_secret_key.startswith("replace-with-"):
            raise ValueError("生产环境必须设置至少 32 位随机 APP_SECRET_KEY")
        if "*" in settings.cors_origin_list:
            raise ValueError("生产环境禁止使用通配符 CORS_ORIGINS")
        if not settings.allowed_host_list:
            raise ValueError("生产环境必须设置 ALLOWED_HOSTS")
    return settings
