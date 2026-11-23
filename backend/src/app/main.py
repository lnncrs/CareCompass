from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.chat import ChatRequest, ChatResponse, echo_reply
from app.config import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or Settings()

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        application.state.settings = config
        yield

    application = FastAPI(title=config.app_name, version="0.1.0", lifespan=lifespan)

    @application.get("/api/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "mode": "echo"}

    @application.post("/api/chat", response_model=ChatResponse)
    async def chat(request: ChatRequest) -> ChatResponse:
        return echo_reply(request)

    return application


app = create_app()
