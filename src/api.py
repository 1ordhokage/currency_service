from datetime import datetime

from fastapi import APIRouter, Depends

from src.service import CurrenciesService
from src.schemas.convert import ConvertSchema, ConvertResponseSchema
from src.schemas.update_date_time import UpdateDateTimeSchema


router = APIRouter(
    prefix="/api",
    tags=["api"]
)


@router.put("/rates")
async def update_rates(service: CurrenciesService = Depends()) -> None:
    """Endpoint for updating rates from the external API.
    Args:
        service (CurrenciesService, optional): currencies business-logic.
        Defaults to Depends().
    """
    await service.update_rates()


@router.get("/last-updated", response_model=UpdateDateTimeSchema)
async def get_last_updated(
    service: CurrenciesService = Depends()
) -> UpdateDateTimeSchema:
    """Endpoint for checking when the rates were updated for the last time.
    Args:
        service (CurrenciesService, optional): currencies business-logic.
        Defaults to Depends().
    Returns:
        UpdateDateTimeSchema: Latest rates update time.
    """
    return await service.get_update_date_time()


@router.post("/convert", response_model=ConvertResponseSchema)
async def convert(
    schema: ConvertSchema,
    service: CurrenciesService = Depends()
) -> ConvertResponseSchema:
    """Endpoint for currency convertion.
    Args:
        schema (ConvertSchema): Convertion DTO.
        service (CurrenciesService, optional): currencies business-logic.
        Defaults to Depends().
    Returns:
        ConvertResponseSchema: Convertion response DTO.
    """
    result = await service.convert(schema)
    return ConvertResponseSchema(
        original_code=schema.original_code,
        target_code=schema.target_code,
        amount=schema.amount,
        result=result,
        date_time=datetime.now()
    )
