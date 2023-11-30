from fastapi import APIRouter, Depends, status

from src.schemas.token import TokenPayloadSchema
from src.schemas.user import UserUpdateSchema, UserResponseSchema
from src.services.auth_service import AuthService
from src.token.token import Token


router = APIRouter(
    prefix="/users",
    tags=["Users controller"]
)


@router.get("/me", response_model=UserResponseSchema)
async def get_user(
    user_info: TokenPayloadSchema = Depends(Token.verify_token),
    service: AuthService = Depends()
):
    user = await service.read_user(id=int(user_info.sub))
    return user


@router.put("/me", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(
    schema: UserUpdateSchema,
    user_info: TokenPayloadSchema = Depends(Token.verify_token),
    service: AuthService = Depends(),
    
):
    await service.update_user(int(user_info.sub), schema)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_info: TokenPayloadSchema = Depends(Token.verify_token),
    service: AuthService = Depends()
):
    await service.delete_user(int(user_info.sub))
