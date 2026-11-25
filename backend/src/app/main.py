from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request

from app.agent import ChatEngine, create_engine, load_prompt
from app.catalog import Catalog, EquipmentType, ServicesResponse, Zone
from app.chat import ChatRequest, ChatResponse, echo_reply
from app.config import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or Settings()

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        application.state.settings = config
        application.state.catalog = Catalog.load(config.catalog_path)
        application.state.prompt = load_prompt(config.prompt_path)
        application.state.engine = (
            create_engine(config, application.state.catalog, application.state.prompt)
            if config.chat_engine == "langgraph"
            else None
        )
        yield

    application = FastAPI(title=config.app_name, version="0.1.0", lifespan=lifespan)

    @application.get("/api/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "mode": config.chat_engine}

    @application.post("/api/chat", response_model=ChatResponse)
    async def chat(payload: ChatRequest, request: Request) -> ChatResponse:
        engine: ChatEngine | None = request.app.state.engine
        if engine is None:
            return echo_reply(payload)
        try:
            return await engine.respond(payload)
        except TimeoutError:
            raise HTTPException(
                504, "O assistente demorou a responder. Tente novamente."
            ) from None
        except Exception:  # noqa: BLE001 - fronteira HTTP: não expor erros do provedor/secrets.
            raise HTTPException(
                502, "Não foi possível obter uma resposta do assistente."
            ) from None

    @application.get("/api/services", response_model=ServicesResponse)
    async def services(
        zone: Zone, request: Request, equipment_type: EquipmentType | None = None
    ) -> ServicesResponse:
        catalog: Catalog = request.app.state.catalog
        return ServicesResponse(
            zone=zone, services=catalog.list_services(zone, equipment_type)
        )

    return application


app = create_app()
