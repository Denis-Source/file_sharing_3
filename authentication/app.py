from fastapi import FastAPI, Request, status, Response
from fastapi.encoders import jsonable_encoder

from api.auth.views import router as auth_router
from api.user.views import router as user_router
from config import ADAPTERS, get_test_database_url
from migrations.operations import migrate_head

migrate_head(get_test_database_url(ADAPTERS.SYNC))
app = FastAPI()
app.include_router(auth_router)
app.include_router(user_router)


@app.exception_handler(Exception)
async def server_error(request: Request, error: Exception):
    return Response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder({
            "message": "...",
            "exception": [str(error)],
            "endpoint": request.url
        })
    )
