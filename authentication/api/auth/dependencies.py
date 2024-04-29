from typing import Annotated

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

from api.auth.views import AUTH_URL_NAME, AUTH_URL_TOKEN_PASSWORD
from api.dependencies import get_auth_service
from models.user import User
from services.authentication_serivce import AuthenticationService, AuthenticationError

oauth2_password_scheme = OAuth2PasswordBearer(tokenUrl=AUTH_URL_NAME + AUTH_URL_TOKEN_PASSWORD)


async def authenticate(
        token: Annotated[str, Depends(oauth2_password_scheme)],
        auth_service: Annotated[AuthenticationService, Depends(get_auth_service)]
) -> User:
    try:
        return await auth_service.get_user_by_token(token)
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
