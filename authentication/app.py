import traceback

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from api.auth.views import router as auth_router
from api.client.views import router as client_router
from api.schemas import MessageResponse
from api.user.views import router as user_router
from config import ADAPTERS, get_test_database_url
from env import get_develop_mode, get_frontend_url
from migrations.operations import migrate_head

migrate_head(get_test_database_url(ADAPTERS.SYNC))
app = FastAPI()

origins = [
    get_frontend_url()
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


@app.exception_handler(500)
async def internal_exception_handler(request: Request, exc: Exception):
    if get_develop_mode():
        traceback.print_exc()
    return JSONResponse(
        content=jsonable_encoder(MessageResponse(
            detail="Internal Server Error")),
        status_code=500
    )
