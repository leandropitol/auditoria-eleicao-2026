"""Funções compartilhadas: caminhos, hash, download com backoff e manifesto de integridade."""

import csv
import hashlib
import io
import threading
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW = REPO_ROOT / "data" / "raw"
PROCESSED = REPO_ROOT / "data" / "processed"
OUTPUT = REPO_ROOT / "output"
MANIFEST = RAW / "MANIFEST.csv"
MANIFEST_FIELDS = [
    "id_fonte", "arquivo", "url", "data_hora_utc", "bytes", "sha256",
    "orgao", "descricao", "licenca", "observacoes",
]
USER_AGENT = "auditoria-eleicao-2026 (pesquisa com dados abertos; python-requests)"
SEMENTE = 20261025

_manifest_lock = threading.Lock()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def agora_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def registra_manifesto(row: dict) -> None:
    """Acrescenta uma linha ao manifesto (append-only: nenhuma linha é reescrita)."""
    with _manifest_lock:
        novo = not MANIFEST.exists()
        with open(MANIFEST, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=MANIFEST_FIELDS)
            if novo:
                writer.writeheader()
            writer.writerow({k: row.get(k, "") for k in MANIFEST_FIELDS})


def arquivos_no_manifesto() -> set[str]:
    if not MANIFEST.exists():
        return set()
    with open(MANIFEST, newline="", encoding="utf-8") as f:
        return {r["arquivo"] for r in csv.DictReader(f)}


def baixa(url: str, destino: Path, sessao: requests.Session | None = None,
          tentativas: int = 6, timeout: int = 120) -> None:
    """Baixa `url` para `destino` (via arquivo .part), com backoff exponencial.

    Nunca sobrescreve: se `destino` já existe, falha, porque data/raw é imutável.
    """
    if destino.exists():
        raise FileExistsError(f"{destino} já existe; data/raw é imutável")
    destino.parent.mkdir(parents=True, exist_ok=True)
    parcial = destino.with_name(destino.name + ".part")
    s = sessao or requests.Session()
    for tentativa in range(tentativas):
        try:
            with s.get(url, stream=True, timeout=timeout,
                       headers={"User-Agent": USER_AGENT}) as r:
                r.raise_for_status()
                with open(parcial, "wb") as f:
                    for chunk in r.iter_content(1 << 20):
                        f.write(chunk)
            parcial.rename(destino)
            return
        except (requests.RequestException, OSError):
            if parcial.exists():
                parcial.unlink()
            if tentativa == tentativas - 1:
                raise
            time.sleep(2 ** tentativa)


def baixa_e_registra(id_fonte: str, url: str, destino: Path, orgao: str, descricao: str,
                     licenca: str, observacoes: str = "",
                     sessao: requests.Session | None = None) -> dict:
    data_hora = agora_utc()
    baixa(url, destino, sessao)
    row = {
        "id_fonte": id_fonte,
        "arquivo": destino.relative_to(RAW).as_posix(),
        "url": url,
        "data_hora_utc": data_hora,
        "bytes": destino.stat().st_size,
        "sha256": sha256_file(destino),
        "orgao": orgao,
        "descricao": descricao,
        "licenca": licenca,
        "observacoes": observacoes,
    }
    registra_manifesto(row)
    return row


def textos_log_urna(origem: Path | bytes) -> list[str]:
    """Textos de um log de urna (.jez): o `logd.dat` e, recursivamente, os logs embutidos (.jez) que o arquivo traz,
    como o da urna substituída numa troca de urna. A ordem dos membros no arquivo varia."""
    with zipfile.ZipFile(io.BytesIO(origem) if isinstance(origem, bytes) else origem) as z:
        textos = []
        for nome in z.namelist():
            if nome.endswith(".jez"):
                textos += textos_log_urna(z.read(nome))
            elif nome.endswith(".dat"):
                textos.append(z.read(nome).decode("latin-1"))
        return textos
