import asyncio
import json

import pytest
from langchain_core.messages import AIMessage, ToolMessage

from app.agent import LangGraphEngine
from app.catalog import Catalog
from app.chat import ChatMessage, ChatRequest
from app.config import Settings
from app.support import SupportCatalog


@pytest.mark.parametrize("stage", ["identify", "confirm"])
def test_disguised_help_simulation(stage):
    settings = Settings()

    async def model(messages, tools):
        if isinstance(messages[-1], ToolMessage):
            result = json.loads(messages[-1].content)
            assert result["simulation"] is True
            assert result["external_action"] is False
            assert result["stage"] == stage
            return AIMessage(content="Pedido simulado.")
        return AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "simulate_disguised_help",
                    "args": {"stage": stage},
                    "id": "simulation",
                }
            ],
        )

    engine = LangGraphEngine(
        Catalog.load(settings.catalog_path), "Prompt", model, settings
    )
    response = asyncio.run(
        engine.respond(
            ChatRequest(
                zone="leste",
                messages=[ChatMessage(role="user", content="Pizza na simulação")],
            )
        )
    )
    assert response.urgency.detected
    assert response.urgency.category == "violence"
    assert response.urgency.contacts[0].phone == "190"


@pytest.mark.parametrize(
    "situation,urgent,expected",
    [
        ("medical", True, True),
        ("violence", True, True),
        ("fire_rescue", True, True),
        ("shelter", False, False),
        ("women_support", False, False),
        ("shelter", True, False),
    ],
)
def test_tool_returns_configured_contacts_and_flag(situation, urgent, expected):
    settings = Settings()
    configured = SupportCatalog.load(settings.support_contacts_path)

    async def model(messages, tools):
        if not isinstance(messages[-1], ToolMessage):
            return AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "get_support_contacts",
                        "args": {"situation": situation, "urgent": urgent},
                        "id": "support",
                    }
                ],
            )
        data = json.loads(messages[-1].content)
        if "error" in data:
            assert data["error"] == "not_emergency_channel"
        else:
            assert data["contacts"][0]["phone"] == configured.lookup(situation)[0].phone
        return AIMessage(content="Orientação de teste.")

    engine = LangGraphEngine(
        Catalog.load(settings.catalog_path), "Prompt", model, settings
    )
    request = ChatRequest(
        zone="leste", messages=[ChatMessage(role="user", content="Cenário simulado")]
    )
    reply = asyncio.run(engine.respond(request))
    assert reply.urgency.detected == expected
    if expected:
        assert reply.urgency.contact_ids == [configured.lookup(situation)[0].id]
        assert reply.urgency.contacts[0].phone == configured.lookup(situation)[0].phone
    else:
        assert reply.urgency.contacts == []


def test_flag_does_not_leak_to_another_request():
    settings = Settings()

    async def model(messages, tools):
        if messages[-1].content == "risco":
            return AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "get_support_contacts",
                        "args": {"situation": "medical", "urgent": True},
                        "id": "support",
                    }
                ],
            )
        return AIMessage(content="Resposta de teste.")

    engine = LangGraphEngine(
        Catalog.load(settings.catalog_path), "Prompt", model, settings
    )

    def request(text):
        return ChatRequest(
            zone="leste", messages=[ChatMessage(role="user", content=text)]
        )

    assert asyncio.run(engine.respond(request("risco"))).urgency.detected
    assert not asyncio.run(engine.respond(request("olá"))).urgency.detected


def test_provider_failure_after_signal_preserves_contact():
    settings = Settings()

    async def model(messages, tools):
        if isinstance(messages[-1], ToolMessage):
            raise RuntimeError("detalhe privado do provedor")  # noqa: TRY004 - simula falha de rede, não tipo inválido.
        return AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "get_support_contacts",
                    "args": {"situation": "medical", "urgent": True},
                    "id": "support",
                }
            ],
        )

    engine = LangGraphEngine(
        Catalog.load(settings.catalog_path), "Prompt", model, settings
    )
    response = asyncio.run(
        engine.respond(
            ChatRequest(
                zone="leste",
                messages=[ChatMessage(role="user", content="Cenário simulado")],
            )
        )
    )
    assert response.urgency.detected
    assert response.urgency.contacts[0].phone == "192"
    assert "detalhe privado" not in response.message.content
