"""Confere data/raw contra o manifesto e resume a coleta por fonte (D1–D8).

Uso: python src/00_manifesto.py
Falha (código 1) se algum arquivo do manifesto estiver ausente ou com SHA-256 diferente,
ou se houver arquivo em data/raw fora do manifesto.
"""

import sys

import pandas as pd

from common import MANIFEST, OUTPUT, RAW, sha256_file

IGNORAR = {"MANIFEST.csv", "log_lote.txt", "log_bu_amostra.txt", ".keep"}


def main() -> None:
    m = pd.read_csv(MANIFEST, dtype={"sha256": str})
    problemas = []
    for r in m.itertuples():
        p = RAW / r.arquivo
        if not p.exists():
            problemas.append(f"ausente: {r.arquivo}")
        elif sha256_file(p) != r.sha256:
            problemas.append(f"sha256 diferente: {r.arquivo}")
    registrados = set(m["arquivo"])
    for p in RAW.rglob("*"):
        if p.is_file() and p.name not in IGNORAR and p.relative_to(RAW).as_posix() not in registrados:
            problemas.append(f"fora do manifesto: {p.relative_to(RAW).as_posix()}")

    resumo = (m.assign(fonte=m["id_fonte"].str.split("_").str[0])
               .groupby("fonte")
               .agg(arquivos=("arquivo", "size"), bytes=("bytes", "sum"),
                    primeiro_acesso_utc=("data_hora_utc", "min"), ultimo_acesso_utc=("data_hora_utc", "max")))
    resumo["GB"] = (resumo["bytes"] / 1e9).round(3)
    OUTPUT.joinpath("tables").mkdir(parents=True, exist_ok=True)
    resumo.to_csv(OUTPUT / "tables" / "coleta_resumo_por_fonte.csv")
    print(resumo.to_string())
    print(f"arquivos no manifesto: {len(m)}; problemas: {len(problemas)}")
    for linha in problemas[:50]:
        print("  " + linha)
    if problemas:
        sys.exit(1)


if __name__ == "__main__":
    main()
