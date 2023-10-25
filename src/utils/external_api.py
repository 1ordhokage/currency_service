from enum import Enum

from httpx import AsyncClient, HTTPError

from fastapi import HTTPException, status

from src.utils.config import external_api_settings


class OptionsToGetEnum(Enum):
    """Enum that shows what wecan get from the external API."""
    SYMBOLS = "symbols"
    RATES = "rates"
    

async def get_from_api(option: OptionsToGetEnum) -> dict[str, str | float]:
    """Gets data from the external API. Uses access_key.
    Args:
        option (OptionsToGetEnum): Current variants shown in OptionsToGetEnum.
    Raises:
        HTTPException: HTTP_503_SERVICE_UNAVAILABLE.
    Returns:
        dict[str, str | float]: result, depends on the chosen option.
    """
    source_url = {
        OptionsToGetEnum.SYMBOLS: external_api_settings.SYMBOLS_URL,
        OptionsToGetEnum.RATES: external_api_settings.RATES_URL
    }
    params = {
        "access_key": external_api_settings.KEY
    }
    try:
        async with AsyncClient() as client:
            result = await client.get(
                source_url.get(option),
                params=params
            )
            return result.json().get(option.value)
    except HTTPError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Currency API is temporary unavailable"
        )
    

async def get_currencies() -> list[dict[str, str | float]]:
    """Gets lsit of currencies. Uses get_from_api() to transform data.
    Returns:
        list[dict[str, str | float]]: list of currencies.
    """
    symbols = await get_from_api(OptionsToGetEnum.SYMBOLS)
    rates = await get_from_api(OptionsToGetEnum.RATES)
    currencies = [
        {
            "code": code,
            "name": name,
            "rate": rates.get(code)
        }
        for code, name in symbols.items()
        if rates.get(code)
    ]
    return currencies
