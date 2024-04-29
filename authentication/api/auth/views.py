from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends

from api.auth.schemas import CredentialsRequest, TokenResponse, AuthorizationResponse, \
    CodeTokenRequest, PasswordTokenRequestForm, RefreshRequest
from api.dependencies import get_auth_service
from api.schemas import ErrorSchema
from env import get_develop_mode
from services.authentication_serivce import AuthenticationService, AuthenticationError

AUTH_URL_NAME = "auth"

AUTH_URL_GET_AUTHORIZATION_URI = "/get-auth-uri"
AUTH_URL_TOKEN_PASSWORD = "/token-password/"

AUTH_URL_TOKEN_CODE = "/token-code/"
AUTH_URL_CALLBACK_CODE = "/login-code/"

AUTH_URL_REFRESH = "/refresh/"

router = APIRouter(
    prefix=f"/{AUTH_URL_NAME}",
    tags=[AUTH_URL_NAME],
    responses={400: {"model": ErrorSchema}},
)


# Move common things into dependencies (service, session etc)
@router.get(AUTH_URL_GET_AUTHORIZATION_URI)
async def code_auth_url(client_id: int, redirect_uri: str) -> AuthorizationResponse:
    return AuthorizationResponse(
        redirect_uri=AuthenticationService.get_auth_uri(client_id, redirect_uri)
    )


@router.post(AUTH_URL_CALLBACK_CODE)
async def callback_code(
        client_id: int, redirect_uri: str,
        user_credentials: CredentialsRequest,
        auth_service: Annotated[AuthenticationService, Depends(get_auth_service)]
) -> AuthorizationResponse:
    try:
        await auth_service.authenticate_user(
            username=user_credentials.username,
            password=user_credentials.password
        )
        code = await auth_service.generate_code(
            client_id=client_id,
            redirect_uri=redirect_uri
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return AuthorizationResponse(
        redirect_uri=auth_service.get_callback_uri(code)
    )


@router.post(AUTH_URL_TOKEN_CODE)
async def token_code(
        data: CodeTokenRequest,
        auth_service: Annotated[AuthenticationService, Depends(get_auth_service)]
) -> TokenResponse:
    try:
        access_token, refresh_token = await auth_service.create_code_pair(
            client_id=data.client_id,
            client_secret=data.client_secret,
            redirect_uri=data.redirect_uri,
            value=data.code
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post(AUTH_URL_TOKEN_PASSWORD)
async def token_password(
        data: Annotated[PasswordTokenRequestForm, Depends()],
        auth_service: Annotated[AuthenticationService, Depends(get_auth_service)],
        develop_mode: Annotated[bool, Depends(get_develop_mode)]
) -> TokenResponse:
    if not develop_mode:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only available in the develop mode")
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


@router.post(AUTH_URL_REFRESH)
async def refresh(
        data: RefreshRequest,
        auth_service: Annotated[AuthenticationService, Depends(get_auth_service)]
) -> TokenResponse:
    try:
        access_token, refresh_token = await auth_service.refresh_pair(
            refresh_token=data.refresh_token,
            client_id=data.client_id,
            client_secret=data.client_secret
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )
