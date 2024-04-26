from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from api.auth.views import authenticate
from api.schemas import HTTPExceptionSchema, MessageSchema
from api.user.schemas import UserResponse, SetPasswordRequest
from config import get_session
from models.user import User
from services.password_service.validators import PasswordValidationError
from services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={400: {"model": HTTPExceptionSchema}},
)


@router.get("/e/", response_model=UserResponse)
async def read_users_me(
        current_user: Annotated[User, Depends(authenticate)],
):
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        created_at=current_user.created_at
    )


@router.post("/set-password")
async def get_me(data: SetPasswordRequest, user: Annotated[User, Depends(authenticate)]) -> MessageSchema:
    session = get_session()
    async with session:
        service = UserService(session)
        try:
            await service.set_password(user, data.new_password)
        except PasswordValidationError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return MessageSchema(detail="Password set")
