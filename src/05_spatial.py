"""T3 — I de Moran global e LISA dos resíduos municipais, com FDR (docs/desenho_T2_T3.md, itens 4–7).

Uso: python src/05_spatial.py
Saídas: output/tables/t3_moran.csv, t3_lisa_{ano}.csv, t3_clusters_2026.csv, t3_resumo.md
"""

import geopandas as gpd
import numpy as np
import pandas as pd
from esda.moran import Moran, Moran_Local
from libpysal.weights import KNN, Queen
from libpysal.weights.util import attach_islands
from statsmodels.stats.multitest import multipletests

from common import OUTPUT, PROCESSED, RAW, SEMENTE

ANOS = [2014, 2018, 2022, 2026]
CONTROLES = [2014, 2018, 2022]
Q_FDR = 0.05
LIMIAR_DIRECAO = 0.80
TIPO = {1: "alto-alto", 2: "baixo-alto", 3: "baixo-baixo", 4: "alto-baixo"}


def pesos(g: gpd.GeoDataFrame):
    w = Queen.from_dataframe(g, use_index=False, silence_warnings=True)
    if w.islands:
        cent = g.to_crs("EPSG:5880").geometry.centroid
        w_knn = KNN.from_array(np.column_stack([cent.x, cent.y]), k=1)
        w = attach_islands(w, w_knn)
    w.transform = "r"
    return w


def analisa(ano: int, malha: gpd.GeoDataFrame) -> tuple[dict, pd.DataFrame]:
    res = pd.read_parquet(PROCESSED / f"t3_residuos_{ano}.parquet")
    g = malha.merge(res, left_on="CD_MUN", right_on="cd_ibge", how="inner").reset_index(drop=True)
    w = pesos(g)
    np.random.seed(SEMENTE)
    mi = Moran(g["residuo"].to_numpy(), w, permutations=999)
    lisa = Moran_Local(g["residuo"].to_numpy(), w, permutations=999, seed=SEMENTE)
    rejeita, p_bh, _, _ = multipletests(lisa.p_sim, alpha=Q_FDR, method="fdr_bh")
    out = pd.DataFrame({"cd_ibge": g["CD_MUN"], "nm_mun": g["NM_MUN"], "uf": g["SIGLA_UF"],
                        "residuo": g["residuo"], "Ii": lisa.Is, "quadrante": lisa.q, "p_sim": lisa.p_sim,
                        "p_bh": p_bh})
    out["cluster"] = rejeita & out["quadrante"].isin([1, 3])
    out["tipo"] = out["quadrante"].map(TIPO).where(out["cluster"], "")
    out["ano"] = ano
    out.to_csv(OUTPUT / "tables" / f"t3_lisa_{ano}.csv", index=False)
    info = {"ano": ano, "municipios": len(g), "ilhas_ligadas_por_knn": len(Queen.from_dataframe(
        g, use_index=False, silence_warnings=True).islands), "I": mi.I, "p_sim": mi.p_sim, "z_sim": mi.z_sim,
        "clusters_fdr": int(out["cluster"].sum()),
        "alto_alto": int((out["tipo"] == "alto-alto").sum()), "baixo_baixo": int((out["tipo"] == "baixo-baixo").sum())}
    return info, out


def main() -> None:
    malha = gpd.read_file(f"zip://{(RAW / 'D7' / 'BR_Municipios_2022.zip').as_posix()}!BR_Municipios_2022.shp")
    infos, lisas = [], {}
    for ano in ANOS:
        info, out = analisa(ano, malha)
        infos.append(info)
        lisas[ano] = out.set_index("cd_ibge")
        print(info, flush=True)
    moran = pd.DataFrame(infos)
    moran.to_csv(OUTPUT / "tables" / "t3_moran.csv", index=False)

    i26 = float(moran.loc[moran["ano"] == 2026, "I"].iloc[0])
    ic = moran[moran["ano"].isin(CONTROLES)]["I"]
    dentro_faixa = bool(ic.min() <= i26 <= ic.max())

    c26 = lisas[2026][lisas[2026]["cluster"]].copy()
    for ano in CONTROLES:
        prev = lisas[ano].reindex(c26.index)
        c26[f"cluster_{ano}"] = prev["cluster"].fillna(False).astype(bool)
        c26[f"tipo_{ano}"] = prev["tipo"].fillna("")
    c26["recorrente"] = c26[[f"cluster_{a}" for a in CONTROLES]].any(axis=1)
    c26["mesmo_tipo_em_algum_ano"] = np.column_stack(
        [c26[f"tipo_{a}"] == c26["tipo"] for a in CONTROLES]).any(axis=1)
    c26["exclusivo_2026"] = ~c26["recorrente"]
    c26.reset_index().to_csv(OUTPUT / "tables" / "t3_clusters_2026.csv", index=False)

    exc = c26[c26["exclusivo_2026"]]
    prop_tipo = exc["tipo"].value_counts(normalize=True)
    direcional = bool(len(exc) and prop_tipo.max() >= LIMIAR_DIRECAO)
    if dentro_faixa and not len(exc):
        classe = "Nada anômalo: I de 2026 dentro da faixa de 2014–2022 e nenhum cluster exclusivo de 2026."
    elif len(exc) and direcional:
        classe = ("Achado (a investigar): clusters significativos exclusivos de 2026 e direcionais. Hipótese "
                  "padrão: erro de especificação do modelo. Municípios listados em t3_clusters_2026.csv.")
    elif len(exc):
        classe = ("Clusters exclusivos de 2026 sem direção predominante (< 80% de um tipo): não atendem ao "
                  "critério de achado; I de 2026 " + ("dentro" if dentro_faixa else "fora") + " da faixa histórica.")
    else:
        classe = ("Clusters de 2026 todos recorrentes (fenômeno regional estrutural); I de 2026 fora da faixa "
                  "de 2014–2022.")
    resumo = {
        "I de Moran 2026": i26, "I de Moran 2014–2022 (mín.)": float(ic.min()),
        "I de Moran 2014–2022 (máx.)": float(ic.max()), "I de 2026 dentro da faixa": dentro_faixa,
        "municípios em cluster em 2026 (FDR q=0,05)": len(c26),
        "dos quais recorrentes (cluster em algum ano anterior)": int(c26["recorrente"].sum()),
        "dos quais exclusivos de 2026": len(exc),
        "exclusivos de 2026 por tipo": exc["tipo"].value_counts().to_dict(),
        "exclusivos de 2026 por UF": exc["uf"].value_counts().to_dict(),
        "classificação T3": classe,
    }
    linhas = ["# T3 — resumo", "", "| Métrica | Valor |", "|---|---|"]
    for k, v in resumo.items():
        linhas.append(f"| {k} | {v:.4g} |" if isinstance(v, float) else f"| {k} | {v} |")
        print(f"{k}: {v}")
    modelos = pd.read_csv(OUTPUT / "tables" / "t3_modelos.csv")
    linhas += ["", "## Modelos por ano", "", modelos.round(4).to_markdown(index=False), "",
               "## Moran global e LISA por ano", "", moran.round(4).to_markdown(index=False), "",
               "Resíduos do modelo misto municipal (`src/04_model_residuals.py`); pesos de contiguidade queen na "
               "malha municipal de 2022 (D7); 999 permutações, semente 20261025; LISA com Benjamini-Hochberg "
               "q = 0,05. Fontes: TSE (D2, D8), IBGE (D6, D7); hashes em `data/raw/MANIFEST.csv`. Regras em "
               "`docs/desenho_T2_T3.md`. Variável: participação do candidato 13 no 2º turno (referência de "
               "sinal); resíduo positivo = acima do previsto para o 13."]
    (OUTPUT / "tables" / "t3_resumo.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
