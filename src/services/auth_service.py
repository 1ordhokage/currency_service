from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import get_async_session
from src.models.users import User
from src.schemas.token import TokenPayloadSchema, TokenSchema
from src.schemas.user import UserRequestSchema
from src.token.config import jwt_settings
from src.token.token import Token


class AuthService:
    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self.session = session
    
    async def read_user(self, id: int = None, email: str = None) -> User:
        if id:
            result = await self.session.execute(
                select(User)
                .where(User.id == id)
            )
        if email:
            result = await self.session.execute(
                select(User)
                .where(User.email == email)
            )
        user = result.scalar()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    
    async def create_user(self, schema: UserRequestSchema) -> User:
        user = User(
            email=schema.email,
            password_hashed=Token.get_password_hash(schema.text_password),
        )
        try:
            self.session.add(user)
            await self.session.commit()
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with email '{user.email}' already exists"
            )
        return user
        
    async def login(self, username: str, password_text: str) -> TokenSchema:
        try:
            user = await self.read_user(email=username)
        except HTTPException:
            user = None
        if not user or not Token.verify_password(password_text, user.password_hashed):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        now = datetime.now()
        payload = TokenPayloadSchema(
            iat=now,
            exp=now + timedelta(minutes=jwt_settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            sub=str(user.id),
        )
        return Token.create_token(payload)

    async def update_user(self, id: int, schema: UserRequestSchema) -> None:
        user = await self.read_user(id)
        try:
            user.email = schema.email
            user.password_hashed = Token.get_password_hash(schema.text_password)
            await self.session.commit()
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with email '{schema.email}' already exists"
            )
    
    async def delete_user(self, id: int) -> None:
        await self.session.execute(
            delete(User)
            .where(User.id == id)
        )
        await self.session.commit()
