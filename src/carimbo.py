"""Carimbo temporal externo (OpenTimestamps) de arquivos: grava <arquivo>.ots ao lado de cada um.

Só o hash SHA-256 (com um nonce aleatório) é enviado aos calendários públicos; o conteúdo não sai da máquina.
O comprovante fica "pendente" até o calendário ancorá-lo num bloco do Bitcoin (algumas horas); depois, qualquer
pessoa verifica com o cliente oficial (`ots upgrade` e `ots verify <arquivo>.ots`) ou em https://opentimestamps.org.

Uso: python src/carimbo.py <arquivo> [<arquivo> ...]
"""

import os
import sys

from opentimestamps.calendar import RemoteCalendar
from opentimestamps.core.op import OpAppend, OpSHA256
from opentimestamps.core.serialize import StreamSerializationContext
from opentimestamps.core.timestamp import DetachedTimestampFile

CALENDARIOS = [
    "https://a.pool.opentimestamps.org",
    "https://b.pool.opentimestamps.org",
    "https://a.pool.eternitywall.com",
    "https://ots.btc.catallaxy.com",
]
MINIMO = 2


def carimba(caminho: str) -> int:
    with open(caminho, "rb") as fd:
        dtf = DetachedTimestampFile.from_fd(OpSHA256(), fd)
    nonce = dtf.timestamp.ops.add(OpAppend(os.urandom(16)))
    raiz = nonce.ops.add(OpSHA256())
    aceitos = 0
    for url in CALENDARIOS:
        try:
            raiz.merge(RemoteCalendar(url).submit(raiz.msg, timeout=30))
            aceitos += 1
        except Exception as e:  # noqa: BLE001 - calendário fora do ar não impede os demais
            print(f"  calendário indisponível: {url} ({type(e).__name__})")
    if aceitos < MINIMO:
        raise RuntimeError(f"{caminho}: só {aceitos} calendário(s) aceitaram; mínimo {MINIMO}")
    with open(caminho + ".ots", "wb") as f:
        dtf.serialize(StreamSerializationContext(f))
    print(f"{caminho}: sha256 {dtf.file_digest.hex()} carimbado em {aceitos} calendários")
    return aceitos


if __name__ == "__main__":
    for arq in sys.argv[1:]:
        carimba(arq)
