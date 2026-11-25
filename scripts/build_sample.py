"""Gera a amostra curada de 40 locais a partir dos HTMLs preservados."""

import hashlib
import json
import re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Seleção humana aprovada: dois locais de alimentação, dois de acolhida e três CAPS.
# As chaves de busca abaixo são trechos do original, não nomes inventados de unidades.
SELECTION = {
    "centro": [
        ("cozinha-cidada", "Rua Prates, 165", "food", "cozinha_cidada"),
        (
            "bom-prato-paulistano",
            "Bom Prato Paulistano Júlio Prestes",
            "food",
            "bom_prato",
        ),
        ("acolhida-centro", "CA CASA DE ASSIS", "shelter", "acolhida"),
        ("acolhida-centro", "CA 24H SANTA CECÍLIA", "shelter", "acolhida"),
        ("caps-territorios", "CAPS ADULTO III SÉ", "mental_health", "caps_adulto"),
        ("caps-territorios", "CAPS AD III CENTRO", "mental_health", "caps_ad"),
        ("caps-territorios", "CAPS IJ III SÉ", "mental_health", "caps_ij"),
    ],
    "leste": [
        ("cozinha-cidada", "Avenida Souza Ramos, 513", "food", "cozinha_cidada"),
        (
            "bom-prato-paulistano",
            "Bom Prato Refeitório Cidade Tiradentes",
            "food",
            "bom_prato",
        ),
        ("acolhida-leste", "CENTRO DE ACOLHIDA SÃO MATEUS", "shelter", "acolhida"),
        (
            "acolhida-leste",
            "CENTRO DE ACOLHIDA SÃO MIGUEL PAULISTA",
            "shelter",
            "acolhida",
        ),
        ("caps-territorios", "CAPS ADULTO II ITAQUERA", "mental_health", "caps_adulto"),
        ("caps-territorios", "CAPS AD III SÃO MATEUS", "mental_health", "caps_ad"),
        ("caps-territorios", "CAPS IJ III SÃO MIGUEL", "mental_health", "caps_ij"),
    ],
    "norte": [
        ("cozinha-cidada", "Avenida Zaki Narchi, 629", "food", "cozinha_cidada"),
        ("cozinha-cidada", "Rua Gervásio Leite Rebelo, 1073", "food", "cozinha_cidada"),
        ("acolhida-norte", "CENTRO DE ACOLHIDA CASA VERDE", "shelter", "acolhida"),
        ("acolhida-norte", "CA II POR 24 HORAS JAÇANÃ", "shelter", "acolhida"),
        (
            "caps-territorios",
            "CAPS ADULTO III MANDAQUI",
            "mental_health",
            "caps_adulto",
        ),
        ("caps-territorios", "CAPS AD III SANTANA", "mental_health", "caps_ad"),
        (
            "caps-territorios",
            "CAPS IJ III VILA MARIA / VILA GUILHERME",
            "mental_health",
            "caps_ij",
        ),
    ],
    "sul": [
        ("cozinha-cidada", "Rua Caprichoso Italiano, 20", "food", "cozinha_cidada"),
        (
            "bom-prato-paulistano",
            "Bom Prato Paulistano M’Boi Mirim / Piraporinha",
            "food",
            "bom_prato",
        ),
        ("acolhida-sul", "CENTRO DE ACOLHIDA CAMPO LIMPO", "shelter", "acolhida"),
        ("acolhida-sul", "CA SANTO AMARO", "shelter", "acolhida"),
        (
            "caps-territorios",
            "CAPS ADULTO III LARGO 13",
            "mental_health",
            "caps_adulto",
        ),
        ("caps-territorios", "CAPS AD III CAMPO LIMPO", "mental_health", "caps_ad"),
        ("caps-territorios", "CAPS IJ II SANTO AMARO", "mental_health", "caps_ij"),
    ],
    "oeste": [
        ("cozinha-cidada", "Largo da Batata", "food", "cozinha_cidada"),
        ("cozinha-cidada", "Rua dos Piemonteses, 841", "food", "cozinha_cidada"),
        ("acolhida-oeste", "CTA BUTANTÃ", "shelter", "acolhida"),
        ("acolhida-oeste", "CA ZANCONE", "shelter", "acolhida"),
        ("caps-territorios", "CAPS ADULTO III LAPA", "mental_health", "caps_adulto"),
        ("caps-territorios", "CAPS AD III BUTANTÃ", "mental_health", "caps_ad"),
        ("caps-territorios", "CAPS IJ II LAPA", "mental_health", "caps_ij"),
    ],
}

# CRAS são identificados explicitamente na fonte consolidada municipal.
CRAS = {
    "centro": "CENTRO – CRAS SÉ",
    "leste": "LESTE – CRAS ITAQUERA",
    "norte": "NORTE – CRAS CACHOEIRINHA",
    "sul": "SUL – CRAS GRAJAÚ",
    "oeste": "OESTE – CRAS BUTANTÃ",
}
for zone, source_name in CRAS.items():
    SELECTION[zone].append(("cras-capital", source_name, "social_assistance", "cras"))

DESCRIPTIONS = {
    "cras": "Centro de Referência de Assistência Social: orientação e proteção social básica.",
    "cozinha_cidada": "Ponto de distribuição de refeições da Rede Cozinha Cidadã.",
    "bom_prato": "Restaurante de alimentação a baixo custo do Bom Prato Paulistano.",
    "acolhida": "Unidade da rede de acolhimento socioassistencial.",
    "caps_adulto": "Centro de atenção psicossocial para adultos.",
    "caps_ad": "Centro de atenção psicossocial em álcool e outras drogas.",
    "caps_ij": "Centro de atenção psicossocial infantojuvenil.",
}


def normalize(text):
    return re.sub(r"\s+", " ", text.replace("\u200b", "").replace("\ufeff", "")).strip()


class SourceText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = 0
        self.lines = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = max(0, self.skip - 1)

    def handle_data(self, data):
        if not self.skip and normalize(data):
            self.lines.append(normalize(data))


def build():
    manifest = json.loads((ROOT / "data/sources.json").read_text(encoding="utf-8"))
    sources = {source["id"]: source for source in manifest["sources"]}
    texts = {}
    for source_id, source in sources.items():
        body = (ROOT / source["path"]).read_bytes()
        if hashlib.sha256(body).hexdigest() != source["sha256"]:
            raise ValueError(f"Fonte alterada: {source_id}")
        parser = SourceText()
        parser.feed(body.decode("utf-8"))
        texts[source_id] = parser.lines
    services = []
    for zone, selections in SELECTION.items():
        for number, (source_id, anchor, category, subtype) in enumerate(selections, 1):
            lines = texts[source_id]
            matches = [i for i, line in enumerate(lines) if line == anchor]
            if subtype == "cozinha_cidada":
                matches = [i for i, line in enumerate(lines) if line.startswith(anchor)]
            if len(matches) != 1:
                raise ValueError(
                    f"Âncora não é única: {source_id}: {anchor}: {matches}"
                )
            index = matches[0]
            name = lines[index]
            if subtype == "cozinha_cidada":
                address = name
                name = f"Rede Cozinha Cidadã — {anchor}"
                evidence = [address]
            elif category == "mental_health":
                if lines[index + 1] != "Endereço:":
                    raise ValueError(f"Endereço não identificado: {anchor}")
                address = lines[index + 2]
                evidence = lines[index : index + 3]
            else:
                address = lines[index + 1]
                evidence = lines[index : index + 2]
            services.append(
                {
                    "id": f"{zone}-{number:02d}",
                    "name": name.split(" – ", 1)[-1] if subtype == "cras" else name,
                    "zone": zone,
                    "category": category,
                    "type": subtype,
                    "address": address,
                    "city": "São Paulo",
                    "state": "SP",
                    "description": DESCRIPTIONS[subtype],
                    "description_basis": "Resumo editorial da categoria; não é transcrição nem oferta individual verificada.",
                    "access_instructions": None,
                    "access_note": "Forma de acesso não especificada nesta fonte de endereços; revisão complementar pendente.",
                    "zone_basis": "Seleção editorial para simulação por zona; não define abrangência de atendimento.",
                    "provenance": {
                        "source_id": source_id,
                        "source_note": "Lista consolidada municipal publicada em 15/02/2019; endereço preservado literalmente para o mock, sem confirmação operacional atual."
                        if subtype == "cras"
                        else None,
                        "url": sources[source_id]["url"],
                        "raw_path": sources[source_id]["path"],
                        "source_sha256": sources[source_id]["sha256"],
                        "collected_at_utc": sources[source_id]["attempted_at_utc"],
                        "checked_on": "2026-11-24",
                        "locator": anchor,
                        "evidence_text": " | ".join(evidence),
                    },
                }
            )
    if len(services) != 40 or Counter(
        item["zone"] for item in services
    ) != dict.fromkeys(SELECTION, 8):
        raise ValueError("Amostra deve ter 40 registros, oito por zona.")
    return {
        "schema_version": "1.0",
        "dataset_id": "carecompass-services-sample",
        "purpose": "Demonstração acadêmica de viabilidade; não é catálogo operacional.",
        "selection": "Amostra intencional: 2 alimentação, 2 acolhimento, 3 CAPS e 1 CRAS por zona.",
        "limitations": [
            "Não representa toda a rede nem comprova funcionamento atual.",
            "Endereços conferidos contra fontes preservadas; sem verificação de campo.",
            "Zona do mock não equivale à área de referência territorial da Saúde ou da Assistência Social.",
            "Sem coordenadas, cálculo de distância ou disponibilidade de vagas.",
            "Os pontos Cozinha Cidadã têm rótulos editoriais por endereço, não nomes oficiais de equipamentos.",
        ],
        "services": services,
    }


if __name__ == "__main__":
    destination = ROOT / "data/processed/services.sample.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(build(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("Amostra gerada: 40 registros, 8 por zona.")
