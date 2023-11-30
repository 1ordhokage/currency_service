from fastapi import FastAPI

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from redis import asyncio as aioredis

from src.api.auth import router as auth_router
from src.api.currencies import router as currencies_router
from src.api.users import router as users_router
from src.utils.config import redis_settings
from src.utils.external_api import get_currencies
from src.utils.start_up import StartUp


app = FastAPI(
    title="Currency exchange service",
    version="0.0.1"
)

app.include_router(auth_router)
app.include_router(currencies_router)
app.include_router(users_router)


@app.on_event("startup")
async def startup_event() -> None:
    redis = aioredis.from_url(
        redis_settings.connection_string,
        encoding="utf8",
        decode_responses=True
    )
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    
    if not await StartUp.check_db_emptyness():
        return
    currencies = await get_currencies()
    await StartUp.insert_currencies(currencies)
