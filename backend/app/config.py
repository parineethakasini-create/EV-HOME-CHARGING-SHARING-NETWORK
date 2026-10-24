from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "sqlite:///./chargeshare.db"
    secret_key: str = "dev-secret"
    access_token_expire_minutes: int = 60
    cors_origins: list[str] = ["http://localhost:5173"]
    mqtt_host: str = ""            # empty = MQTT disabled (commands are only logged)
    mqtt_port: int = 1883
    platform_fee_pct: float = 0.10
    session_grace_minutes: int = 15
    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""
    ml_model_dir: str = "ml_artifacts"


settings = Settings()
