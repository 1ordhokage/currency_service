from fastapi import FastAPI

from src.api.auth import router as auth_router
from src.api.currencies import router as currencies_router
from src.api.users import router as users_router
from src.utils.external_api import get_currencies
from src.utils.start_up import StartUp


app = FastAPI(
    title="Currency exchange API",
    version="0.0.1"
)

app.include_router(auth_router)
app.include_router(currencies_router)
app.include_router(users_router)


@app.on_event("startup")
async def startup_event() -> None:
    """On start-up event. Cheks if db is empty.If empty,
    then inserts currencies from an external API.
    """
    if not await StartUp.check_db_emptyness():
        return
    currencies = await get_currencies()
    await StartUp.insert_currencies(currencies)
