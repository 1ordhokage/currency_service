from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from src.schemas.token import TokenSchema
from src.schemas.user import UserCreateSchema, UserResponseSchema
from src.services.auth_service import AuthService
from src.tasks.tasks import send_welcome_email


router = APIRouter(
    prefix="/auth",
    tags=["Auth controller"]
)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponseSchema
)
async def register(schema: UserCreateSchema, service: AuthService = Depends()):
    user = await service.create_user(schema)
    send_welcome_email.delay(schema.email)
    return user


@router.post("/token", response_model=TokenSchema)
async def login(
    schema: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends()
):
    token = await service.login(schema.username, schema.password)
    return token
