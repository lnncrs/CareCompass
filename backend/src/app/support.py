"""Contatos públicos configuráveis; esta consulta não realiza ligações."""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Situation = Literal["medical", "violence", "fire_rescue", "shelter", "women_support"]


class SupportContact(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: str
    name: str
    phone: str = Field(pattern=r"^\d{3}$")
    situation: Situation
    emergency: bool
    purpose: str
    coverage: str
    source_url: str
    checked_on: str


class SupportCatalog(BaseModel):
    contacts: tuple[SupportContact, ...]

    @model_validator(mode="after")
    def unique_ids(self) -> "SupportCatalog":
        if len({item.id for item in self.contacts}) != len(self.contacts):
            raise ValueError("Contatos duplicados.")
        return self

    @classmethod
    def load(cls, path: Path) -> "SupportCatalog":
        return cls.model_validate_json(path.read_text(encoding="utf-8"))

    def lookup(self, situation: Situation) -> list[SupportContact]:
        return [item for item in self.contacts if item.situation == situation]


class Urgency(BaseModel):
    detected: bool = False
    category: Situation | None = None
    contact_ids: list[str] = Field(default_factory=list)
    contacts: list[SupportContact] = Field(default_factory=list)
