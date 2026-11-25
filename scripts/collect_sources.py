"""Coleta finita de fontes oficiais; não segue links nem extrai arquivos."""

import argparse
import hashlib
import json
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILE_LIMIT = 256 * 1024
TOTAL_LIMIT = 2 * 1024 * 1024
SOURCES = [
    (
        "smdhc",
        "cras-capital",
        "https://prefeitura.sp.gov.br/web/direitos_humanos/w/mulheres/rede_de_protecao/271427",
    ),
    (
        "sesana",
        "cozinha-cidada",
        "https://prefeitura.sp.gov.br/web/sesana/w/pontos-de-distribuicao-cozinha-cidada",
    ),
    (
        "sesana",
        "bom-prato-paulistano",
        "https://prefeitura.sp.gov.br/web/sesana/w/bom-prato",
    ),
    (
        "saude",
        "caps-territorios",
        "https://prefeitura.sp.gov.br/web/saude/w/servi%C3%A7os-dos-centros-de-aten%C3%A7%C3%A3o-psicossocial-caps-por-territ%C3%B3rio",
    ),
    (
        "smads",
        "acolhida-leste",
        "https://www2.prefeitura.sp.gov.br/web/assistencia_social/w/cta/331268",
    ),
    (
        "smads",
        "acolhida-norte",
        "https://www2.prefeitura.sp.gov.br/web/assistencia_social/w/cta/331281",
    ),
    (
        "smads",
        "acolhida-sul",
        "https://www2.prefeitura.sp.gov.br/web/assistencia_social/w/cta/331285",
    ),
    (
        "smads",
        "acolhida-oeste",
        "https://www2.prefeitura.sp.gov.br/web/assistencia_social/w/cta/331273",
    ),
    (
        "smads",
        "acolhida-centro",
        "https://www2.prefeitura.sp.gov.br/web/assistencia_social/w/cta/331279",
    ),
]


def read_limited(response, allowance, deadline):
    """Conta os bytes lidos mesmo quando o servidor não informa Content-Length."""
    result = bytearray()
    while len(result) < allowance:
        if time.monotonic() > deadline:
            return bytes(result), "timeout"
        try:
            chunk = response.read(min(8192, allowance - len(result)))
        except OSError:
            return bytes(result), "download_error"
        if not chunk:
            return bytes(result), "saved"
        result.extend(chunk)
    # Sem ler além do teto: tamanho exatamente no limite fica conservadoramente bloqueado.
    return bytes(result), "limit_reached"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--extend",
        action="store_true",
        help="Acrescentar novas fontes sem baixar novamente ou alterar as existentes.",
    )
    args = parser.parse_args()
    manifest_path = ROOT / "data/sources.json"
    if manifest_path.exists() and not args.extend:
        raise SystemExit(
            "Coleta já registrada. Não sobrescrever evidências automaticamente."
        )
    records = []
    used = 0
    if manifest_path.exists():
        previous = json.loads(manifest_path.read_text(encoding="utf-8"))
        records = previous["sources"]
        used = previous["received_bytes"]
        for source in records:
            if source["status"] == "saved":
                body = (ROOT / source["path"]).read_bytes()
                if hashlib.sha256(body).hexdigest() != source["sha256"]:
                    raise SystemExit(f"Evidência alterada: {source['id']}")
    existing_ids = {source["id"] for source in records}
    for agency, source_id, url in SOURCES:
        if source_id in existing_ids:
            continue
        record = {
            "id": source_id,
            "agency": agency,
            "url": url,
            "attempted_at_utc": datetime.now(UTC).isoformat(),
            "status": "not_collected",
            "path": None,
        }
        allowance = min(FILE_LIMIT, TOTAL_LIMIT - used)
        if allowance <= 0:
            record["status"] = "total_limit_reached"
            records.append(record)
            continue
        started = time.monotonic()
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "CareCompass-Academic-Source-Collection/0.1",
                "Accept-Encoding": "identity",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                record["final_url"] = response.url
                record["content_type"] = response.headers.get("Content-Type", "")
                declared = response.headers.get("Content-Length")
                record["declared_bytes"] = (
                    int(declared) if declared and declared.isdigit() else None
                )
                encoding = response.headers.get("Content-Encoding", "identity").lower()
                if encoding not in ("", "identity"):
                    record["status"] = "encoded_response_rejected"
                elif "text/html" not in record["content_type"]:
                    record["status"] = "unexpected_content_type"
                elif record["declared_bytes"] and record["declared_bytes"] >= allowance:
                    record["status"] = "declared_limit_reached"
                else:
                    payload, status = read_limited(response, allowance, started + 20)
                    used += len(payload)
                    record["received_bytes"] = len(payload)
                    record["status"] = status
                    if status == "saved":
                        destination = ROOT / "data/raw" / agency / f"{source_id}.html"
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        destination.write_bytes(payload)
                        record["path"] = destination.relative_to(ROOT).as_posix()
                        record["sha256"] = hashlib.sha256(payload).hexdigest()
        except (OSError, urllib.error.URLError) as exc:
            record["status"] = "download_error"
            record["error_type"] = type(exc).__name__
        records.append(record)
        print(f"{source_id}: {record['status']}")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(
            {
                "file_limit_bytes": FILE_LIMIT,
                "total_limit_bytes": TOTAL_LIMIT,
                "received_bytes": used,
                "sources": records,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
