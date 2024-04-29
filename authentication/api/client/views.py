from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi import HTTPException
from fastapi import status

from api.client.schemas import RegisterClientRequest, RegisterClientResponse
from api.dependancies import get_client_service, get_user_service
from api.schemas import ErrorSchema
from models.base import FieldValidationError
from services.base import UniquenessError
from services.client_service import ClientService
from services.user_service import UserService

CLIENT_URL_NAME = "client"
CLIENT_URL_CREATE = "/create/"

router = APIRouter(
    prefix=f"/{CLIENT_URL_NAME}",
    tags=[CLIENT_URL_NAME],
    responses={400: {"model": ErrorSchema}},
)


@router.post(CLIENT_URL_CREATE)
async def register(
        data: RegisterClientRequest,
        user_service: Annotated[UserService, Depends(get_user_service)],
        client_service: Annotated[ClientService, Depends(get_client_service)]
) -> RegisterClientResponse:
    user = await user_service.get_user_by_username(data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found")
    try:
        client = await client_service.create(
            user=user,
            name=data.client_name,
        )
    except (UniquenessError, FieldValidationError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return RegisterClientResponse(
        id=client.id,
        name=client.name,
        secret=client.secret,
        created_at=client.created_at
    )
