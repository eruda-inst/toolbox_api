from typing import ClassVar

from pydantic import EmailStr, Field, NonNegativeInt, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )

    database_url_async: str = Field(default="driver://user:pass@localhost/dbname")
    database_url_sync: str = Field(default="driver://user:pass@localhost/dbname")

    default_user_email: EmailStr = Field(default="email@email.com")
    default_user_full_name: str = Field(default="default_user_full_name")
    default_user_password: SecretStr = Field(default=SecretStr("default_user_password"))

    postgres_db: str = Field(default="postgres_db")
    postgres_password: SecretStr = Field(default=SecretStr("postgres_password"))
    postgres_user: str = Field(default="postgres_user")

    jwt_access_token_expire_minutes: NonNegativeInt = Field(default=0)
    jwt_algorithm: str = Field(default="jwt_algorithm")
    jwt_refresh_token_expire_days: NonNegativeInt = Field(default=0)
    jwt_secret_key: SecretStr = Field(default=SecretStr("jwt_secret_key"))

    autorun_migrations: str = Field(default="autorun_migrations")

    timezone: str = Field(default="timezone")

    @computed_field
    @property
    def jwt_token_expire_seconds(self) -> NonNegativeInt:
        return self.jwt_access_token_expire_minutes * 60


settings = Settings()
