"""Testes devem ser independentes das credenciais locais do desenvolvedor."""

import os

import pytest

from app.config import Settings


@pytest.fixture(autouse=True)
def isolate_local_configuration(monkeypatch):
    monkeypatch.setitem(Settings.model_config, "env_file", None)
    for name in list(os.environ):
        if name.startswith("CARECOMPASS_"):
            monkeypatch.delenv(name)
