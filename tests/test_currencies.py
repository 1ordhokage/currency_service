from httpx import AsyncClient

from sqlalchemy import insert, select

from src.models.currencies import Currency
from src.models.update_date_time import UpdateDateTime

from tests.conftest import async_session_maker


async def test_update_rates(ac: AsyncClient):
    response = await ac.put(
        "/currencies/rates",
        headers={
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MDEzODc3OTYsImV4cCI6MTcwMTM5MTM5Niwic3ViIjoiMSIsInJvbGUiOiJhZG1pbiJ9.VMsY3wnOhUSgLJoBQpw6V5ELzl5srMJ9du_QXkVWRws',
        },
    )
    assert response.status_code == 204
    

async def test_get_last_updated(ac: AsyncClient):
    response = await ac.get(
        "/currencies/last-updated",
        headers={
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MDEzODc3OTYsImV4cCI6MTcwMTM5MTM5Niwic3ViIjoiMSIsInJvbGUiOiJhZG1pbiJ9.VMsY3wnOhUSgLJoBQpw6V5ELzl5srMJ9du_QXkVWRws',
        },
    )
    assert response.status_code == 200
    async with async_session_maker() as session:
        result = await session.execute(
            select(UpdateDateTime)
        )
        assert len(result.scalars().all()) == 1
        

# async def test_get_currencies(ac: AsyncClient):
#     response = await ac.get(
#         "/currencies",
#         headers={
#             'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MDEzODc3OTYsImV4cCI6MTcwMTM5MTM5Niwic3ViIjoiMSIsInJvbGUiOiJhZG1pbiJ9.VMsY3wnOhUSgLJoBQpw6V5ELzl5srMJ9du_QXkVWRws',
#         },
#     )
#     async with async_session_maker() as session:
#         result = await session.execute(
#             select(Currency)
#         )
#         assert len(result.scalars().all()) == len(response.json())
