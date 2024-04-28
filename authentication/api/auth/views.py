from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends

from api.auth.schemas import CredentialsRequest, TokenResponse, AuthorizationResponse, \
    CodeTokenRequest, PasswordTokenRequestForm
from api.schemas import ErrorSchema
from config import get_session
from services.authentication_serivce import AuthenticationService, AuthenticationError

AUTH_URL_NAME = "auth"

AUTH_URL_GET_AUTHORIZATION_URL = "/get-auth-url"
AUTH_URL_TOKEN_PASSWORD = "/token-password/"

AUTH_URL_TOKEN_CODE = "/token-code/"
AUTH_URL_CALLBACK_CODE = "/login-code/"

router = APIRouter(
    prefix=f"/{AUTH_URL_NAME}",
    tags=[AUTH_URL_NAME],
    responses={400: {"model": ErrorSchema}},
)


@router.get(AUTH_URL_GET_AUTHORIZATION_URL)
async def code_auth_url(client_id: int, redirect_uri: str) -> AuthorizationResponse:
    return AuthorizationResponse(
        redirect_uri=AuthenticationService.get_auth_uri(client_id, redirect_uri)
    )


@router.post(AUTH_URL_CALLBACK_CODE)
async def callback_code(client_id: int, redirect_uri: str,
                        user_credentials: CredentialsRequest) -> AuthorizationResponse:
    session = get_session()
    async with session:
        auth_service = AuthenticationService(session)
        try:
            await auth_service.authenticate_user(
                username=user_credentials.username,
                password=user_credentials.password
            )
            code = await auth_service.generate_code(
                client_id=client_id,
                redirect_uri=redirect_uri
            )
            return AuthorizationResponse(
                redirect_uri=auth_service.get_callback_uri(code)
            )
        except AuthenticationError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(AUTH_URL_TOKEN_CODE)
async def token_code(data: CodeTokenRequest) -> TokenResponse:
    session = get_session()
    async with session:
        auth_service = AuthenticationService(session)
        try:
            access_token, refresh_token = await auth_service.create_code_pair(
                client_id=data.client_id,
                client_secret=data.client_secret,
                redirect_uri=data.redirect_uri,
                value=data.code
            )
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer"
            )
        except AuthenticationError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# TODO Only allow in a develop mode
@router.post(AUTH_URL_TOKEN_PASSWORD)
async def token_password(
        data: Annotated[PasswordTokenRequestForm, Depends()],
) -> TokenResponse:
    session = get_session()
    async with session:
        auth_service = AuthenticationService(session)
        # TODO what if client id cannot be cast into int
        try:
            access_token, _ = await auth_service.create_password_pair(
                username=data.username,
                password=data.password,
                client_id=data.client_id,
                client_secret=data.client_secret
            )
        except AuthenticationError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        return TokenResponse(
            access_token=access_token,
            refresh_token=None,
            token_type="bearer"
        )
