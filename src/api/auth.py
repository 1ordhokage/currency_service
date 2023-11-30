from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from src.schemas.token import TokenSchema
from src.schemas.user import UserRequestSchema, UserResponseSchema
from src.services.auth_service import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["Auth controller"]
)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponseSchema
)
async def register(schema: UserRequestSchema, service: AuthService = Depends()):
    user = await service.create_user(schema)
    return user


@router.post("/token", response_model=TokenSchema)
async def login(
    schema: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends()
):
    token = await service.login(schema.username, schema.password)
    return token
