"""Consulta determinística ao catálogo, independente de HTTP e de motores de IA."""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

Zone = Literal["centro", "leste", "norte", "sul", "oeste"]
EquipmentType = Literal[
    "cozinha_cidada",
    "bom_prato",
    "acolhida",
    "caps_adulto",
    "caps_ad",
    "caps_ij",
    "cras",
]


class Provenance(BaseModel):
    url: str
    checked_on: str
    source_note: str | None = None


class Service(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: str
    name: str
    zone: Zone
    category: Literal["food", "shelter", "mental_health", "social_assistance"]
    type: EquipmentType
    address: str
    description: str
    provenance: Provenance


class Catalog(BaseModel):
    services: tuple[Service, ...]

    @classmethod
    def load(cls, path: Path) -> "Catalog":
        return cls.model_validate_json(path.read_text(encoding="utf-8"))

    def list_services(
        self, zone: Zone, equipment_type: EquipmentType | None = None
    ) -> list[Service]:
        return [
            service
            for service in self.services
            if service.zone == zone
            and (equipment_type is None or service.type == equipment_type)
        ]


class ServicesResponse(BaseModel):
    zone: Zone
    services: list[Service]
