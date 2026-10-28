"""T5 — auditoria do desempenho das pesquisas no 2º turno (docs/desenho_T5_T6.md, seção T5).

Uso: python src/07_polls.py
Saídas: output/tables/t5_pesquisas_2t.csv (todas as linhas extraídas), t5_pesquisas_finais.csv, t5_resumo.md
"""

import importlib.util
import io
import re
import unicodedata
import zipfile
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from scipy import stats

from common import OUTPUT, RAW

ANOS = [2010, 2014, 2018, 2022, 2026]
DATA_1T = {2010: date(2010, 10, 3), 2014: date(2014, 10, 5), 2018: date(2018, 10, 7),
           2022: date(2022, 10, 2), 2026: date(2026, 10, 4)}
DATA_2T = {2010: date(2010, 10, 31), 2014: date(2014, 10, 26), 2018: date(2018, 10, 28),
           2022: date(2022, 10, 30), 2026: date(2026, 10, 25)}
MESES = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct",
                                      "nov", "dec"], 1)}
NAO_CANDIDATO = re.compile(r"poll|firm|publisher|client|date|period|sample|abst|undec|blank|null|lead|margin|"
                           r"link|other|aggregat|update|ref", re.I)
LINHA_RESULTADO = re.compile(r"result|election|official|tse", re.I)

# Padronização de nomes de institutos entre anos e fontes. Fusões só quando é a mesma empresa;
# Ibope (até 2020) e Ipec (desde 2021) ficam separados: o Ipec é empresa nova, criada por ex-executivos do Ibope.
ALIAS = {
    "ibope inteligencia": "ibope", "ibope": "ibope",
    "datafolha": "datafolha", "ipec": "ipec", "quaest": "quaest", "genial/quaest": "quaest",
    "atlasintel": "atlasintel", "atlas": "atlasintel", "atlas intel": "atlasintel",
    "parana pesquisas": "parana pesquisas", "vox populi": "vox populi", "mda": "mda", "cnt/mda": "mda",
    "sensus": "sensus", "poderdata": "poderdata", "futura": "futura", "ideia": "ideia", "ideia big data": "ideia",
    "real time big data": "real time big data", "modalmais/futura": "futura", "abc dados": "abc dados",
    "datatempo": "datatempo", "gerp": "gerp", "brasmarket": "brasmarket", "ipespe": "ipespe",
    "nexus": "nexus", "datapoder360": "poderdata", "travessia": "travessia", "verita": "verita",
    "fsb comunicacao": "fsb", "fsb pesquisa": "fsb", "idea big data": "ideia", "idea": "ideia",
    "realtime big data": "real time big data", "real time": "real time big data",
}


def _sem_acento(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)).lower()


def instituto(nome: str, publisher_primeiro: bool = False) -> str:
    """Nome padronizado do instituto.

    A fonte mistura "Instituto/Cliente" e "Cliente/Instituto" (às vezes na mesma tabela). Entre os segmentos do
    nome, vale o que corresponde a um instituto conhecido (valores de ALIAS). Sem correspondência, vale o
    segmento indicado pelo cabeçalho da coluna ("Publisher/Pollster": o último; senão, o primeiro).
    """
    chave = _sem_acento(re.sub(r"\[.*?\]", "", str(nome)))
    chave = re.sub(r"archived \S+ at the wayback machine", "", chave).strip(" .*")
    if chave in ALIAS:
        return ALIAS[chave]
    partes = [x.strip(" .*") for x in re.split(r"[/(]| for | para ", chave) if x.strip(" .*)")]
    conhecidos = [ALIAS[x] for x in partes if x in ALIAS]
    if conhecidos:
        return conhecidos[0]
    return partes[-1] if (publisher_primeiro and len(partes) > 1) else partes[0]


def _t6():
    spec = importlib.util.spec_from_file_location("t6", Path(__file__).with_name("08_historical.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def finalistas(ano: int) -> tuple[dict, dict]:
    """(números e participações oficiais no 2º turno de A e B, tokens de nome por número)."""
    t6 = _t6()
    v = t6.votos_brasil(ano)
    r1 = v[v["turno"] == 1].set_index("candidato")["votos"].sort_values(ascending=False)
    a, b = r1.index[0], r1.index[1]
    r2 = v[v["turno"] == 2].set_index("candidato")["votos"]
    oficial = {"A": a, "B": b, "votos_A": int(r2[a]), "votos_B": int(r2[b])}
    return oficial, nomes_candidatos(ano, [a, b])


def nomes_candidatos(ano: int, numeros: list[str]) -> dict:
    tokens = {n: set() for n in numeros}
    if ano == 2026:
        with zipfile.ZipFile(RAW / "D2" / "votacao_secao_2026_BR.zip") as z:
            nome = next(n for n in z.namelist() if n.lower().endswith(".csv"))
            df = pd.read_csv(z.open(nome), sep=";", encoding="latin-1", dtype=str,
                             usecols=["NR_VOTAVEL", "NM_VOTAVEL"], nrows=200_000)
        pares = df.drop_duplicates().itertuples(index=False)
    else:
        with zipfile.ZipFile(RAW / "D8" / f"votacao_candidato_munzona_{ano}.zip") as z:
            # o menor arquivo com linhas de Presidente basta para os nomes
            for info in sorted((i for i in z.infolist() if i.filename.lower().endswith(".csv")),
                               key=lambda i: i.file_size):
                df = pd.read_csv(z.open(info), sep=";", encoding="latin-1", dtype=str)
                df = df[df["CD_CARGO"] == "1"]
                if len(df):
                    break
        pares = [(r.NR_CANDIDATO, f"{r.NM_CANDIDATO} {r.NM_URNA_CANDIDATO}")
                 for r in df.drop_duplicates("NR_CANDIDATO").itertuples()]
    for numero, nome in pares:
        if numero in tokens:
            tokens[numero] |= {t for t in re.findall(r"[a-z]+", _sem_acento(nome)) if len(t) > 2}
    return tokens


def _data_fim(texto: str, ano: int) -> date | None:
    s = _sem_acento(re.sub(r"\[.*?\]", "", str(texto)))
    anos = [int(y) for y in re.findall(r"(?:19|20)\d{2}", s)]
    y = anos[-1] if anos else ano
    candidatos = []
    for d, m in re.findall(r"(?<!\d)(\d{1,2})\s*([a-z]{3})[a-z]*", s):
        if m in MESES:
            candidatos.append((MESES[m], int(d)))
    for m, d1, d2 in re.findall(r"([a-z]{3})[a-z]*\.?\s*(\d{1,2})(?!\d)(?:\s*[-–]\s*(\d{1,2})(?!\d))?", s):
        if m in MESES:
            candidatos.append((MESES[m], int(d2 or d1)))
    if not candidatos:
        return None
    m, d = max(candidatos)
    try:
        return date(y, m, d)
    except ValueError:
        return None


def _pct(x) -> float:
    s = re.sub(r"\[.*?\]", "", str(x)).replace("%", "").replace(",", ".").strip()
    try:
        return float(s)
    except ValueError:
        return np.nan


def _n(x) -> float:
    s = re.sub(r"\[.*?\]", "", str(x))
    s = re.sub(r"[^\d]", "", s)
    return float(s) if s else np.nan


def _rotulo(c) -> str:
    partes = c if isinstance(c, tuple) else (c,)
    return " ".join(dict.fromkeys(str(x) for x in partes if not str(x).startswith("Unnamed")))


def pesquisas_ano(ano: int, tokens: dict, oficial: dict) -> pd.DataFrame:
    arq = next((RAW / "D9").glob(f"pesquisas_{ano}_rev*.html"))
    soup = BeautifulSoup(arq.read_text(encoding="utf-8"), "lxml")
    linhas, nivel_secao, dentro = [], None, False
    for el in soup.find_all(["h2", "h3", "h4", "table"]):
        if el.name != "table":
            nivel = int(el.name[1])
            if el.get_text(strip=True).startswith("Second round"):
                dentro, nivel_secao = True, nivel
            elif dentro and nivel <= nivel_secao:
                dentro = False
            continue
        if not dentro:
            continue
        try:
            df = pd.read_html(io.StringIO(str(el)))[0]
        except ValueError:
            continue
        rot = [_rotulo(c) for c in df.columns]
        cand = [i for i, r in enumerate(rot) if not NAO_CANDIDATO.search(r)]
        mapa = {}
        for i in cand:
            toks = set(re.findall(r"[a-z]+", _sem_acento(rot[i])))
            achados = [n for n, tk in tokens.items() if toks & tk]
            mapa[i] = achados[0] if len(achados) == 1 else None
        if sorted(v for v in mapa.values() if v) != sorted([oficial["A"], oficial["B"]]) or None in mapa.values():
            continue
        i_inst = next((i for i, r in enumerate(rot) if re.search(r"poll|firm|publisher", r, re.I)), None)
        i_data = next((i for i, r in enumerate(rot) if re.search(r"date|period", r, re.I)), None)
        if i_inst is None or i_data is None:  # agregadores e tabelas sem pesquisa individual
            continue
        i_n = next((i for i, r in enumerate(rot) if re.search(r"sample", r, re.I)), None)
        i_a = next(i for i, v in mapa.items() if v == oficial["A"])
        i_b = next(i for i, v in mapa.items() if v == oficial["B"])
        for _, r in df.iterrows():
            nome = str(r.iloc[i_inst])
            if LINHA_RESULTADO.search(nome) or nome == rot[i_inst]:
                continue
            linhas.append({"ano": ano, "fonte_tabela": arq.name, "instituto_original": nome,
                           "instituto": instituto(nome, bool(re.search(r"publisher", rot[i_inst], re.I))),
                           "periodo": r.iloc[i_data],
                           "fim_campo": _data_fim(r.iloc[i_data], ano),
                           "n": _n(r.iloc[i_n]) if i_n is not None else np.nan,
                           "pct_A": _pct(r.iloc[i_a]), "pct_B": _pct(r.iloc[i_b])})
    return pd.DataFrame(linhas)


def registro_tse(ano: int) -> pd.DataFrame:
    arq = RAW / "D5" / f"pesquisa_eleitoral_{ano}.zip"
    if not arq.exists():
        return pd.DataFrame()
    with zipfile.ZipFile(arq) as z:
        df = pd.concat([pd.read_csv(z.open(n), sep=";", encoding="latin-1", dtype=str)
                        for n in z.namelist() if n.lower().endswith(".csv")], ignore_index=True)
    df = df.rename(columns={"DS_CARGOS": "DS_CARGO", "QT_ENTREVISTADOS": "QT_ENTREVISTADO"})
    df = df[(df["SG_UF"] == "BR") & df["DS_CARGO"].str.contains("Presidente", case=False, na=False)]
    # 2014/2022/2026: "AAAA-MM-DD hh:mm:ss"; 2018: "DD/MM/AAAA"
    fim = df["DT_FIM_PESQUISA"].str[:10]
    df["fim_campo"] = pd.to_datetime(fim, format="%Y-%m-%d", errors="coerce").fillna(
        pd.to_datetime(fim, format="%d/%m/%Y", errors="coerce")).dt.date
    df["inst_tse"] = (df["NM_EMPRESA"].fillna("") + " " + df["NM_EMPRESA_FANTASIA"].fillna("")).map(_sem_acento)
    return df[["NR_PROTOCOLO_REGISTRO", "NM_EMPRESA", "inst_tse", "fim_campo", "QT_ENTREVISTADO"]]


def cruza_tse(finais: pd.DataFrame) -> pd.DataFrame:
    out = []
    for ano, g in finais.groupby("ano"):
        reg = registro_tse(ano)
        for r in g.itertuples():
            cand = reg[(reg["fim_campo"] == r.fim_campo) & reg["inst_tse"].str.contains(
                re.escape(r.instituto.split()[0]), na=False)] if len(reg) else reg
            cand = cand.drop_duplicates("NR_PROTOCOLO_REGISTRO") if len(cand) else cand
            ns = {float(x) for x in cand["QT_ENTREVISTADO"].dropna()} if len(cand) else set()
            mesmo_n = cand[cand["QT_ENTREVISTADO"].astype(float) == r.n] if len(cand) else cand
            out.append({"protocolo_tse": ";".join((mesmo_n if len(mesmo_n) else cand)["NR_PROTOCOLO_REGISTRO"])
                        if len(cand) else "",
                        "n_tse": ";".join(sorted(set(cand["QT_ENTREVISTADO"]))) if len(cand) else "",
                        "registro_tse": ("sem registro no portal" if ano == 2010 else
                                         "n confere" if r.n in ns else
                                         "registro na data, n difere" if len(cand) else "não localizado")})
    return pd.concat([finais.reset_index(drop=True), pd.DataFrame(out)], axis=1)


def analisa(validas: pd.DataFrame, oficiais: dict, sufixo: str) -> tuple[dict, list[str]]:
    finais = (validas.sort_values(["ano", "instituto", "fim_campo", "n", "ordem_fonte"],
                                  ascending=[True, True, False, False, True])
              .groupby(["ano", "instituto"], as_index=False).first())

    def margem_real(ano):
        o = oficiais[ano]
        return 100 * (o["votos_A"] - o["votos_B"]) / (o["votos_A"] + o["votos_B"])

    finais["margem_pesquisa"] = 100 * (finais["pct_A"] - finais["pct_B"]) / (finais["pct_A"] + finais["pct_B"])
    finais["margem_real"] = finais["ano"].map(margem_real)
    finais["erro"] = finais["margem_pesquisa"] - finais["margem_real"]
    p = finais["pct_A"] / (finais["pct_A"] + finais["pct_B"])
    finais["dp_amostral_margem"] = 200 * np.sqrt(p * (1 - p) / finais["n"])
    finais["erro_em_dp"] = finais["erro"] / finais["dp_amostral_margem"]
    finais = cruza_tse(finais)

    # critério do plano: 2026 dentro da distribuição histórica do mesmo instituto
    hist = finais[finais["ano"] < 2026]
    comb = hist["erro"].abs().to_numpy()
    crit = []
    for r in finais[finais["ano"] == 2026].itertuples():
        h = hist[hist["instituto"] == r.instituto]["erro"].abs()
        crit.append({"instituto": r.instituto, "erro_2026": r.erro, "n_hist": len(h),
                     "max_abs_erro_hist": h.max() if len(h) else np.nan,
                     "dentro_hist_instituto": (abs(r.erro) <= h.max()) if len(h) else np.nan,
                     "percentil_no_historico_combinado": stats.percentileofscore(comb, abs(r.erro))})
    crit = pd.DataFrame(crit)

    # correlação entre institutos
    por_ano = finais.groupby("ano")["erro"].agg(["count", "mean", "std", "min", "max"])
    grupos = [g["erro"].to_numpy() for _, g in finais.groupby("ano") if len(g) > 1]
    _, p_anova = stats.f_oneway(*grupos)
    media = finais["erro"].mean()
    eta2 = sum(len(g) * (g.mean() - media) ** 2 for g in grupos) / ((finais["erro"] - media) ** 2).sum()
    concord = []
    for _, g in finais.groupby("ano"):
        sinal = np.sign(g["erro"].to_numpy())
        pares = [(i, j) for i in range(len(sinal)) for j in range(i + 1, len(sinal))]
        if pares:
            concord.append(np.mean([sinal[i] == sinal[j] for i, j in pares]))

    finais.to_csv(OUTPUT / "tables" / f"t5_pesquisas_finais{sufixo}.csv", index=False)
    crit.to_csv(OUTPUT / "tables" / f"t5_criterio_2026{sufixo}.csv", index=False)
    por_ano.to_csv(OUTPUT / "tables" / f"t5_erro_por_eleicao{sufixo}.csv")

    dentro = crit["dentro_hist_instituto"].dropna()
    resumo = {
        "pesquisas finais (instituto × eleição)": len(finais),
        "pesquisas finais por eleição": finais.groupby("ano").size().to_dict(),
        "margem real 2026 (p.p., A − B sobre A+B)": round(margem_real(2026), 3),
        "institutos 2026 com histórico": int(len(dentro)),
        "dos quais com erro absoluto 2026 ≤ maior erro absoluto histórico do instituto": int(dentro.astype(bool).sum()),
        "institutos 2026 sem histórico": int(crit["dentro_hist_instituto"].isna().sum()),
        "erro médio 2026 (p.p.)": round(float(finais.loc[finais["ano"] == 2026, "erro"].mean()), 3),
        "variância dos erros explicada pela eleição (η²)": round(float(eta2), 3),
        "ANOVA erro ~ eleição: p": float(p_anova),
        "concordância média de sinal entre pares de institutos na mesma eleição": round(float(np.mean(concord)), 3),
    }
    corpo = ["| Métrica | Valor |", "|---|---|"]
    for k, v in resumo.items():
        corpo.append(f"| {k} | {v:.4g} |" if isinstance(v, float) else f"| {k} | {v} |")
    corpo += ["", "### Erro por eleição (p.p. na margem)", "", por_ano.round(2).to_markdown(), "",
              "### Critério do plano — 2026 por instituto", "", crit.round(2).to_markdown(index=False), "",
              "### Pesquisas finais", "",
              finais[["ano", "instituto", "fim_campo", "n", "pct_A", "pct_B", "margem_pesquisa", "margem_real",
                      "erro", "dp_amostral_margem", "erro_em_dp", "registro_tse", "protocolo_tse"]]
              .round(2).to_markdown(index=False)]
    return resumo, corpo


def main() -> None:
    todas, oficiais = [], {}
    for ano in ANOS:
        oficial, tokens = finalistas(ano)
        oficiais[ano] = oficial
        p = pesquisas_ano(ano, tokens, oficial)
        p["A"], p["B"] = oficial["A"], oficial["B"]
        todas.append(p)
    todas = pd.concat(todas, ignore_index=True)
    OUTPUT.joinpath("tables").mkdir(parents=True, exist_ok=True)
    todas.to_csv(OUTPUT / "tables" / "t5_pesquisas_2t.csv", index=False)

    validas = todas.dropna(subset=["fim_campo", "pct_A", "pct_B"])
    validas = validas[validas.apply(lambda r: r.fim_campo < DATA_2T[r.ano], axis=1)]
    validas = validas.reset_index().rename(columns={"index": "ordem_fonte"})
    # regra 2 como fixada em docs/desenho_T5_T6.md
    res_reg, corpo_reg = analisa(validas, oficiais, "")
    # correção registrada em DESVIOS.md (exploratória): só pesquisas com fim de campo após o 1º turno
    entre_turnos = validas[validas.apply(lambda r: r.fim_campo > DATA_1T[r.ano], axis=1)]
    res_cor, corpo_cor = analisa(entre_turnos, oficiais, "_entre_turnos_EXPLORATORIO")

    for rotulo, res in (("regra fixada", res_reg), ("entre turnos (exploratório)", res_cor)):
        print(f"== {rotulo}")
        for k, v in res.items():
            print(f"{k}: {v}")
    linhas = ["# T5 — resumo", "", f"Linhas de pesquisa de 2º turno extraídas da fonte: {len(todas)}.", "",
              "## A. Regra 2 como fixada em `docs/desenho_T5_T6.md`", "",
              "Inclui, para institutos sem pesquisa entre os turnos, pesquisas de confronto direto feitas antes "
              "do 1º turno.", ""] + corpo_reg + [
              "", "## B. Correção exploratória (DESVIOS.md): só pesquisas com fim de campo entre os turnos", ""] + \
        corpo_cor + ["",
                     "A = mais votado no 1º turno; erro = margem da pesquisa − margem real (positivo superestima A). "
                     "Fontes: resultados das pesquisas na Wikipedia em inglês com revisões fixadas (D9, fonte "
                     "secundária); registro do TSE (D5; não existe para 2010); resultados oficiais do TSE (D8; 2026 "
                     "em D2). Hashes em `data/raw/MANIFEST.csv`. Regras em `docs/desenho_T5_T6.md`. O desvio-padrão "
                     "amostral cobre só erro amostral sob amostragem aleatória simples; 2010 não tem n na fonte."]
    (OUTPUT / "tables" / "t5_resumo.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
