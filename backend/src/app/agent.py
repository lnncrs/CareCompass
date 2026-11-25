"""Execução por turno, sem checkpointer ou histórico persistido no servidor."""

import asyncio
import json
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Literal, Protocol
from urllib.parse import urlparse

from langchain_core.messages import (
    AIMessage,
    AnyMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_core.tools import BaseTool, tool
from langchain_openai import ChatOpenAI
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langsmith import tracing_context

from app.catalog import Catalog, EquipmentType, Zone
from app.chat import ChatMessage, ChatRequest, ChatResponse
from app.config import Settings
from app.support import Situation, SupportCatalog, Urgency

ModelCall = Callable[[list[BaseMessage], list[BaseTool]], Awaitable[BaseMessage]]


class ChatEngine(Protocol):
    async def respond(self, request: ChatRequest) -> ChatResponse: ...


def load_prompt(path: Path) -> str:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError("O arquivo de prompt está vazio.")
    return text


def catalog_tool(catalog: Catalog, active_zone: Zone) -> BaseTool:
    @tool
    def list_services(zone: Zone, equipment_type: EquipmentType | None = None) -> str:
        """Liste equipamentos da zona ativa. Para buscar CRAS, use equipment_type='cras'."""
        if zone != active_zone:
            return json.dumps({"error": "zone_mismatch", "active_zone": active_zone})
        return json.dumps(
            {
                "zone": active_zone,
                "services": [
                    item.model_dump()
                    for item in catalog.list_services(active_zone, equipment_type)
                ],
            },
            ensure_ascii=False,
        )

    return list_services


class LangGraphEngine:
    def __init__(
        self, catalog: Catalog, prompt: str, call_model: ModelCall, settings: Settings
    ):
        self.catalog = catalog
        self.prompt = prompt
        self.call_model = call_model
        self.settings = settings
        self.support = SupportCatalog.load(settings.support_contacts_path)

    async def respond(self, request: ChatRequest) -> ChatResponse:
        urgency = Urgency()

        @tool
        def get_support_contacts(situation: Situation, urgent: bool = False) -> str:
            """Consulte contatos oficiais. Use urgent=true somente ao identificar risco imediato; também sinaliza a interface. Não realiza ligações."""
            contacts = self.support.lookup(situation)
            if urgent:
                emergency_contacts = [item for item in contacts if item.emergency]
                if not emergency_contacts:
                    return json.dumps(
                        {
                            "error": "not_emergency_channel",
                            "hint": "Use medical, violence ou fire_rescue para risco imediato.",
                        }
                    )
                urgency.detected = True
                urgency.category = situation
                for item in emergency_contacts:
                    if item.id not in urgency.contact_ids:
                        urgency.contact_ids.append(item.id)
                        urgency.contacts.append(item)
            return json.dumps(
                {
                    "situation": situation,
                    "contacts": [item.model_dump() for item in contacts],
                },
                ensure_ascii=False,
            )

        @tool
        def simulate_disguised_help(stage: Literal["identify", "confirm"]) -> str:
            """Sinalize o cenário fictício de socorro disfarçado de pedido de pizza. Não faz pedidos nem aciona serviços. confirm apenas após endereço fictício."""
            contacts = [
                item for item in self.support.lookup("violence") if item.emergency
            ]
            if not contacts:
                return json.dumps({"error": "missing_emergency_contact"})
            urgency.detected = True
            urgency.category = "violence"
            for item in contacts:
                if item.id not in urgency.contact_ids:
                    urgency.contact_ids.append(item.id)
                    urgency.contacts.append(item)
            return json.dumps(
                {
                    "simulation": True,
                    "external_action": False,
                    "stage": stage,
                    "delivery_status": "confirmed_in_simulation"
                    if stage == "confirm"
                    else "awaiting_fictional_location",
                }
            )

        tools = [
            catalog_tool(self.catalog, request.zone),
            get_support_contacts,
            simulate_disguised_help,
        ]

        async def assistant(state: MessagesState):
            instruction = SystemMessage(
                content=(
                    self.prompt + "\n\nCONTEXTO DA APLICAÇÃO\n"
                    f"Zona ativa: {request.zone}. Esta seleção prevalece sobre zonas no histórico.\n"
                    "Contatos oficiais disponíveis pela tool get_support_contacts. "
                    "A tool registra a sinalização visual quando urgent=true; não realiza ligações."
                )
            )
            response = await self.call_model([instruction, *state["messages"]], tools)
            return {"messages": [response]}

        graph = StateGraph(MessagesState)
        graph.add_node("assistant", assistant)
        graph.add_node("tools", ToolNode(tools))
        graph.add_edge(START, "assistant")
        graph.add_conditional_edges("assistant", tools_condition)
        graph.add_edge("tools", "assistant")
        workflow = graph.compile()
        history: list[AnyMessage] = [
            HumanMessage(content=item.content)
            if item.role == "user"
            else AIMessage(content=item.content)
            for item in request.messages
        ]
        # Se a tool já sinalizou urgência, uma falha posterior não deve apagar o aviso.
        try:
            with tracing_context(enabled=False):
                async with asyncio.timeout(self.settings.agent_timeout_seconds):
                    state: MessagesState = {"messages": history}
                    result = await workflow.ainvoke(
                        state,
                        {"recursion_limit": self.settings.agent_max_steps},
                    )
            last = result["messages"][-1]
        except Exception:  # Preservar sinalização já confirmada pela tool.
            if not urgency.detected:
                raise
            contacts_text = "; ".join(
                f"{item.name}: {item.phone}" for item in urgency.contacts
            )
            last = AIMessage(
                content=f"Possível urgência identificada. Contatos disponíveis: {contacts_text}. Não consegui completar a resposta; nenhum serviço foi acionado."
            )
        if (
            not isinstance(last, AIMessage)
            or not isinstance(last.content, str)
            or not last.content.strip()
        ):
            raise ValueError("O modelo não produziu resposta textual.")
        return ChatResponse(
            urgency=urgency,
            zone=request.zone,
            mode="langgraph",
            message=ChatMessage(
                role="assistant",
                content=last.content,
            ),
        )


def create_engine(settings: Settings, catalog: Catalog, prompt: str) -> ChatEngine:
    if (
        not settings.foundry_base_url
        or not settings.foundry_deployment
        or not settings.foundry_api_key
    ):
        raise ValueError(
            "Configure CARECOMPASS_FOUNDRY_BASE_URL, CARECOMPASS_FOUNDRY_DEPLOYMENT e CARECOMPASS_FOUNDRY_API_KEY para usar langgraph."
        )
    parsed = urlparse(settings.foundry_base_url)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or not parsed.path.rstrip("/").endswith("/openai/v1")
    ):
        raise ValueError(
            "FOUNDRY_BASE_URL deve ser uma URL HTTPS de inferência terminada em /openai/v1/, sem credenciais ou parâmetros."
        )
    model = ChatOpenAI(
        model=settings.foundry_deployment,
        base_url=settings.foundry_base_url,
        api_key=settings.foundry_api_key,
        timeout=settings.agent_timeout_seconds,
        max_retries=0,
        max_completion_tokens=settings.agent_max_output_tokens,
        use_responses_api=False,
    )

    async def call_model(
        messages: list[BaseMessage], tools: list[BaseTool]
    ) -> BaseMessage:
        return await model.bind_tools(tools).ainvoke(messages)

    return LangGraphEngine(catalog, prompt, call_model, settings)
