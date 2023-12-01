from httpx import AsyncClient

from sqlalchemy import insert, select

from src.models.users import User
from src.utils.roles import RoleEnum

from tests.conftest import async_session_maker


# async def test_add_user():
#     async with async_session_maker() as session:
#         await session.execute(
#             insert(User)
#             .values({
#                 "id": 1,
#                 "email": "test@mail.com",
#                 "password_hashed": "fake_hashed",
#                 "role": "admin"
#             })
#         )
#         await session.commit()
#         result = await session.execute(
#             select(User)
#             .where(User.id == 1)
#         )
#         assert result.scalar().email == "test@mail.com"
        

async def test_get_user_me(ac: AsyncClient):
    response = await ac.get(
        "/users/me",
        headers={
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MDEzODc3OTYsImV4cCI6MTcwMTM5MTM5Niwic3ViIjoiMSIsInJvbGUiOiJhZG1pbiJ9.VMsY3wnOhUSgLJoBQpw6V5ELzl5srMJ9du_QXkVWRws',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "email": "test@mail.com",
        "role": "admin"
    }
    
    
async def test_update_user_me(ac: AsyncClient):
    response = await ac.put(
        "/users/me",
        headers={
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MDEzODc3OTYsImV4cCI6MTcwMTM5MTM5Niwic3ViIjoiMSIsInJvbGUiOiJhZG1pbiJ9.VMsY3wnOhUSgLJoBQpw6V5ELzl5srMJ9du_QXkVWRws',
        },
        json={
            "email": "new@mail.com",
            "text_password": "stringst"
        }
    )
    assert response.status_code == 204
    async with async_session_maker() as session:
        result = await session.execute(
            select(User)
            .where(User.id == 1)
        )
        assert result.scalar().email == "new@mail.com"
        

async def test_delete_user_me(ac: AsyncClient):
    response = await ac.delete(
        "/users/me",
        headers={
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MDEzODc3OTYsImV4cCI6MTcwMTM5MTM5Niwic3ViIjoiMSIsInJvbGUiOiJhZG1pbiJ9.VMsY3wnOhUSgLJoBQpw6V5ELzl5srMJ9du_QXkVWRws',
        },
    )
    assert response.status_code == 204
    async with async_session_maker() as session:
        result = await session.execute(
            select(User)
        )
        assert len(result.scalars().all()) == 0
