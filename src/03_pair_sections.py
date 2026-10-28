"""T2 — pareamento de seções entre turnos (2026) e seções com deslocamento atípico (docs/desenho_T2_T3.md).

Uso: python src/03_pair_sections.py
Saídas: output/tables/t2_secoes_anomalas.csv, t2_componentes.csv, t2_coeficientes.csv, t2_resumo.md

Dado agregado: nenhuma taxa de transferência individual é estimada (falácia ecológica).
"""

import zipfile

import numpy as np
import pandas as pd
from scipy import stats
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree
from statsmodels.stats.multitest import multipletests

from common import OUTPUT, PROCESSED, RAW, SEMENTE

CHAVE = ["uf", "mun", "zona", "secao"]
K_VIZINHOS = 5
PERMUTACOES = 999
Q_FDR = 0.05
ALFA = 0.05
PERFIL = ["p_fem", "p_id_16_24", "p_id_25_44", "p_id_45_59", "p_id_60_69", "p_esc_superior", "p_esc_medio"]
TURNOS = ["abst_1t", "bn_1t", "d_comparecimento", "d_bn"]


def residuos(df: pd.DataFrame, xcols: list[str], pesos: np.ndarray | None = None) -> tuple[np.ndarray, pd.Series]:
    """Mínimos quadrados com efeito fixo de município (transformação dentro do grupo); resíduo padronizado.

    Com `pesos`, médias de grupo e ajuste são ponderados, e o resíduo padronizado é e·sqrt(w)/sigma_w.
    """
    w = np.ones(len(df)) if pesos is None else np.asarray(pesos, dtype=float)
    grupo = df.groupby(["uf", "mun"]).ngroup().to_numpy()
    soma_w = np.bincount(grupo, weights=w)

    def centra(v: np.ndarray) -> np.ndarray:
        return v - (np.bincount(grupo, weights=w * v) / soma_w)[grupo]

    y = centra(df["y"].to_numpy(dtype=float))
    X = np.column_stack([centra(df[c].to_numpy(dtype=float)) for c in xcols])
    rw = np.sqrt(w)
    beta, *_ = np.linalg.lstsq(X * rw[:, None], y * rw, rcond=None)
    e = y - X @ beta
    gl = len(df) - len(xcols) - len(soma_w)
    sigma = np.sqrt((w * e ** 2).sum() / gl)
    return e * rw / sigma, pd.Series(beta, index=xcols)


def vizinhos(xyz: np.ndarray, k: int) -> np.ndarray:
    """k vizinhos mais próximos, excluindo o próprio ponto.

    Várias seções dividem o mesmo local (coordenadas idênticas); com empates em distância zero, o próprio índice
    pode não vir na primeira coluna da consulta, então ele é removido explicitamente.
    """
    _, idx = cKDTree(xyz).query(xyz, k=k + 1)
    nao_proprio = idx != np.arange(len(xyz))[:, None]
    ordem = np.argsort(~nao_proprio, axis=1, kind="stable")
    return np.take_along_axis(idx, ordem, axis=1)[:, :k]


def nomes_locais() -> pd.DataFrame:
    cols = ["SG_UF", "CD_MUNICIPIO", "NM_MUNICIPIO", "NR_ZONA", "NR_SECAO", "NM_LOCAL_VOTACAO", "DS_TIPO_LOCAL"]
    with zipfile.ZipFile(RAW / "D3" / "eleitorado_local_votacao_2026.zip") as z:
        df = pd.concat([pd.read_csv(z.open(n), sep=";", encoding="latin-1", dtype=str, usecols=cols)[cols]
                        for n in z.namelist() if n.lower().endswith(".csv")])
    df = df.drop_duplicates(cols[:5])
    df.columns = ["uf", "mun", "nm_mun", "zona", "secao", "nm_local", "tipo_local"]
    for c, w in (("mun", 5), ("zona", 4), ("secao", 4)):
        df[c] = df[c].str.zfill(w)
    return df


def margem_nacional(df: pd.DataFrame) -> float:
    """Diferença absoluta de votos entre os dois finalistas na base (sem o exterior)."""
    v13 = (df["y"] / 100 * df["votos_2t"]).sum()
    return float(abs(v13 - (df["votos_2t"].sum() - v13)))


def analisa(df: pd.DataFrame, xcols: list[str], viz: np.ndarray, idx_geo: np.ndarray, nomes: pd.DataFrame,
            pesos: np.ndarray | None, sufixo: str) -> tuple[dict, list[str]]:
    df = df.copy()
    z, beta = residuos(df, xcols, pesos)
    df["z"] = z
    df["p"] = 2 * stats.norm.sf(np.abs(z))
    df["anomala"], df["p_bh"], _, _ = multipletests(df["p"], alpha=Q_FDR, method="fdr_bh")
    an = df[df["anomala"]]

    # (b) direção
    pos = int((an["z"] > 0).sum())
    p_direcao = float(stats.binomtest(pos, len(an), 0.5).pvalue) if len(an) else np.nan

    # (a) agrupamento espacial no grafo de k vizinhos (seções com coordenadas)
    geo = df.iloc[idx_geo].reset_index(drop=True)
    rot = geo["anomala"].to_numpy(dtype=bool)
    obs = int((rot[:, None] & rot[viz]).sum())
    rng = np.random.default_rng(SEMENTE)
    perm = np.empty(PERMUTACOES)
    for i in range(PERMUTACOES):
        r = rng.permutation(rot)
        perm[i] = (r[:, None] & r[viz]).sum()
    p_espacial = float((1 + (perm >= obs).sum()) / (PERMUTACOES + 1))

    # componentes conexos de seções anômalas
    linhas_i = np.repeat(np.arange(len(geo)), K_VIZINHOS)
    colunas = viz.ravel()
    mask = rot[linhas_i] & rot[colunas]
    m = coo_matrix((np.ones(mask.sum()), (linhas_i[mask], colunas[mask])), shape=(len(geo), len(geo)))
    _, comp = connected_components(m, directed=False)
    geo["componente"] = np.where(rot, comp, -1)
    geo = geo.merge(nomes, on=CHAVE, how="left")
    tam = geo[geo["componente"] >= 0].groupby("componente").size()
    comps = (geo[geo["componente"].isin(tam[tam >= 3].index)]
             .groupby("componente")
             .agg(n_secoes=("secao", "size"), uf=("uf", "first"), nm_mun=("nm_mun", "first"),
                  municipios=("mun", "nunique"), locais=("local", "nunique"), local=("nm_local", "first"),
                  votos_2t_medio=("votos_2t", "mean"), z_medio=("z", "mean"),
                  z_positivos=("z", lambda s: int((s > 0).sum())))
             .sort_values("n_secoes", ascending=False))
    comps.to_csv(OUTPUT / "tables" / f"t2_componentes{sufixo}.csv")

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

    an_out = df[df["anomala"]].merge(nomes, on=CHAVE, how="left").sort_values("p")
    an_out[[*CHAVE, "nm_mun", "local", "nm_local", "tipo_local", "lat", "lon", "votos_2t", "y", "z", "p",
            "p_bh"]].to_csv(OUTPUT / "tables" / f"t2_secoes_anomalas{sufixo}.csv", index=False)
    beta.rename("coef_dentro_municipio").to_csv(OUTPUT / "tables" / f"t2_coeficientes{sufixo}.csv")

    indig = an_out["nm_local"].str.contains(r"ALDEIA|IND[IÍ]GENA|TUXAUA", case=False, regex=True, na=False)
    corte = df["votos_2t"].quantile(0.2)
    resumo = {"seções anômalas (FDR q=0,05)": len(an),
              "proporção anômala": len(an) / len(df),
              "anômalas com resíduo positivo (acima do previsto para o 13)": pos,
              "anômalas com resíduo negativo": len(an) - pos,
              "(b) p binomial de direção": p_direcao,
              "(a) pares vizinhos anômalo-anômalo: observado": obs,
              "(a) pares vizinhos anômalo-anômalo: esperado sob permutação": float(perm.mean()),
              "(a) p de permutação (unilateral)": p_espacial,
              "componentes com ≥ 3 seções anômalas": len(comps),
              f"anômalas no quintil inferior de tamanho (até {corte:.0f} votos)": int((an["votos_2t"] <= corte).sum()),
              "anômalas em locais com nome indígena (aldeia, escola indígena)": int(indig.sum()),
              "votos válidos (2º turno) somados nas seções anômalas": int(an["votos_2t"].sum()),
              "idem, em % da margem nacional entre os finalistas (exterior excluído)":
                  100 * an["votos_2t"].sum() / margem_nacional(df),
              "classificação T2": classe}
    corpo = ["| Métrica | Valor |", "|---|---|"]
    for k, v in resumo.items():
        corpo.append(f"| {k} | {v:.4g} |" if isinstance(v, float) else f"| {k} | {v} |")
    corpo += ["", "### Componentes com ≥ 3 seções anômalas", "", comps.head(20).round(2).to_markdown()]
    return resumo, corpo


def main() -> None:
    base = pd.read_parquet(PROCESSED / "t23_secoes_2026.parquet")
    locais = pd.read_parquet(PROCESSED / "t23_locais_2026.parquet")
    nomes = nomes_locais()
    t1 = sorted(c for c in base.columns if c.startswith("t1_c"))
    xcols = t1 + TURNOS + PERFIL
    contagem = {"seções na base (exceto exterior)": len(base),
                "sem 2º turno": int(base["y"].isna().sum()),
                "sem 1º turno": int(base[t1[0]].isna().sum()),
                "sem perfil do eleitorado (D3)": int(base["p_fem"].isna().sum())}
    df = base.dropna(subset=["y", *xcols]).reset_index(drop=True)
    df = df.merge(locais[[*CHAVE, "local", "lat", "lon"]], on=CHAVE, how="left")
    contagem["seções pareadas e completas (modelo)"] = len(df)

    idx_geo = np.flatnonzero(df["lat"].notna() & df["lon"].notna())
    contagem["seções com coordenadas válidas (critério a)"] = len(idx_geo)
    lat = np.radians(df["lat"].to_numpy()[idx_geo])
    lon = np.radians(df["lon"].to_numpy()[idx_geo])
    viz = vizinhos(np.column_stack([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)]), K_VIZINHOS)

    res_conf, corpo_conf = analisa(df, xcols, viz, idx_geo, nomes, None, "")
    res_pond, corpo_pond = analisa(df, xcols, viz, idx_geo, nomes, df["votos_2t"].to_numpy(),
                                   "_PONDERADO_EXPLORATORIO")
    for rotulo, r in (("confirmatório", {**contagem, **res_conf}), ("ponderado (exploratório)", res_pond)):
        print(f"== {rotulo}")
        for k, v in r.items():
            print(f"{k}: {v}")
    linhas = ["# T2 — resumo", "", "| Base | Valor |", "|---|---|"]
    linhas += [f"| {k} | {v} |" for k, v in contagem.items()]
    linhas += ["", "## A. Confirmatório (regras de `docs/desenho_T2_T3.md`)", ""] + corpo_conf
    linhas += ["", "## B. Sensibilidade exploratória: ponderação pelos votos da seção (DESVIOS.md)", ""] + corpo_pond
    linhas += ["", "Modelo: participação do candidato 13 no 2º turno (votos nominais dos dois finalistas) sobre o 1º "
               "turno da seção, abstenção e brancos/nulos, variações entre turnos e perfil do eleitorado (D3), com "
               "efeito fixo de município. Resíduo padronizado; Benjamini-Hochberg q = 0,05. Dado agregado: os "
               "coeficientes não descrevem comportamento individual. Fontes: TSE (D2, D3, D4); hashes em "
               "`data/raw/MANIFEST.csv`. Regras em `docs/desenho_T2_T3.md`."]
    (OUTPUT / "tables" / "t2_resumo.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
