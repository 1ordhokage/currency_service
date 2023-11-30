from pydantic import BaseSettings, SettingsConfigDict


class SMTPSettings(BaseSettings):
    USER: str
    PASSWORD: str
    HOST: str
    PORT: int

    model_config = SettingsConfigDict(
        env_prefix="JWT_",
        env_file=".env"
    )


smtp_settings = SMTPSettings()
