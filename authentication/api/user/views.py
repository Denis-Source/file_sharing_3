from enum import Enum
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from api.auth.dependencies import authenticate
from api.dependencies import get_user_service
from api.schemas import ErrorSchema, MessageResponse
from api.user.schemas import UserResponse, SetPasswordRequest, RegisterRequest, RegisterResponse
from models.base import FieldValidationError
from models.user import User
from services.base import UniquenessError
from services.password_service.validators import PasswordValidationError
from services.user_service import UserService

USER_URL_NAME = "users"


class UserRoutes(str, Enum):
    REGISTER = "/register/"
    PROFILE = "/profile/"
    SET_PASSWORD = "/set-password/"


router = APIRouter(
    prefix=f"/{USER_URL_NAME}",
    tags=[USER_URL_NAME],
    responses={400: {"model": ErrorSchema}},
)


@router.post(UserRoutes.REGISTER)
async def register(
        data: RegisterRequest,
        user_service: Annotated[UserService, Depends(get_user_service)]
) -> RegisterResponse:
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


@router.get(UserRoutes.PROFILE, response_model=UserResponse)
async def profile(
        current_user: Annotated[User, Depends(authenticate)],
):
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        created_at=current_user.created_at
    )


@router.post(UserRoutes.SET_PASSWORD)
async def set_password(
        data: SetPasswordRequest,
        user: Annotated[User, Depends(authenticate)],
        user_service: Annotated[UserService, Depends(get_user_service)]
) -> MessageResponse:
    try:
        await user_service.set_password(user, data.new_password)
    except PasswordValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return MessageResponse(detail="Password set")
