"""T6 — série histórica de reversões de 2º turno (docs/desenho_T5_T6.md, seção T6).

Uso: python src/08_historical.py
Saídas: output/tables/t6_casos.csv, t6_resumo.md
"""

import io
import re
import zipfile

import numpy as np
import pandas as pd
import statsmodels.api as sm
from bs4 import BeautifulSoup
from scipy import stats

from common import OUTPUT, PROCESSED, RAW

ANOS_BR = [1989, 2002, 2006, 2010, 2014, 2018, 2022]
CAMPOS_1989 = ["DATA_GERACAO", "HORA_GERACAO", "ANO_ELEICAO", "NUM_TURNO", "DESCRICAO_ELEICAO", "SIGLA_UF",
               "SIGLA_UE", "CODIGO_CARGO", "NUMERO_CAND", "SQ_CANDIDATO", "NOME_CANDIDATO", "NOME_URNA_CANDIDATO",
               "DESCRICAO_CARGO", "COD_SIT_CAND_SUPERIOR", "DESC_SIT_CAND_SUPERIOR", "CODIGO_SIT_CANDIDATO",
               "DESC_SIT_CANDIDATO", "CODIGO_SIT_CAND_TOT", "DESC_SIT_CAND_TOT", "NUMERO_PARTIDO", "SIGLA_PARTIDO",
               "NOME_PARTIDO", "SEQUENCIAL_LEGENDA", "NOME_COLIGACAO", "COMPOSICAO_LEGENDA", "TOTAL_VOTOS"]
NAO_NOMINAIS = {"95", "96", "97", "98"}  # branco, nulo, anulado em apuração separada, nulo técnico


# --- Brasil (TSE) ------------------------------------------------------------------------------

def votos_brasil(ano: int) -> pd.DataFrame:
    """Votos nominais de Presidente por turno e candidato (cache reconstruível em data/processed)."""
    cache = PROCESSED / f"votos_presidente_{ano}.parquet"
    if cache.exists():
        return pd.read_parquet(cache)
    df = _votos_brasil(ano)
    df.to_parquet(cache, index=False)
    return df


def _votos_brasil(ano: int) -> pd.DataFrame:
    if ano == 1989:
        with zipfile.ZipFile(RAW / "D8" / "votacao_candidato_uf_1989.zip") as z:
            nome = next(n for n in z.namelist() if n.lower().endswith(".txt"))
            df = pd.read_csv(z.open(nome), sep=";", encoding="latin-1", header=None, names=CAMPOS_1989, dtype=str)
        df = df[df["DESCRICAO_CARGO"].str.upper() == "PRESIDENTE"]
        out = df.assign(turno=df["NUM_TURNO"].astype(int), candidato=df["NUMERO_CAND"],
                        votos=df["TOTAL_VOTOS"].astype(int))
        return out.groupby(["turno", "candidato"], as_index=False)["votos"].sum()
    if ano == 2026:
        cols = ["NR_TURNO", "CD_CARGO", "NR_VOTAVEL", "QT_VOTOS"]
        partes = []
        with zipfile.ZipFile(RAW / "D2" / "votacao_secao_2026_BR.zip") as z:
            nome = next(n for n in z.namelist() if n.lower().endswith(".csv"))
            for b in pd.read_csv(z.open(nome), sep=";", encoding="latin-1", usecols=cols, dtype=str,
                                 chunksize=2_000_000):
                b = b[(b["CD_CARGO"] == "1") & (~b["NR_VOTAVEL"].isin(NAO_NOMINAIS))]
                partes.append(b.assign(QT_VOTOS=b["QT_VOTOS"].astype(int))
                               .groupby(["NR_TURNO", "NR_VOTAVEL"], as_index=False)["QT_VOTOS"].sum())
        df = pd.concat(partes).groupby(["NR_TURNO", "NR_VOTAVEL"], as_index=False)["QT_VOTOS"].sum()
        return df.rename(columns={"NR_TURNO": "turno", "NR_VOTAVEL": "candidato", "QT_VOTOS": "votos"}).assign(
            turno=lambda d: d["turno"].astype(int))
    partes = []
    with zipfile.ZipFile(RAW / "D8" / f"votacao_candidato_munzona_{ano}.zip") as z:
        for nome in [n for n in z.namelist() if n.lower().endswith(".csv")]:
            df = pd.read_csv(z.open(nome), sep=";", encoding="latin-1", dtype=str)
            df = df[df["CD_CARGO"] == "1"]
            if df.empty:
                continue
            col = "QT_VOTOS_NOMINAIS_VALIDOS" if "QT_VOTOS_NOMINAIS_VALIDOS" in df else "QT_VOTOS_NOMINAIS"
            partes.append(df[["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_TURNO", "NR_CANDIDATO", col]]
                          .rename(columns={col: "votos"}))
    df = pd.concat(partes).drop_duplicates(["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_TURNO", "NR_CANDIDATO"])
    df = df.assign(turno=df["NR_TURNO"].astype(int), candidato=df["NR_CANDIDATO"], votos=df["votos"].astype(int))
    return df.groupby(["turno", "candidato"], as_index=False)["votos"].sum()


def caso(pais: str, ano: int, r1: pd.Series, r2: pd.Series, fonte: str, obs: str = "") -> dict:
    """r1, r2: participação (%) por candidato no 1º e no 2º turno."""
    r1 = r1.sort_values(ascending=False)
    lider, segundo = r1.index[0], r1.index[1]
    vencedor = r2.idxmax()
    return {
        "pais": pais, "ano": ano, "lider_1t": lider, "segundo_1t": segundo,
        "pct_lider_1t": round(float(r1.iloc[0]), 3), "pct_segundo_1t": round(float(r1.iloc[1]), 3),
        "margem_1t_pp": round(float(r1.iloc[0] - r1.iloc[1]), 3),
        "vencedor_2t": vencedor, "pct_vencedor_2t": round(float(r2.max()), 3),
        "margem_2t_lider_menos_segundo_pp": round(float(r2.get(lider, np.nan) - r2.get(segundo, np.nan)), 3),
        "finalistas_sao_top2": set(r2.index) == {lider, segundo},
        "reversao": vencedor != lider, "fonte": fonte, "obs": obs,
    }


def casos_brasil() -> list[dict]:
    casos = []
    for ano in ANOS_BR + [2026]:
        v = votos_brasil(ano)
        r = {t: (g.set_index("candidato")["votos"] / g["votos"].sum() * 100) for t, g in v.groupby("turno")}
        fonte = "TSE D2" if ano == 2026 else "TSE D8"
        casos.append(caso("Brasil", ano, r[1], r[2][r[2] > 0], fonte,
                          "percentuais sobre votos nominais (1989: sem brancos, que então contavam como válidos)"
                          if ano == 1989 else "percentuais sobre votos nominais válidos"))
    return casos


# --- exterior (Wikipedia, D10) -----------------------------------------------------------------

_ROTULOS_NAO_CANDIDATO = re.compile(
    r"valid|blank|null|invalid|spoil|total|registered|turnout|abstention|source|vote[s]? cast|none of|"
    r"en blanco|nulos|eligible|void", re.I)


def _num(x) -> float:
    if pd.isna(x):
        return np.nan
    s = re.sub(r"\[.*?\]", "", str(x)).replace(",", "").replace("%", "").strip()
    try:
        return float(s)
    except ValueError:
        return np.nan


def tabela_resultados(html: str) -> pd.DataFrame | None:
    """Primeira tabela com colunas "First round"/"Second round" e subcolunas "%"; None se não houver 2º turno."""
    soup = BeautifulSoup(html, "lxml")
    for tag in soup.find_all(["td", "th"]):
        for attr in ("rowspan", "colspan"):
            if tag.has_attr(attr):
                dig = re.sub(r"\D", "", tag[attr])
                tag[attr] = dig or "1"
    for tabela in soup.find_all("table"):
        cab = tabela.get_text(" ")
        if "First round" not in cab or "Second round" not in cab:
            continue
        try:
            df = pd.read_html(io.StringIO(str(tabela)))[0]
        except ValueError:
            continue
        if not isinstance(df.columns, pd.MultiIndex):
            continue
        c1 = [c for c in df.columns if str(c[0]).startswith("First round") and str(c[1]).strip() == "%"]
        c2 = [c for c in df.columns if str(c[0]).startswith("Second round") and str(c[1]).strip() == "%"]
        cn = [c for c in df.columns if str(c[0]).startswith("Candidate")]
        if c1 and c2 and cn:
            return pd.DataFrame({"candidato": df[cn[-1]].astype(str), "pct1": df[c1[0]].map(_num),
                                 "pct2": df[c2[0]].map(_num)})
    return None


def casos_exterior() -> tuple[list[dict], list[dict]]:
    manifesto = pd.read_csv(RAW / "MANIFEST.csv", dtype=str)
    casos, sem_2t = [], []
    for arq in sorted((RAW / "D10").glob("*.html")):
        pais_slug, ano, _ = arq.stem.split("_", 2)
        pais = {"france": "França", "chile": "Chile", "colombia": "Colômbia", "argentina": "Argentina",
                "peru": "Peru"}[pais_slug]
        rel = arq.relative_to(RAW).as_posix()
        fonte = manifesto.loc[manifesto["arquivo"] == rel, "url"].iloc[0]
        t = tabela_resultados(arq.read_text(encoding="utf-8"))
        if t is None:
            sem_2t.append({"pais": pais, "ano": int(ano), "fonte": fonte})
            continue
        t = t[~t["candidato"].str.contains(_ROTULOS_NAO_CANDIDATO) & t["pct1"].notna()]
        t = t.drop_duplicates("candidato").set_index("candidato")
        r2 = t["pct2"].dropna()
        r2 = r2[r2 > 0]
        soma1, soma2 = t["pct1"].sum(), r2.sum()
        obs = "" if (abs(soma1 - 100) <= 1.5 and abs(soma2 - 100) <= 1.5 and len(r2) == 2) else \
            f"VERIFICAR: soma 1º turno={soma1:.2f}, soma 2º turno={soma2:.2f}, finalistas={len(r2)}"
        if pais == "Colômbia" and obs and len(r2) == 2 and soma1 <= 100 and soma2 <= 100:
            # na Colômbia o voto em branco é válido: os percentuais da fonte somam menos de 100 entre candidatos
            obs = (f"percentuais sobre votos válidos incluindo o voto em branco (válido na Colômbia); "
                   f"soma dos candidatos: 1º turno={soma1:.2f}, 2º turno={soma2:.2f}")
        casos.append(caso(pais, int(ano), t["pct1"], r2, fonte, obs))
    return casos, sem_2t


# --- estimativas ----------------------------------------------------------------------------------

def clopper_pearson(k: int, n: int) -> tuple[float, float]:
    lo = 0.0 if k == 0 else stats.beta.ppf(0.025, k, n - k + 1)
    hi = 1.0 if k == n else stats.beta.ppf(0.975, k + 1, n - k)
    return float(lo), float(hi)


def main() -> None:
    br = casos_brasil()
    ext, sem_2t = casos_exterior()
    casos = pd.DataFrame(br + ext).sort_values(["pais", "ano"]).reset_index(drop=True)
    casos["caso_2026_brasil"] = (casos["pais"] == "Brasil") & (casos["ano"] == 2026)
    OUTPUT.joinpath("tables").mkdir(parents=True, exist_ok=True)
    casos.to_csv(OUTPUT / "tables" / "t6_casos.csv", index=False)
    pd.DataFrame(sem_2t).to_csv(OUTPUT / "tables" / "t6_eleicoes_sem_2turno.csv", index=False)

    problemas = casos[(casos["obs"].str.startswith("VERIFICAR")) | (~casos["finalistas_sao_top2"])]
    base = casos[~casos["caso_2026_brasil"]]
    m2026 = float(casos.loc[casos["caso_2026_brasil"], "margem_1t_pp"].iloc[0])

    # Brasil isolado, 1989–2022
    b = base[base["pais"] == "Brasil"]
    k_b, n_b = int(b["reversao"].sum()), len(b)
    laplace = (k_b + 1) / (n_b + 2)
    cp_b = clopper_pearson(k_b, n_b)

    # base combinada: logística reversão ~ margem
    y = base["reversao"].astype(int).to_numpy()
    X = sm.add_constant(base["margem_1t_pp"].to_numpy())
    fit = sm.Logit(y, X).fit(disp=False)
    x0 = np.array([1.0, m2026])
    eta = float(x0 @ fit.params)
    se = float(np.sqrt(x0 @ fit.cov_params() @ x0))
    expit = lambda z: 1 / (1 + np.exp(-z))  # noqa: E731
    p_hat, p_lo, p_hi = expit(eta), expit(eta - 1.96 * se), expit(eta + 1.96 * se)

    # verificação: 10 casos de margem mais próxima
    viz = base.assign(d=(base["margem_1t_pp"] - m2026).abs()).nsmallest(10, "d")
    k_v = int(viz["reversao"].sum())
    cp_v = clopper_pearson(k_v, 10)

    resumo = {
        "casos na base (sem Brasil 2026)": len(base),
        "casos por país": base.groupby("pais").size().to_dict(),
        "reversões na base": int(base["reversao"].sum()),
        "eleições sem 2º turno (excluídas)": len(sem_2t),
        "casos com alerta de extração": len(problemas),
        "margem do 1º turno, Brasil 2026 (p.p.)": m2026,
        "Brasil 1989–2022: reversões / 2ºs turnos": f"{k_b} / {n_b}",
        "Brasil: regra de sucessão de Laplace": laplace,
        "Brasil: limite superior IC 95% (regra de três, 3/n)": 3 / n_b,
        "Brasil: IC 95% Clopper-Pearson": cp_b,
        "logística: coeficiente da margem (por p.p.)": float(fit.params[1]),
        "logística: p-valor do coeficiente": float(fit.pvalues[1]),
        "logística: P(reversão dada a margem de 2026)": p_hat,
        "logística: IC 95% (delta, escala logit)": (p_lo, p_hi),
        "10 casos de margem mais próxima: reversões": f"{k_v} / 10",
        "10 casos de margem mais próxima: IC 95% Clopper-Pearson": cp_v,
        "10 casos de margem mais próxima: faixa de margens (p.p.)":
            (float(viz["margem_1t_pp"].min()), float(viz["margem_1t_pp"].max())),
    }
    linhas = ["# T6 — resumo", "", "| Métrica | Valor |", "|---|---|"]
    for k, v in resumo.items():
        if isinstance(v, float):
            v = f"{v:.4g}"
        elif isinstance(v, tuple):
            v = "(" + ", ".join(f"{x:.4g}" for x in v) + ")"
        linhas.append(f"| {k} | {v} |")
        print(f"{k}: {v}")
    linhas += ["", "## Casos", "", casos.drop(columns=["fonte"]).to_markdown(index=False), "",
               "Fontes: Brasil, TSE (D8; 2026 em D2); demais países, Wikipedia em inglês com revisões fixadas "
               "(D10, URLs com `oldid` na coluna `fonte` de `t6_casos.csv`), fonte secundária. Hashes em "
               "`data/raw/MANIFEST.csv`. Regras em `docs/desenho_T5_T6.md`. O caso Brasil 2026 aparece na tabela "
               "e fica fora de todas as estimativas."]
    if len(problemas):
        print("\nALERTAS DE EXTRAÇÃO:\n" + problemas[["pais", "ano", "obs", "finalistas_sao_top2"]].to_string())
    (OUTPUT / "tables" / "t6_resumo.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
