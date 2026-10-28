"""T4 — testes de dígitos (APENAS COMPLETUDE; nunca evidência). Regras em docs/desenho_T4_consolidacao.md.

Uso: python src/06_digits.py
Saídas: output/tables/t4_digitos.csv, t4_resumo.md
"""

import zipfile

import numpy as np
import pandas as pd
from scipy import stats

from common import OUTPUT, PROCESSED, RAW

ANOS = [2014, 2018, 2022, 2026]
BENFORD_2 = np.array([sum(np.log10(1 + 1 / (10 * d1 + d2)) for d1 in range(1, 10)) for d2 in range(10)])


def contagens(ano: int) -> pd.DataFrame:
    """Votos de cada finalista do 2º turno por seção (inclui exterior)."""
    finalistas = set(pd.read_parquet(PROCESSED / f"votos_presidente_{ano}.parquet")
                     .query("turno == 2")["candidato"])
    arq = RAW / ("D2" if ano == 2026 else "D8") / f"votacao_secao_{ano}_BR.zip"
    partes = []
    with zipfile.ZipFile(arq) as z:
        nome = next(n for n in z.namelist() if n.lower().endswith(".csv"))
        for b in pd.read_csv(z.open(nome), sep=";", encoding="latin-1", dtype=str, chunksize=2_000_000,
                             usecols=["NR_TURNO", "CD_CARGO", "NR_VOTAVEL", "QT_VOTOS"]):
            b = b[(b["NR_TURNO"] == "2") & (b["CD_CARGO"] == "1") & b["NR_VOTAVEL"].isin(finalistas)]
            partes.append(b[["NR_VOTAVEL", "QT_VOTOS"]])
    df = pd.concat(partes)
    df["QT_VOTOS"] = df["QT_VOTOS"].astype(int)
    return df


def testes(v: np.ndarray) -> dict:
    v = v[v >= 10]
    n = len(v)
    seg = np.array([int(str(x)[1]) for x in v])
    ult = v % 10
    obs2 = np.bincount(seg, minlength=10) / n
    obsu = np.bincount(ult, minlength=10) / n
    chi2_2 = stats.chisquare(np.bincount(seg, minlength=10), BENFORD_2 * n)
    chi2_u = stats.chisquare(np.bincount(ult, minlength=10))
    m5 = int((ult % 5 == 0).sum())
    m10 = int((ult == 0).sum())
    return {
        "n_contagens_ge_10": n,
        "benford2_media_2o_digito": float(seg.mean()),
        "benford2_MAD": float(np.abs(obs2 - BENFORD_2).mean()),
        "benford2_chi2": float(chi2_2.statistic), "benford2_p": float(chi2_2.pvalue),
        "ultimo_MAD": float(np.abs(obsu - 0.1).mean()),
        "ultimo_chi2": float(chi2_u.statistic), "ultimo_p": float(chi2_u.pvalue),
        "prop_mult5": m5 / n, "mult5_p": float(stats.binomtest(m5, n, 0.2).pvalue),
        "prop_mult10": m10 / n, "mult10_p": float(stats.binomtest(m10, n, 0.1).pvalue),
    }


def main() -> None:
    linhas = []
    for ano in ANOS:
        df = contagens(ano)
        for cand, g in df.groupby("NR_VOTAVEL"):
            r = {"ano": ano, "candidato": cand, **testes(g["QT_VOTOS"].to_numpy())}
            linhas.append(r)
            print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()}, flush=True)
    t = pd.DataFrame(linhas)
    OUTPUT.joinpath("tables").mkdir(parents=True, exist_ok=True)
    t.to_csv(OUTPUT / "tables" / "t4_digitos.csv", index=False)

    ctrl = t[t["ano"] < 2026]
    t26 = t[t["ano"] == 2026]
    faixa = {c: (ctrl[c].min(), ctrl[c].max()) for c in ("benford2_MAD", "ultimo_MAD", "prop_mult5", "prop_mult10")}
    comp = [{"métrica": c, "2014–2022 (mín.)": lo, "2014–2022 (máx.)": hi,
             "2026 (candidatos)": ", ".join(f"{r.candidato}: {getattr(r, c):.4f}" for r in t26.itertuples()),
             "2026 dentro da faixa": all(lo <= getattr(r, c) <= hi for r in t26.itertuples())}
            for c, (lo, hi) in faixa.items()]
    comp = pd.DataFrame(comp)
    linhas_md = ["# T4 — dígitos (completude; não é evidência)", "",
                 "**Advertência do pré-registro:** contagens por urna têm faixa estreita e teto rígido; Benford não vale "
                 "nessas condições e produz falsos positivos com regularidade. Desvio em T4, sozinho, não constitui "
                 "achado e não deve ser reportado como evidência sob nenhuma circunstância.", "",
                 "## 2026 contra os anos de controle (tamanho do desvio)", "", comp.round(4).to_markdown(index=False), "",
                 "## Todos os testes", "", t.round(4).to_markdown(index=False), "",
                 "Contagens ≥ 10 votos por seção e finalista. MAD = desvio absoluto médio entre as proporções observada e "
                 "esperada. Com centenas de milhares de seções, p-valores baixos são esperados mesmo para desvios "
                 "mínimos. Fontes: TSE (D2, D8); hashes em `data/raw/MANIFEST.csv`. Regras em "
                 "`docs/desenho_T4_consolidacao.md`."]
    (OUTPUT / "tables" / "t4_resumo.md").write_text("\n".join(linhas_md) + "\n", encoding="utf-8")
    print(comp.round(4).to_string())


if __name__ == "__main__":
    main()
