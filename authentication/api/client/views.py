from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import status

from api.client.schemas import RegisterClientRequest, RegisterClientResponse
from api.schemas import HTTPExceptionSchema
from config import get_session
from models.base import FieldValidationError
from services.base import UniquenessError
from services.client_service import ClientService
from services.user_service import UserService

router = APIRouter(
    prefix="/client",
    tags=["client"],
    responses={400: {"model": HTTPExceptionSchema}},
)


@router.post("/create/")
async def register(data: RegisterClientRequest) -> RegisterClientResponse:
    session = get_session()

    async with session:
        user_service = UserService(session)
        client_service = ClientService(session)

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
