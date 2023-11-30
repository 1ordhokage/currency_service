from datetime import datetime

from fastapi import APIRouter, Depends, status
from fastapi_cache.decorator import cache

from src.schemas.convert import ConvertSchema, ConvertResponseSchema
from src.schemas.currency import CurrencySchema
from src.schemas.token import TokenPayloadSchema
from src.schemas.update_date_time import UpdateDateTimeSchema

from src.services.currencies_service import CurrenciesService

from src.token.token import Token


router = APIRouter(
    prefix="/currencies",
    tags=["Currencies controller"]
)


@router.get("", response_model=list[CurrencySchema])
@cache(expire=600)
async def get_currencies(
    _: TokenPayloadSchema = Depends(Token.verify_token),
    service: CurrenciesService = Depends()
):
    currencies = await service.get_currencies()
    return currencies


@router.put("/rates", status_code=status.HTTP_204_NO_CONTENT)
async def update_rates(
    _: TokenPayloadSchema = Depends(Token.verify_admin),
    service: CurrenciesService = Depends()
):
    await service.update_rates()


@router.get("/last-updated", response_model=UpdateDateTimeSchema)
async def get_last_updated(
    _: TokenPayloadSchema = Depends(Token.verify_admin),
    service: CurrenciesService = Depends()
):
    last_updated = await service.get_update_date_time()
    return last_updated


@router.post("/convert", response_model=ConvertResponseSchema)
async def convert(
    schema: ConvertSchema,
    _: TokenPayloadSchema = Depends(Token.verify_token),
    service: CurrenciesService = Depends()
):
    result = await service.convert(schema)
    return ConvertResponseSchema(
        original_code=schema.original_code,
        target_code=schema.target_code,
        amount=schema.amount,
        result=result,
        date_time=datetime.now()
    )
