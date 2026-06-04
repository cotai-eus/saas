from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = ""
    db_user: str = "saas"
    db_password: str = ""
    db_host: str = "localhost"
    db_port: str = "5432"
    db_name: str = "saas"
    auth_host: str = "auth.local.dev"

    redis_url: str = "redis://localhost:6379/0"
    queue_backend: str = "redis"

    baileys_service_url: str = "http://baileys:3000"
    baileys_api_key: str = ""

    channel_config_encryption_key: str = ""

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    model_config = {"env_file": ".env", "env_prefix": ""}


settings = Settings()
