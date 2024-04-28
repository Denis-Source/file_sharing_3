from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from api.auth.views import authenticate
from api.schemas import ErrorSchema, MessageSchema
from api.user.schemas import UserResponse, SetPasswordRequest, RegisterRequest, RegisterResponse
from config import get_session
from models.base import FieldValidationError
from models.user import User
from services.base import UniquenessError
from services.password_service.validators import PasswordValidationError
from services.user_service import UserService

AUTH_URL_NAME = "users"
USER_URL_REGISTER = "/register/"
USER_URL_PROFILE = "/profile/"
USER_URL_SET_PASSWORD = "/set-password/"

router = APIRouter(
    prefix=f"/{AUTH_URL_NAME}",
    tags=[AUTH_URL_NAME],
    responses={400: {"model": ErrorSchema}},
)


@router.post(USER_URL_REGISTER)
async def register(data: RegisterRequest) -> RegisterResponse:
    session = get_session()

    async with session:
        user_service = UserService(session)
        try:
            user = await user_service.create(
                username=data.username,
                plain_password=data.password
            )
        except (UniquenessError, FieldValidationError) as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        return RegisterResponse(
            id=user.id,
            username=user.username,
            created_at=user.created_at
        )


@router.get(USER_URL_PROFILE, response_model=UserResponse)
async def profile(
        current_user: Annotated[User, Depends(authenticate)],
):
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        created_at=current_user.created_at
    )


@router.post(USER_URL_SET_PASSWORD)
async def set_password(data: SetPasswordRequest, user: Annotated[User, Depends(authenticate)]) -> MessageSchema:
    session = get_session()
    async with session:
        service = UserService(session)
        try:
            await service.set_password(user, data.new_password)
        except PasswordValidationError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return MessageSchema(detail="Password set")
