from pydantic_settings import BaseSettings, SettingsConfigDict


class ExternalAPISettings(BaseSettings):
    SYMBOLS_URL: str
    RATES_URL: str
    KEY: str
    
    model_config = SettingsConfigDict(
        env_prefix="EXTERNAL_API_",
        env_file=".env"
    )


external_api_settings = ExternalAPISettings()
