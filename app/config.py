import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):

    env: str = "prod"
    database_url: str = "sqlite:///./data/app.db"
    database_clean: bool = False
    secret_key: str = "prod-secret"
    app_port: int = 80
    app_prefix: str = ""

    model_config = SettingsConfigDict(env_file=".env")

    def __init__(self, **values):
        if 'ENV' in os.environ:
            custom_env = f".env.{os.environ['ENV']}"
            if os.path.exists(custom_env):
                self.model_config['env_file'] = custom_env
        super().__init__(**values)

@lru_cache()
def get_settings():
    return Settings()