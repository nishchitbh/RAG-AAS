import os
from dotenv import load_dotenv

from fastapi import FastAPI
from contextlib import asynccontextmanager
from api.tickets.presentation.routes import TicketRoutes
from api.company.presentation.routes import CompanyRoutes
from api.end_users.presentation.routes import EndUserRoutes
from api.chat.presentation.routes import ChatWebSocketRoute
from api.auth.presentation.routes import AuthRoutes, UserRoutes
from api.document_upload.presentation.routes import UploadRoutes
from api.notifications.presentation.routes import NotificationRoutes

from api.shared.middlewares.rate_limiter import rate_limit_middleware
from api.shared.middlewares.generic_response import generic_middleware

from api.shared.config import setting, process_executor

load_dotenv()
ENV = os.getenv("ENV", "prod").lower()
IS_PROD = ENV == "prod"


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(setting.upload_folder, exist_ok=True)
    yield
    process_executor.shutdown()


app = FastAPI(
    title="RAG As a Service",
    lifespan=lifespan,
    docs_url=None if IS_PROD else "/docs",
    redoc_url=None if IS_PROD else "/redoc",
    openapi_url=None if IS_PROD else "/openapi.json",
)

app.middleware("http")(rate_limit_middleware)
app.middleware("http")(generic_middleware)


app.include_router(AuthRoutes().router)
app.include_router(UserRoutes().router)
app.include_router(CompanyRoutes().router)
app.include_router(UploadRoutes().router)
app.include_router(NotificationRoutes().router)
app.include_router(ChatWebSocketRoute().router)
app.include_router(EndUserRoutes().router)
app.include_router(TicketRoutes().router)
