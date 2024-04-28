import traceback

from fastapi import FastAPI, Request, status, Response
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware

from api.auth.views import router as auth_router
from api.client.views import router as client_router
from api.user.views import router as user_router
from config import ADAPTERS, get_test_database_url
from migrations.operations import migrate_head

migrate_head(get_test_database_url(ADAPTERS.SYNC))
app = FastAPI()

origins = [
    "http://localhost:3000",
]

for router in [auth_router, user_router, client_router]:
    app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# TODO handle exception in dev mode
# TODO do something about content (does not show in a response)
@app.exception_handler(Exception)
async def server_error(request: Request, error: Exception):
    traceback.print_exc()
    return Response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder({
            "message": "...",
            "exception": [str(error)],
            "endpoint": request.url
        })
    )
