from pydantic_settings import BaseSettings, SettingsConfigDict


class JWTSettings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    
    model_config = SettingsConfigDict(
        env_prefix="JWT_",
        env_file=".env"
    )


jwt_settings = JWTSettings()
