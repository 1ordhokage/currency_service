from pydantic_settings import BaseSettings, SettingsConfigDict


class DBSettings(BaseSettings):
    HOST: str
    PORT: str
    USER: str
    PASS: str
    NAME: str

    @property
    def connection_string(self) -> str:
        """Generates DB connection string.
        Returns:
            str: DB connnection string.
        """
        data = f"{self.USER}:{self.PASS}@{self.HOST}:{self.PORT}/{self.NAME}"
        return f"postgresql+asyncpg://{data}"
    
    model_config = SettingsConfigDict(env_prefix="DB_", env_file=".env")


db_settings = DBSettings()
