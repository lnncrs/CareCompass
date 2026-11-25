import asyncio
import json

import pytest
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.errors import GraphRecursionError

from app.agent import LangGraphEngine, catalog_tool, create_engine, load_prompt
from app.catalog import Catalog
from app.chat import ChatMessage, ChatRequest, ChatResponse
from app.config import Settings
from app.main import create_app


def test_tool_enforces_active_zone():
    catalog = Catalog.load(Settings().catalog_path)
    tool = catalog_tool(catalog, "norte")
    result = json.loads(tool.invoke({"zone": "norte"}))
    assert len(result["services"]) == 8
    assert all(item["zone"] == "norte" for item in result["services"])
    assert json.loads(tool.invoke({"zone": "leste"})) == {
        "error": "zone_mismatch",
        "active_zone": "norte",
    }


def test_real_graph_calls_tool_and_preserves_history_without_persistence():
    catalog = Catalog.load(Settings().catalog_path)
    calls = []

    async def model(messages, tools):
        calls.append(messages)
        assert "Zona ativa: norte" in messages[0].content
        if not isinstance(messages[-1], ToolMessage):
            return AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "list_services",
                        "args": {"zone": "norte"},
                        "id": "lookup",
                    }
                ],
            )
        data = json.loads(messages[-1].content)
        return AIMessage(content=f"Uma opção é {data['services'][0]['name']}.")

    engine = LangGraphEngine(catalog, "Prompt de teste", model, Settings())
    request = ChatRequest(
        zone="norte",
        messages=[
            ChatMessage(role="user", content="Estou na Leste"),
            ChatMessage(role="assistant", content="Como posso ajudar?"),
            ChatMessage(role="user", content="Comida"),
        ],
    )
    response = asyncio.run(engine.respond(request))
    assert response.mode == "langgraph"
    assert response.zone == "norte"
    assert "Zaki Narchi" in response.message.content
    assert isinstance(calls[0][1], HumanMessage)
    assert calls[0][1].content == "Estou na Leste"
    assert len(calls[0]) == 4
    calls.clear()
    asyncio.run(
        engine.respond(
            ChatRequest(zone="norte", messages=[ChatMessage(role="user", content="Oi")])
        )
    )
    assert len(calls[0]) == 2


def test_loop_is_bounded():
    async def looping_model(messages, tools):
        return AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "list_services",
                    "args": {"zone": "norte"},
                    "id": "loop",
                }
            ],
        )

    settings = Settings(agent_max_steps=2)
    engine = LangGraphEngine(
        Catalog.load(settings.catalog_path), "Prompt", looping_model, settings
    )
    with pytest.raises(GraphRecursionError):
        asyncio.run(
            engine.respond(
                ChatRequest(
                    zone="norte", messages=[ChatMessage(role="user", content="Oi")]
                )
            )
        )


def test_turn_timeout():
    async def slow_model(messages, tools):
        await asyncio.sleep(1)
        return AIMessage(content="Oi")

    settings = Settings(agent_timeout_seconds=0.01)
    engine = LangGraphEngine(
        Catalog.load(settings.catalog_path), "Prompt", slow_model, settings
    )
    with pytest.raises(TimeoutError):
        asyncio.run(
            engine.respond(
                ChatRequest(
                    zone="norte", messages=[ChatMessage(role="user", content="Oi")]
                )
            )
        )


def test_missing_configuration_and_prompt(tmp_path):
    settings = Settings(
        foundry_base_url=None, foundry_deployment=None, foundry_api_key=None
    )
    with pytest.raises(ValueError, match="FOUNDRY_BASE_URL"):
        create_engine(settings, Catalog.load(settings.catalog_path), "Prompt")
    path = tmp_path / "empty.md"
    path.write_text("  ", encoding="utf-8")
    with pytest.raises(ValueError, match="vazio"):
        load_prompt(path)
    with pytest.raises(FileNotFoundError):
        load_prompt(tmp_path / "absent.md")


def test_prompt_loaded_once_at_startup(monkeypatch, tmp_path):
    path = tmp_path / "prompt.md"
    path.write_text("Versão inicial", encoding="utf-8")
    loaded = []

    class FakeEngine:
        async def respond(self, request):
            return ChatResponse(
                zone=request.zone,
                mode="langgraph",
                message=ChatMessage(role="assistant", content=loaded[-1]),
            )

    def factory(settings, catalog, prompt):
        loaded.append(prompt)
        return FakeEngine()

    monkeypatch.setattr("app.main.create_engine", factory)
    app = create_app(Settings(chat_engine="langgraph", prompt_path=path))
    payload = {"zone": "leste", "messages": [{"role": "user", "content": "Oi"}]}
    with TestClient(app) as client:
        path.write_text("Versão alterada", encoding="utf-8")
        assert client.get("/api/health").json()["mode"] == "langgraph"
        assert (
            client.post("/api/chat", json=payload).json()["message"]["content"]
            == "Versão inicial"
        )
        assert client.post("/api/chat", json=payload).status_code == 200
    assert loaded == ["Versão inicial"]
    with TestClient(app) as client:
        assert (
            client.post("/api/chat", json=payload).json()["message"]["content"]
            == "Versão alterada"
        )


@pytest.mark.parametrize(
    "error,status", [(TimeoutError("secret"), 504), (RuntimeError("secret"), 502)]
)
def test_provider_errors_do_not_expose_details(monkeypatch, error, status):
    class BrokenEngine:
        async def respond(self, request):
            raise error

    monkeypatch.setattr("app.main.create_engine", lambda *args: BrokenEngine())
    with TestClient(create_app(Settings(chat_engine="langgraph"))) as client:
        response = client.post(
            "/api/chat",
            json={"zone": "norte", "messages": [{"role": "user", "content": "Oi"}]},
        )
        assert response.status_code == status
        assert "secret" not in response.text
