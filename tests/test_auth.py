from httpx import AsyncClient

from sqlalchemy import insert, select

from src.models.users import User
from src.utils.roles import RoleEnum

from tests.conftest import async_session_maker


async def test_register(ac: AsyncClient):
    body = {
        "email": "test@mail.com",
        "text_password": "stringst",
        "role": "admin"
    }
    
    response = await ac.post("/auth/register", json=body)
    assert response.status_code == 201
    
    async with async_session_maker() as session:
        result = await session.execute(
            select(User)
            .where(User.email == "test@mail.com")
        )
        assert result.scalar().id == 1


# async def test_login(ac: AsyncClient):
#     response = await ac.post(
#         "/auth/register",

#         headers={
#             'accept': 'application/json',
#             'Content-Type': 'application/x-www-form-urlencoded'
#         },
#         data={
#             'grant_type': '',
#             'username': 'test@mail.com',
#             'password': 'stringst',
#             'scope': '',
#             'client_id': '',
#             'client_secret': ''
#         }
#     )
#     assert response.status_code == 200
