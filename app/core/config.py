from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Carrier Gateway Service"
    env: str = "test"
    database_url: str

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

settings = Settings()