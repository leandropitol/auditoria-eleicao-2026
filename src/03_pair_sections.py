"""T2 — pareamento de seções entre turnos (2026) e seções com deslocamento atípico (docs/desenho_T2_T3.md).

Uso: python src/03_pair_sections.py
Saídas: output/tables/t2_secoes_anomalas.csv, t2_componentes.csv, t2_coeficientes.csv, t2_resumo.md

Dado agregado: nenhuma taxa de transferência individual é estimada (falácia ecológica).
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree
from statsmodels.stats.multitest import multipletests

from common import OUTPUT, PROCESSED, SEMENTE

CHAVE = ["uf", "mun", "zona", "secao"]
K_VIZINHOS = 5
PERMUTACOES = 999
Q_FDR = 0.05
ALFA = 0.05
PERFIL = ["p_fem", "p_id_16_24", "p_id_25_44", "p_id_45_59", "p_id_60_69", "p_esc_superior", "p_esc_medio"]
TURNOS = ["abst_1t", "bn_1t", "d_comparecimento", "d_bn"]


def residuos(df: pd.DataFrame, xcols: list[str]) -> tuple[np.ndarray, pd.Series]:
    """OLS com efeito fixo de município pela transformação dentro do grupo."""
    g = df.groupby(["uf", "mun"])
    y = (df["y"] - g["y"].transform("mean")).to_numpy()
    X = np.column_stack([(df[c] - g[c].transform("mean")).to_numpy() for c in xcols])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    e = y - X @ beta
    gl = len(df) - len(xcols) - g.ngroups
    sigma = np.sqrt((e ** 2).sum() / gl)
    return e / sigma, pd.Series(beta, index=xcols)


def main() -> None:
    base = pd.read_parquet(PROCESSED / "t23_secoes_2026.parquet")
    locais = pd.read_parquet(PROCESSED / "t23_locais_2026.parquet")
    t1 = sorted(c for c in base.columns if c.startswith("t1_c"))
    xcols = t1 + TURNOS + PERFIL
    contagem = {"seções na base (exceto exterior)": len(base),
                "sem 2º turno": int(base["y"].isna().sum()),
                "sem 1º turno": int(base[t1[0]].isna().sum()),
                "sem perfil do eleitorado (D3)": int(base["p_fem"].isna().sum())}
    df = base.dropna(subset=["y", *xcols]).reset_index(drop=True)
    contagem["seções pareadas e completas (modelo)"] = len(df)

    z, beta = residuos(df, xcols)
    df["z"] = z
    df["p"] = 2 * stats.norm.sf(np.abs(z))
    df["anomala"], df["p_bh"], _, _ = multipletests(df["p"], alpha=Q_FDR, method="fdr_bh")
    an = df[df["anomala"]]

    # (b) direção
    pos = int((an["z"] > 0).sum())
    p_direcao = float(stats.binomtest(pos, len(an), 0.5).pvalue) if len(an) else np.nan

    # (a) agrupamento espacial: k vizinhos mais próximos pelas coordenadas do local de votação
    df = df.merge(locais[[*CHAVE, "local", "lat", "lon"]], on=CHAVE, how="left")
    geo = df.dropna(subset=["lat", "lon"]).reset_index(drop=True)
    lat, lon = np.radians(geo["lat"].to_numpy()), np.radians(geo["lon"].to_numpy())
    xyz = np.column_stack([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)])
    _, viz = cKDTree(xyz).query(xyz, k=K_VIZINHOS + 1)
    viz = viz[:, 1:]
    rot = geo["anomala"].to_numpy()
    obs = int((rot[:, None] & rot[viz]).sum())
    rng = np.random.default_rng(SEMENTE)
    perm = np.empty(PERMUTACOES)
    for i in range(PERMUTACOES):
        r = rng.permutation(rot)
        perm[i] = (r[:, None] & r[viz]).sum()
    p_espacial = float((1 + (perm >= obs).sum()) / (PERMUTACOES + 1))
    esperado = float(perm.mean())

    # componentes conexos de seções anômalas no grafo de vizinhos
    linhas_i = np.repeat(np.arange(len(geo)), K_VIZINHOS)
    colunas = viz.ravel()
    mask = rot[linhas_i] & rot[colunas]
    m = coo_matrix((np.ones(mask.sum()), (linhas_i[mask], colunas[mask])), shape=(len(geo), len(geo)))
    _, comp = connected_components(m, directed=False)
    geo["componente"] = np.where(rot, comp, -1)
    tam = geo[geo["componente"] >= 0].groupby("componente").size()
    grandes = tam[tam >= 3].index
    comps = (geo[geo["componente"].isin(grandes)]
             .groupby("componente")
             .agg(n_secoes=("secao", "size"), uf=("uf", "first"), mun=("mun", "first"),
                  municipios=("mun", "nunique"), locais=("local", "nunique"), z_medio=("z", "mean"),
                  z_positivos=("z", lambda s: int((s > 0).sum())))
             .sort_values("n_secoes", ascending=False))
    comps.to_csv(OUTPUT / "tables" / "t2_componentes.csv")

    agrupado = p_espacial < ALFA
    direcional = (not np.isnan(p_direcao)) and p_direcao < ALFA
    if len(an) == 0:
        classe = "Nenhuma seção anômala após FDR: heterogeneidade regional."
    elif agrupado and direcional:
        classe = ("Critérios (a), (b) e (c) atendidos: seções anômalas agrupadas e direcionais, condicionais ao "
                  "perfil e ao município. Achado a localizar (componentes listados); hipótese padrão: erro de "
                  "especificação do modelo.")
    else:
        falta = [n for n, ok in (("(a) agrupamento", agrupado), ("(b) direção", direcional)) if not ok]
        classe = f"Heterogeneidade regional: falta {' e '.join(falta)}."

    an_out = df[df["anomala"]].sort_values("p")
    an_out[[*CHAVE, "local", "lat", "lon", "y", "z", "p", "p_bh", "votos_2t"]].to_csv(
        OUTPUT / "tables" / "t2_secoes_anomalas.csv", index=False)
    beta.rename("coef_dentro_municipio").to_csv(OUTPUT / "tables" / "t2_coeficientes.csv")

    resumo = {**contagem,
              "seções anômalas (FDR q=0,05)": len(an),
              "proporção anômala": len(an) / len(df),
              "anômalas com resíduo positivo (acima do previsto para o 13)": pos,
              "anômalas com resíduo negativo": len(an) - pos,
              "(b) p binomial de direção": p_direcao,
              "seções com coordenadas válidas (critério a)": len(geo),
              "(a) pares vizinhos anômalo-anômalo: observado": obs,
              "(a) pares vizinhos anômalo-anômalo: esperado sob permutação": esperado,
              "(a) p de permutação (unilateral)": p_espacial,
              "componentes com ≥ 3 seções anômalas": len(comps),
              "classificação T2": classe}
    linhas = ["# T2 — resumo", "", "| Métrica | Valor |", "|---|---|"]
    for k, v in resumo.items():
        linhas.append(f"| {k} | {v:.4g} |" if isinstance(v, float) else f"| {k} | {v} |")
        print(f"{k}: {v}")
    linhas += ["", "## Maiores componentes de seções anômalas", "", comps.head(20).round(2).to_markdown(), "",
               "Modelo: participação do candidato 13 no 2º turno (votos nominais dos dois finalistas) sobre o 1º turno "
               "da seção, abstenção e brancos/nulos, variações entre turnos e perfil do eleitorado (D3), com efeito "
               "fixo de município. Resíduo padronizado; Benjamini-Hochberg q = 0,05. Dado agregado: os coeficientes "
               "não descrevem comportamento individual. Fontes: TSE (D2, D3, D4); hashes em "
               "`data/raw/MANIFEST.csv`. Regras em `docs/desenho_T2_T3.md`."]
    (OUTPUT / "tables" / "t2_resumo.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
