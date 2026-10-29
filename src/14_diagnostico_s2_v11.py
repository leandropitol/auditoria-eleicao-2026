"""EXPLORATÓRIO — diagnóstico da especificação S2 (docs/plano_v1_1_adendo.md, carimbado antes da execução).

Uso: python src/14_diagnostico_s2_v11.py
Saídas: output/tables/v11_s2_diagnostico.csv, v11_s2b.csv; acrescenta seção a v11_EXPLORATORIO.md
"""

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

from common import OUTPUT, PROCESSED

T = OUTPUT / "tables"
FAIXAS = [0, 10, 25, 50, 75, 90, 100]
ROTULOS = ["0–10%", "10–25%", "25–50%", "50–75%", "75–90%", "90–100%"]


def _modulo(nome, arquivo):
    spec = importlib.util.spec_from_file_location(nome, Path(__file__).with_name(arquivo))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main() -> None:
    T2 = _modulo("t2", "03_pair_sections.py")
    S = _modulo("s", "13_sensibilidades_v11.py")
    base = pd.read_parquet(PROCESSED / "t23_secoes_2026.parquet")
    chave = {"uf": str, "mun": str, "zona": str, "secao": str}

    def faixas_de(arquivo: str) -> pd.Series:
        """Anômalas por faixa da participação ORIGINAL do 13 (nas saídas em logit, a coluna y está em logit)."""
        an = pd.read_csv(T / arquivo, dtype=chave)
        for c, w in (("mun", 5), ("zona", 4), ("secao", 4)):
            an[c] = an[c].str.zfill(w)
        y_pct = an[T2.CHAVE].merge(base[[*T2.CHAVE, "y"]], on=T2.CHAVE, how="left")["y"]
        assert y_pct.notna().all()
        return pd.cut(y_pct, FAIXAS, labels=ROTULOS, include_lowest=True).value_counts(sort=False)

    todas = pd.cut(base["y"], FAIXAS, labels=ROTULOS, include_lowest=True).value_counts(sort=False)
    d1 = pd.DataFrame({"secoes_total": todas,
                       "anomalas_S2": faixas_de("t2_secoes_anomalas_v11_S2_logit_ponderado.csv")})
    d1["pct_das_secoes"] = 100 * d1["secoes_total"] / d1["secoes_total"].sum()
    d1["pct_das_anomalas_S2"] = 100 * d1["anomalas_S2"] / d1["anomalas_S2"].sum()
    extremas = float(d1.loc[["0–10%", "90–100%"], "anomalas_S2"].sum() / d1["anomalas_S2"].sum())

    # S2b: logit com peso de variância inversa n·p̂·(1−p̂)
    locais = pd.read_parquet(PROCESSED / "t23_locais_2026.parquet")
    nomes = T2.nomes_locais()
    t1 = sorted(c for c in base.columns if c.startswith("t1_c"))
    xfull = t1 + T2.TURNOS + T2.PERFIL
    df = base.dropna(subset=["y", *xfull]).reset_index(drop=True)
    df = df.merge(locais[[*T2.CHAVE, "local", "lat", "lon"]], on=T2.CHAVE, how="left")
    v13 = df["y"] / 100 * df["votos_2t"]
    p = np.clip(df["y"] / 100, 0.02, 0.98)
    df["peso_s2b"] = df["votos_2t"] * p * (1 - p)
    df["y"] = np.log((v13 + 0.5) / (df["votos_2t"] - v13 + 0.5))
    idx = np.flatnonzero(df["lat"].notna() & df["lon"].notna())
    lat, lon = np.radians(df["lat"].to_numpy()[idx]), np.radians(df["lon"].to_numpy()[idx])
    viz = T2.vizinhos(np.column_stack([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)]),
                      T2.K_VIZINHOS)
    res, _ = T2.analisa(df, xfull, viz, idx, nomes, df["peso_s2b"].to_numpy(), "_v11_S2b_logit_peso_correto")
    an_b = pd.read_csv(T / "t2_secoes_anomalas_v11_S2b_logit_peso_correto.csv")
    margem = S.margem_oficial()
    s2b = pd.DataFrame([{
        "especificacao": "S2b_logit_peso_variancia_inversa", "secoes_no_modelo": len(df), "anomalas": len(an_b),
        "positivas_13": int((an_b["z"] > 0).sum()), "negativas_13": int((an_b["z"] < 0).sum()),
        "p_direcao": res["(b) p binomial de direção"], "p_agrupamento": res["(a) p de permutação (unilateral)"],
        "votos_nas_anomalas": int(an_b["votos_2t"].sum()),
        "pior_caso_pct_margem": S.pior_caso(an_b["votos_2t"].sum(), margem),
        "classificacao_pelos_criterios": res["classificação T2"]}])
    s2b.to_csv(T / "v11_s2b.csv", index=False)
    d1["anomalas_S2b"] = faixas_de("t2_secoes_anomalas_v11_S2b_logit_peso_correto.csv")
    d1["pct_das_anomalas_S2b"] = 100 * d1["anomalas_S2b"] / d1["anomalas_S2b"].sum()
    d1.to_csv(T / "v11_s2_diagnostico.csv")
    print(d1.round(2).to_string())
    print(f"proporção das anômalas de S2 em faixas extremas (<10% ou >90%): {extremas:.3f}")
    print(s2b.T.to_string())

    md = ["", "## Adendo — diagnóstico de S2 (plano carimbado em `docs/plano_v1_1_adendo.md`)", "",
          "### D1: anômalas de S2 por faixa de participação do 13", "", d1.round(2).to_markdown(), "",
          f"Proporção das anômalas de S2 em faixas extremas (abaixo de 10% ou acima de 90%): "
          f"{100 * extremas:.1f}%.", "",
          "### S2b: logit com peso de variância inversa n·p̂·(1−p̂)", "", s2b.round(4).to_markdown(index=False)]
    with open(T / "v11_EXPLORATORIO.md", "a", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")


if __name__ == "__main__":
    main()
