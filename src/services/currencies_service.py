from datetime import datetime

from fastapi import Depends, HTTPException, status

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import get_async_session
from src.models.currencies import Currency
from src.models.update_date_time import UpdateDateTime
from src.schemas.convert import ConvertSchema
from src.utils.external_api import get_from_api, OptionsToGetEnum


class CurrenciesService:
    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self.session = session
    
    async def get_update_date_time(self) -> UpdateDateTime:
        result = await self.session.execute(
            select(UpdateDateTime)
        )
        return list(
            result.scalars()
        )[-1]

    async def __insert_update_date_time(self):
        await self.session.execute(
            insert(UpdateDateTime)
            .values(
                {"last_update": datetime.now()}
            )
        )
         
    async def update_rates(self):
        new_rates = await get_from_api(OptionsToGetEnum.RATES)
        for code, rate in new_rates.items():
            await self.session.execute(
                update(Currency)
                .where(Currency.code == code)
                .values(
                    {"rate": rate}
                )
            )
        await self.__insert_update_date_time()
        await self.session.commit()
    
    async def get_rate(self, code: str) -> float:
        try:
            currency = await self.session.execute(
                select(Currency)
                .where(Currency.code == code)
            )
            return currency.scalar().rate
        except AttributeError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Currency not found"
            )
        
    async def convert(self, schema: ConvertSchema) -> float:
        original_rate = await self.get_rate(schema.original_code)
        target_rate = await self.get_rate(schema.target_code)
        return "{:.2f}".format(target_rate / original_rate * schema.amount)
