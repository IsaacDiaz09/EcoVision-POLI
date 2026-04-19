from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Firebase
    firebase_project_id: str

    # Roboflow
    roboflow_api_key: str
    roboflow_project: str
    roboflow_version: int = 1

    # App
    app_env: str = "development"
    app_port: int = 8000


settings = Settings()
