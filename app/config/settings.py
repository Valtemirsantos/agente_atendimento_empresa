from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Valores carregados do ambiente ou do arquivo .env local."""

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    database_url: str = "sqlite:///empresa.db"
    internal_api_key: str | None = None
    access_keys: dict[str, str] = Field(default_factory=dict)
    conversation_retention_days: int = Field(default=30, ge=1, le=365)
    rate_limit_requests: int = Field(default=60, ge=1, le=600)
    rate_limit_window_seconds: int = Field(default=60, ge=1, le=3_600)
    require_https: bool = False
    allowed_hosts: str = "localhost,127.0.0.1,testserver"
    conversation_hash_key: str | None = None
    backup_encryption_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def database_path(self) -> str:
        prefix = "sqlite:///"
        if not self.database_url.startswith(prefix):
            raise ValueError("DATABASE_URL deve usar o formato sqlite:///caminho.db")
        return self.database_url.removeprefix(prefix)

    @property
    def configured_access_keys(self) -> dict[str, str]:
        """Mantem compatibilidade local com a chave interna unica."""
        if self.access_keys:
            return self.access_keys
        if self.internal_api_key:
            return {self.internal_api_key: "support"}
        return {}

    @property
    def allowed_host_list(self) -> list[str]:
        return [host.strip() for host in self.allowed_hosts.split(",") if host.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()