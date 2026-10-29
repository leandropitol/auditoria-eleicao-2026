"""EXPLORATÓRIO — sensibilidades e detalhamentos da revisão v1.1 (docs/plano_v1_1.md, carimbado antes da execução).

Uso: python src/13_sensibilidades_v11.py
Saídas: output/tables/v11_*.csv, output/tables/v11_EXPLORATORIO.md, output/relatorio/dados_v11.json
"""

import importlib.util
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from esda.moran import Moran, Moran_Local
from scipy import stats
from statsmodels.stats.multitest import multipletests

from common import OUTPUT, PROCESSED, RAW, SEMENTE

T = OUTPUT / "tables"
ANOS = [2014, 2018, 2022, 2026]
PADRAO_INDIGENA = r"ALDEIA|IND[IÍ]GENA|TUXAUA"


def _modulo(nome: str, arquivo: str):
    spec = importlib.util.spec_from_file_location(nome, Path(__file__).with_name(arquivo))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


T2 = _modulo("t2", "03_pair_sections.py")
ESP = _modulo("esp", "05_spatial.py")


def margem_oficial() -> float:
    v = pd.read_parquet(PROCESSED / "votos_presidente_2026.parquet").query("turno == 2")["votos"]
    return float(v.max() - v.min())


def pior_caso(votos_anomalas: float, margem: float) -> float:
    """Mudança máxima de margem (% da margem oficial) se todos os votos de um finalista nas seções fossem do outro."""
    return 100 * 2 * votos_anomalas / margem


# --- T3 sem Censo -----------------------------------------------------------------------------------

def t3_sem_censo() -> pd.DataFrame:
    malha = gpd.read_file(f"zip://{(RAW / 'D7' / 'BR_Municipios_2022.zip').as_posix()}!BR_Municipios_2022.shp")
    linhas, lisas = [], {}
    for ano in ANOS:
        df = pd.read_parquet(PROCESSED / f"t23_municipal_{ano}.parquet")
        t1 = sorted(c for c in df.columns if c.startswith("t1_c"))
        df = df.dropna(subset=["y", "cd_ibge", *t1]).sort_values("votos_2t", ascending=False).drop_duplicates("cd_ibge")
        z = df.copy()
        for c in t1:
            z[c] = (z[c] - z[c].mean()) / z[c].std()
        fit = smf.mixedlm("y ~ " + " + ".join(t1), z, groups=z["uf"]).fit(reml=True)
        z["residuo"] = z["y"] - fit.fittedvalues
        g = malha.merge(z[["cd_ibge", "residuo"]], left_on="CD_MUN", right_on="cd_ibge").reset_index(drop=True)
        w = ESP.pesos(g)
        r2 = float(np.corrcoef(z["y"], fit.fittedvalues)[0, 1] ** 2)
        for perms in (999, 9999):
            np.random.seed(SEMENTE)
            mi = Moran(g["residuo"].to_numpy(), w, permutations=perms)
            lisa = Moran_Local(g["residuo"].to_numpy(), w, permutations=perms, seed=SEMENTE)
            rej, _, _, _ = multipletests(lisa.p_sim, alpha=0.05, method="fdr_bh")
            cluster = rej & np.isin(lisa.q, [1, 3])
            lisas[(ano, perms)] = set(g.loc[cluster, "CD_MUN"])
            linhas.append({"ano": ano, "permutacoes": perms, "r2_condicional": r2, "I": mi.I, "p_sim": mi.p_sim,
                           "clusters_fdr": int(cluster.sum())})
            print(linhas[-1], flush=True)
    res = pd.DataFrame(linhas)
    for perms in (999, 9999):
        c26 = lisas[(2026, perms)]
        anteriores = set().union(*(lisas[(a, perms)] for a in ANOS[:-1]))
        res.loc[(res["ano"] == 2026) & (res["permutacoes"] == perms), "clusters_2026_exclusivos"] = len(c26 - anteriores)
    res.to_csv(T / "v11_t3_sem_censo.csv", index=False)
    return res


# --- T2 especificações alternativas -----------------------------------------------------------------

def t2_especificacoes(margem: float) -> pd.DataFrame:
    base = pd.read_parquet(PROCESSED / "t23_secoes_2026.parquet")
    locais = pd.read_parquet(PROCESSED / "t23_locais_2026.parquet")
    nomes = T2.nomes_locais()
    t1 = sorted(c for c in base.columns if c.startswith("t1_c"))
    xfull = t1 + T2.TURNOS + T2.PERFIL
    df = base.dropna(subset=["y", *xfull]).reset_index(drop=True)
    df = df.merge(locais[[*T2.CHAVE, "local", "lat", "lon"]], on=T2.CHAVE, how="left")
    df = df.merge(nomes[[*T2.CHAVE, "nm_local"]], on=T2.CHAVE, how="left")
    df["indigena"] = df["nm_local"].str.contains(PADRAO_INDIGENA, case=False, regex=True, na=False)
    df = df.drop(columns="nm_local")  # analisa() junta os nomes de novo para anotar as saídas

    def prepara(d):
        d = d.reset_index(drop=True)
        idx = np.flatnonzero(d["lat"].notna() & d["lon"].notna())
        lat, lon = np.radians(d["lat"].to_numpy()[idx]), np.radians(d["lon"].to_numpy()[idx])
        viz = T2.vizinhos(np.column_stack([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)]),
                          T2.K_VIZINHOS)
        return d, idx, viz

    v13 = df["y"] / 100 * df["votos_2t"]
    logit = df.copy()
    logit["y"] = np.log((v13 + 0.5) / (df["votos_2t"] - v13 + 0.5))
    especs = {
        "S1_sem_perfil_D3": (df, t1 + T2.TURNOS, None),
        "S2_logit_ponderado": (logit, xfull, "votos_2t"),
        "S3_ponderado_sem_locais_indigenas": (df[~df["indigena"]], xfull, "votos_2t"),
    }
    linhas = []
    for nome, (d, xcols, peso) in especs.items():
        d, idx, viz = prepara(d)
        res, _ = T2.analisa(d, xcols, viz, idx, nomes, None if peso is None else d[peso].to_numpy(), f"_v11_{nome}")
        an = pd.read_csv(T / f"t2_secoes_anomalas_v11_{nome}.csv")
        linhas.append({"especificacao": nome, "secoes_no_modelo": len(d), "anomalas": len(an),
                       "positivas_13": int((an["z"] > 0).sum()), "negativas_13": int((an["z"] < 0).sum()),
                       "p_direcao": res["(b) p binomial de direção"], "p_agrupamento": res["(a) p de permutação (unilateral)"],
                       "votos_nas_anomalas": int(an["votos_2t"].sum()),
                       "pior_caso_pct_margem": pior_caso(an["votos_2t"].sum(), margem),
                       "classificacao_pelos_criterios": res["classificação T2"]})
        print(linhas[-1], flush=True)
    out = pd.DataFrame(linhas)
    out.to_csv(T / "v11_t2_especificacoes.csv", index=False)
    return out


def t2_distribuicao() -> dict:
    """Distribuição das 461 seções anômalas confirmatórias (tamanho, |z|, UF) e contagem antes/depois do FDR."""
    base = pd.read_parquet(PROCESSED / "t23_secoes_2026.parquet")
    an = pd.read_csv(T / "t2_secoes_anomalas.csv", dtype={"mun": str, "zona": str, "secao": str})
    faixas = [0, 100, 150, 200, 250, 300, 1000]
    rot = ["até 100", "101–150", "151–200", "201–250", "251–300", "mais de 300"]
    tam_all = pd.cut(base["votos_2t"], faixas, labels=rot).value_counts(sort=False)
    tam_an = pd.cut(an["votos_2t"], faixas, labels=rot).value_counts(sort=False)
    tab_tam = pd.DataFrame({"secoes_total": tam_all, "anomalas": tam_an})
    tab_tam["pct_anomalas_na_faixa"] = 100 * tab_tam["anomalas"] / tab_tam["secoes_total"]
    tab_tam.to_csv(T / "v11_t2_anomalas_por_tamanho.csv")
    tab_z = pd.cut(an["z"].abs(), [0, 5, 6, 8, 100], labels=["4,5–5", "5–6", "6–8", "> 8"]).value_counts(sort=False)
    tab_uf = an["uf"].value_counts()
    pd.DataFrame({"anomalas": tab_uf}).to_csv(T / "v11_t2_anomalas_por_uf.csv")
    p_sem_correcao = 2 * stats.norm.sf(np.abs(an["z"]))
    return {"por_tamanho": tab_tam, "por_z": tab_z, "por_uf": tab_uf, "z_min": float(an["z"].abs().min()),
            "z_max": float(an["z"].abs().max()), "p_bh_max": float(an["p_bh"].max()),
            "p_sem_correcao_max": float(p_sem_correcao.max())}


# --- T1 detalhamento ---------------------------------------------------------------------------------

def t1_detalhe() -> dict:
    val = pd.read_parquet(PROCESSED / "t1_bu_validacao.parquet")
    amostra = pd.read_csv(PROCESSED / "t1_amostra.csv", dtype=str)
    verif = val[val["situacao"] == "bu_verificado"]
    n = len(verif)
    sup = 1 - 0.025 ** (1 / n)
    w = verif["peso"].astype(float).to_numpy()
    n_eff = w.sum() ** 2 / (w ** 2).sum()
    sup_pond = 1 - 0.025 ** (1 / n_eff)
    ag = val[val["situacao"].str.startswith("secao_agregada")].copy()
    ag["principal"] = ag["situacao"].str.extract(r"principal=(\d+)")[0]
    chaves_verif = set(zip(verif["uf"], verif["mun"], verif["zona"], verif["secao"]))
    ag["principal_verificada"] = [(r.uf, r.mun, r.zona, r.principal) in chaves_verif for r in ag.itertuples()]
    sem = val[val["situacao"].str.startswith("sem_bu")]["situacao"].value_counts()
    return {"n": n, "ic_sup": sup, "n_eff_kish": n_eff, "ic_sup_ponderado": sup_pond,
            "agregadas": len(ag), "agregadas_principal_verificada": int(ag["principal_verificada"].sum()),
            "sem_bu": {k: int(v) for k, v in sem.items()}, "sorteadas": len(amostra)}


def main() -> None:
    margem = margem_oficial()
    t1 = t1_detalhe()
    print(t1, flush=True)
    dist = t2_distribuicao()
    conf = pd.read_csv(T / "t2_secoes_anomalas.csv")
    pond = pd.read_csv(T / "t2_secoes_anomalas_PONDERADO_EXPLORATORIO.csv")
    pior = {"confirmatorio": pior_caso(conf["votos_2t"].sum(), margem),
            "ponderado": pior_caso(pond["votos_2t"].sum(), margem)}
    t2e = t2_especificacoes(margem)
    t3 = t3_sem_censo()

    fmt = lambda x, c=2: f"{x:,.{c}f}".replace(",", "X").replace(".", ",").replace("X", ".")  # noqa: E731
    md = ["# Revisão v1.1 — sensibilidades e detalhamentos (EXPLORATÓRIO)", "",
          "Plano carimbado antes da execução: `docs/plano_v1_1.md` (+ `.ots`). Nada aqui altera a classificação "
          "confirmatória.", "",
          "## T1 — intervalo e seções excluídas", "",
          f"- Clopper-Pearson exato, k = 0, n = {t1['n']}: limite superior 1 − 0,025^(1/n) = "
          f"{fmt(100 * t1['ic_sup'], 4)}%.",
          f"- Com pesos amostrais (tamanho efetivo de Kish = {fmt(t1['n_eff_kish'], 0)}): limite superior "
          f"{fmt(100 * t1['ic_sup_ponderado'], 4)}%.",
          f"- Seções agregadas sorteadas: {t1['agregadas']}; em {t1['agregadas_principal_verificada']} delas a "
          "seção principal também foi sorteada e verificada (as demais têm votos no BU de uma principal não sorteada).",
          f"- Seções sem BU \"Totalizado\": {t1['sem_bu']}.",
          "- Escopo: a reconciliação BU × totalização não verifica se a urna registrou a intenção do eleitor.", "",
          "## T2 — pior caso", "",
          f"- Confirmatório (461 seções): {fmt(pior['confirmatorio'])}% da margem oficial de {fmt(margem, 0)} votos.",
          f"- Ponderado (52 seções): {fmt(pior['ponderado'])}% da margem.", "",
          "## T2 — distribuição das 461 seções (confirmatório)", "",
          dist["por_tamanho"].round(3).to_markdown(), "",
          f"|z| entre {fmt(dist['z_min'])} e {fmt(dist['z_max'])}; p corrigido (BH) máximo "
          f"{dist['p_bh_max']:.4g}; p sem correção máximo {dist['p_sem_correcao_max']:.3g}.", "",
          dist["por_z"].to_frame("anomalas").to_markdown(), "",
          "## T2 — especificações alternativas", "", t2e.round(4).to_markdown(index=False), "",
          "## T3 — sem covariáveis do Censo 2022", "", t3.round(4).to_markdown(index=False), "",
          "Fontes: TSE (D1–D4), IBGE (D7); hashes em `data/raw/MANIFEST.csv`."]
    (T / "v11_EXPLORATORIO.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    dados = {"t1": {k: (v if not isinstance(v, float) else v) for k, v in t1.items()},
             "pior_caso": pior, "margem_oficial": margem,
             "t2_especificacoes": t2e.to_dict(orient="records"),
             "t2_por_tamanho": dist["por_tamanho"].reset_index(names="faixa").to_dict(orient="records"),
             "t3_sem_censo": t3.to_dict(orient="records")}
    (OUTPUT / "relatorio" / "dados_v11.json").write_text(json.dumps(dados, ensure_ascii=False, indent=1, default=str),
                                                          encoding="utf-8")


if __name__ == "__main__":
    main()
