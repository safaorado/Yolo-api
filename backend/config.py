from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "YOLO Classifier API"
    model_path: str = "best.pt"
    allowed_origins: list[str] = ["*"]
    max_upload_size_mb: int = 10

    class Config:
        env_file = ".env"


settings = Settings()