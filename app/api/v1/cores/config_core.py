from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, SecretStr, EmailStr, NonNegativeInt


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = ""
    database_url_migrations: str = ""

    default_user_full_name: str = ""
    default_user_email: EmailStr = ""
    default_user_password: SecretStr = SecretStr("")

    postgres_user: str = ""
    postgres_password: SecretStr = SecretStr("")
    postgres_db: str = ""

    token_expire_minutes: NonNegativeInt = 0
    refresh_token_expire_days: NonNegativeInt = 0

    brevo_api_key: SecretStr = SecretStr("")
    brevo_from_email: EmailStr = ""
    brevo_from_name: str = ""

    secret_key: SecretStr = SecretStr("")

    @property
    def token_expire_seconds(self) -> NonNegativeInt:
        return self.token_expire_minutes * 60

    @field_validator("database_url")
    def change_db_schema(cls, v: str) -> str:
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v


settings = Settings()
