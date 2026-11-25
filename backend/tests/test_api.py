import pytest
from fastapi.testclient import TestClient

from app.main import create_app


def test_health_and_multiturn_echo():
    with TestClient(create_app()) as client:
        assert client.get("/api/health").json() == {"status": "ok", "mode": "echo"}
        response = client.post(
            "/api/chat",
            json={
                "zone": "leste",
                "messages": [
                    {"role": "user", "content": "Estou em Itaquera"},
                    {"role": "assistant", "content": "Você disse: Estou em Itaquera"},
                    {"role": "user", "content": "Quero encontrar um CRAS"},
                ],
            },
        )
        assert response.status_code == 200
        assert response.json() == {
            "zone": "leste",
            "mode": "echo",
            "urgency": {
                "detected": False,
                "category": None,
                "contact_ids": [],
                "contacts": [],
            },
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
        assert (
            client.post(
                "/api/chat", json={"zone": "leste", "messages": messages}
            ).status_code
            == 422
        )


@pytest.mark.parametrize("zone", ["centro", "leste", "norte", "sul", "oeste"])
def test_services_are_filtered_by_zone(zone):
    with TestClient(create_app()) as client:
        response = client.get("/api/services", params={"zone": zone})
        assert response.status_code == 200
        records = response.json()["services"]
        assert len(records) == 8
        assert all(item["zone"] == zone for item in records)
        assert all(item["address"] and item["provenance"]["url"] for item in records)


def test_zone_validation_and_switch_without_losing_history():
    messages = [{"role": "user", "content": "Estou na Leste"}]
    with TestClient(create_app()) as client:
        for zone in [None, "inexistente"]:
            params = {} if zone is None else {"zone": zone}
            assert client.get("/api/services", params=params).status_code == 422
            assert (
                client.post(
                    "/api/chat", json={**params, "messages": messages}
                ).status_code
                == 422
            )
        response = client.post(
            "/api/chat", json={"zone": "norte", "messages": messages}
        )
        assert response.status_code == 200
        assert response.json()["zone"] == "norte"


@pytest.mark.parametrize("zone", ["centro", "leste", "norte", "sul", "oeste"])
def test_one_cras_per_zone_and_filter(zone):
    with TestClient(create_app()) as client:
        response = client.get(
            "/api/services", params={"zone": zone, "equipment_type": "cras"}
        )
        assert response.status_code == 200
        records = response.json()["services"]
        assert len(records) == 1
        assert records[0]["type"] == "cras"
        assert records[0]["zone"] == zone
        assert "2019" in records[0]["provenance"]["source_note"]
        assert (
            client.get(
                "/api/services", params={"zone": zone, "equipment_type": "inventado"}
            ).status_code
            == 422
        )
