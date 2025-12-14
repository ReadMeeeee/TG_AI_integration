from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    dialect: str = "postgresql"
    driver: str = "asyncpg"
    db_path: str = "postgres:postgres@localhost:5432/TG_AI_integration_db"

    sql_echo: bool = False

    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_pre_ping: bool = True
    db_pool_recycle: int = 1800

    @computed_field
    @property
    def database_url(self) -> str:
        return f"{self.dialect}+{self.driver}://{self.db_path}"


settings = Settings()
