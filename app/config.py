from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_name: str = "LMI Auth Service"
    debug: bool = True
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    database_url: str = "postgresql+psycopg2://lmi_user:change_me@localhost:5432/lmi_auth"

    secret_key: str = "change_me"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    log_level: str = "INFO"
    log_file: str = "auth.log"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
