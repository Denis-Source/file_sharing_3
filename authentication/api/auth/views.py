from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from api.auth.schemas import RegisterRequest, RegisterResponse, Token
from api.schemas import HTTPExceptionSchema
from config import get_session
from models.base import FieldValidationError
from services.authentication_serivce import AuthenticationService, AuthenticationError
from services.base import UniquenessError
from services.user_service import UserService

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={400: {"model": HTTPExceptionSchema}},
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


@router.post("/register/")
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


@router.post("/token/")
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    session = get_session()
    async with session:
        auth_service = AuthenticationService(session)
        # TODO what if client id cannot be cast into int
        try:
            token = await auth_service.create_oauth_token(
                username=form_data.username,
                password=form_data.password,
                client_id=int(form_data.client_id),
                client_secret=form_data.client_secret
            )
        except AuthenticationError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return Token(access_token=token, token_type="bearer")


async def authenticate(token: Annotated[str, Depends(oauth2_scheme)]):
    session = get_session()
    async with session:
        auth_service = AuthenticationService(session)
        try:
            user = await auth_service.get_user_by_token(token)
        except AuthenticationError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return user
