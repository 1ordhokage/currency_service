import asyncio
from typing import AsyncGenerator
from fastapi.testclient import TestClient
from httpx import AsyncClient

from pydantic_settings import BaseSettings, SettingsConfigDict
import pytest

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

from src.database.database import get_async_session
from src.main import app
from src.models.base import Base


# REDIS_HOST=localhost
# REDIS_PORT=6379

# DB
class TestDBSettings(BaseSettings):
    HOST: str
    PORT: str
    USER: str
    PASS: str
    NAME: str

    @property
    def connection_string(self) -> str:
        data = f"{self.USER}:{self.PASS}@{self.HOST}:{self.PORT}/{self.NAME}"
        return f"postgresql+asyncpg://{data}"
    
    model_config = SettingsConfigDict(env_prefix="TEST_DB_", env_file=".env")


test_db_settings = TestDBSettings()

engine_test = create_async_engine(
    test_db_settings.connection_string
)

async_session_maker = async_sessionmaker(
    engine_test,
    expire_on_commit=False
)

Base.metadata.bind = engine_test


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session


@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# SETUP
@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


client = TestClient(app)


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
