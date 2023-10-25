from datetime import datetime

from sqlalchemy import insert, select

from src.database.database import async_session_maker, AsyncSession
from src.models.currencies import Currency
from src.models.update_date_time import UpdateDateTime


class StartUp:
    """Interface for functions that should be performed on app's start-up."""
    
    @staticmethod
    async def check_db_emptyness() -> bool:
        """Cheks if the db is emtpy.
        Returns:
            bool: Is db empty.
        """
        async with async_session_maker() as session:
            result = await session.execute(
                select(UpdateDateTime)
            )
            return result.scalars().first() is None
    
    @staticmethod
    async def __insert_update_date_time(session: AsyncSession):
        """Inserts update_date_time in empty DB. PRIVATE METHOD!
        Should be only called by StartUp.insert_currencies.
        Doesn't perform session commit.
        Args:
            session (AsyncSession): current DB session.
        """
        await session.execute(
            insert(UpdateDateTime)
            .values(
                {"last_update": datetime.now()}
            )
        )
    
    @staticmethod
    async def insert_currencies(currencies: list[dict[str, str | float]]):
        """Inserts currencies in empty DB.
        Should be ONLY performed on app's start-up.
        Args:
            currencies (list[dict[str, str | float]]): currencies.
        """
        async with async_session_maker() as session:
            await session.execute(
                insert(Currency)
                .values(currencies)
            )
            await StartUp.__insert_update_date_time(session)
            await session.commit()

    
