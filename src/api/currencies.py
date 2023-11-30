from datetime import datetime

from fastapi import APIRouter, Depends, status

from src.services.currencies_service import CurrenciesService
from src.schemas.convert import ConvertSchema, ConvertResponseSchema
from src.schemas.token import TokenPayloadSchema
from src.schemas.update_date_time import UpdateDateTimeSchema
from src.token.token import Token


router = APIRouter(
    prefix="/currencies",
    tags=["Currencies controller"]
)


@router.put("/rates", status_code=status.HTTP_204_NO_CONTENT)
async def update_rates(
    _: TokenPayloadSchema = Depends(Token.verify_token),
    service: CurrenciesService = Depends()
):
    await service.update_rates()


@router.get("/last-updated", response_model=UpdateDateTimeSchema)
async def get_last_updated(
    _: TokenPayloadSchema = Depends(Token.verify_token),
    service: CurrenciesService = Depends()
):
    return await service.get_update_date_time()


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
