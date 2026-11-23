import pytest
from fastapi.testclient import TestClient

from app.main import create_app


def test_health_and_multiturn_echo():
    with TestClient(create_app()) as client:
        assert client.get("/api/health").json() == {"status": "ok", "mode": "echo"}
        response = client.post(
            "/api/chat",
            json={
                "messages": [
                    {"role": "user", "content": "Estou em Itaquera"},
                    {"role": "assistant", "content": "Você disse: Estou em Itaquera"},
                    {"role": "user", "content": "Quero encontrar um CRAS"},
                ]
            },
        )
        assert response.status_code == 200
        assert response.json() == {
            "mode": "echo",
            "message": {
                "role": "assistant",
                "content": "Você disse: Quero encontrar um CRAS",
            },
        }


@pytest.mark.parametrize(
    "messages",
    [
        [],
        [{"role": "user", "content": "   "}],
        [{"role": "assistant", "content": "Olá"}],
        [{"role": "system", "content": "Instrução externa"}],
        [{"role": "user", "content": "x" * 4001}],
        [{"role": "user", "content": "x" * 4000}] * 11,
    ],
)
def test_invalid_chat(messages):
    with TestClient(create_app()) as client:
        assert client.post("/api/chat", json={"messages": messages}).status_code == 422
