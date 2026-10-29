"""Plano v1.2 (EXPLORATÓRIO) — votos depositados após as 17h no 2º turno (docs/plano_v1_2_encerramento.md).

Uso:
    python src/15_encerramento_v12.py selecao   # D11 -> horários por seção, grupos G0/G1/G2, A3, seleção de logs
    python src/15_encerramento_v12.py analise   # D12 -> votos após 17h por seção, A1 e A2

Saídas: data/processed/v12_secoes.parquet, v12_selecao_logs.csv, v12_logs.parquet;
        output/tables/v12_*.csv e v12_encerramento_EXPLORATORIO.md
"""

import argparse
import io
import re
import zipfile

import numpy as np
import pandas as pd

from common import OUTPUT, PROCESSED, RAW, SEMENTE

CHAVE = ["uf", "mun", "zona", "secao"]
N_AMOSTRA_G0 = 600
LIMITE_SECOES = 12_000
MSG_VOTO = "O voto do eleitor foi computado"
TAB = OUTPUT / "tables"
COLS = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO", "CD_CARGO_PERGUNTA", "QT_APTOS", "QT_COMPARECIMENTO",
        "CD_TIPO_VOTAVEL", "NR_VOTAVEL", "QT_VOTOS", "DS_TIPO_URNA", "DS_SECOES_AGREGADAS", "DT_ABERTURA",
        "DT_ENCERRAMENTO"]


def le_bweb() -> pd.DataFrame:
    """Uma linha por seção (cargo Presidente): aptos, comparecimento, votos 13 e 22, horários locais."""
    partes = []
    for zp in sorted((RAW / "D11").glob("bweb_2t_*.zip")):
        with zipfile.ZipFile(zp) as z:
            nome = next(n for n in z.namelist() if n.endswith(".csv"))
            with z.open(nome) as f:
                df = pd.read_csv(io.TextIOWrapper(f, encoding="latin-1"), sep=";", usecols=COLS, dtype=str)
        df = df[df.CD_CARGO_PERGUNTA == "1"]
        df["QT_VOTOS"] = df.QT_VOTOS.astype(int)
        nom = df[df.CD_TIPO_VOTAVEL == "1"].pivot_table(index=["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"],
                                                         columns="NR_VOTAVEL", values="QT_VOTOS", aggfunc="sum")
        cab = df.drop_duplicates(["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]).set_index(
            ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"])[
            ["QT_APTOS", "QT_COMPARECIMENTO", "DS_TIPO_URNA", "DS_SECOES_AGREGADAS", "DT_ABERTURA", "DT_ENCERRAMENTO"]]
        cab["v13"] = nom.get("13", 0)
        cab["v22"] = nom.get("22", 0)
        partes.append(cab.reset_index())
        print(f"{zp.name}: {len(cab)} seções", flush=True)
    s = pd.concat(partes, ignore_index=True)
    s = s.rename(columns={"SG_UF": "uf", "CD_MUNICIPIO": "mun", "NR_ZONA": "zona", "NR_SECAO": "secao",
                          "QT_APTOS": "aptos", "QT_COMPARECIMENTO": "comparecimento", "DS_TIPO_URNA": "tipo_urna",
                          "DS_SECOES_AGREGADAS": "agregadas"})
    s["mun"] = s.mun.str.zfill(5)
    s["zona"] = s.zona.str.zfill(4)
    s["secao"] = s.secao.str.zfill(4)
    for c in ("aptos", "comparecimento"):
        s[c] = s[c].astype(int)
    s[["v13", "v22"]] = s[["v13", "v22"]].fillna(0).astype(int)
    s["abertura_local"] = pd.to_datetime(s.DT_ABERTURA, errors="coerce")
    s["encerramento_local"] = pd.to_datetime(s.DT_ENCERRAMENTO, errors="coerce")
    return s.drop(columns=["DT_ABERTURA", "DT_ENCERRAMENTO"])


def deslocamentos(s: pd.DataFrame) -> pd.Series:
    """Regra 1: round(mediana(abertura) − 08:00) em horas, por município."""
    oito = s.abertura_local.dt.normalize() + pd.Timedelta(hours=8)
    horas = (s.abertura_local - oito).dt.total_seconds() / 3600
    return horas.groupby([s.uf, s.mun]).transform("median").round()


def grupo(hora: pd.Series) -> pd.Series:
    """Regra 2: G0 até 17h15; G1 17h16–18h59; G2 19h00 ou depois (hora de Brasília)."""
    minutos = hora.dt.hour * 60 + hora.dt.minute
    return pd.Series(np.select([minutos <= 17 * 60 + 15, minutos < 19 * 60], ["G0", "G1"], "G2"),
                     index=hora.index).where(hora.notna())


def selecao() -> None:
    s = le_bweb()
    s["deslocamento_h"] = deslocamentos(s)
    s["encerramento_bsb"] = s.encerramento_local - pd.to_timedelta(s.deslocamento_h, unit="h")
    s["grupo"] = grupo(s.encerramento_bsb)
    s.to_parquet(PROCESSED / "v12_secoes.parquet", index=False)

    desl = s.groupby(["uf", "deslocamento_h"]).size().rename("secoes").reset_index()
    desl.to_csv(TAB / "v12_deslocamentos.csv", index=False)

    # A3: faixas do documento (sem a de 17h00 ou antes, que o documento não mostra) e os grupos do plano
    m = (s.encerramento_bsb.dt.hour * 60 + s.encerramento_bsb.dt.minute)
    faixa = np.select([m <= 17 * 60, m <= 17 * 60 + 15, m < 19 * 60], ["até 17h00", "17h01 a 17h15", "17h16 a 18h59"],
                      "19h00 ou depois")
    s["faixa"] = pd.Series(faixa, index=s.index).where(s.encerramento_bsb.notna(), "sem horário")
    a3 = s.groupby("faixa").agg(secoes=("secao", "size"), aptos=("aptos", "sum"),
                                comparecimento=("comparecimento", "sum"), v13=("v13", "sum"), v22=("v22", "sum"))
    a3["pct_13"] = (100 * a3.v13 / (a3.v13 + a3.v22)).round(2)
    a3["margem_13_menos_22"] = a3.v13 - a3.v22
    a3 = a3.reindex(["até 17h00", "17h01 a 17h15", "17h16 a 18h59", "19h00 ou depois", "sem horário"]).dropna(how="all")
    a3.to_csv(TAB / "v12_faixas_encerramento.csv")

    alvo = s[s.grupo.isin(["G1", "G2"])]
    g0 = s[s.grupo == "G0"].sample(N_AMOSTRA_G0, random_state=SEMENTE)
    sel = pd.concat([alvo, g0])[CHAVE + ["grupo"]]
    sel.to_csv(PROCESSED / "v12_selecao_logs.csv", index=False)
    print(a3.to_string())
    print(f"seleção: G1={int((sel.grupo == 'G1').sum())} G2={int((sel.grupo == 'G2').sum())} G0={len(g0)} "
          f"total={len(sel)}; estimativa ~ {len(sel) * 0.19 / 1000:.2f} GB")
    if len(sel) > LIMITE_SECOES:
        print(f"ATENÇÃO: acima de {LIMITE_SECOES} seções; pedir autorização antes de baixar (plano v1.2)")


def horas_de_voto(texto: str) -> list[str]:
    """Regra 4: horário (relógio da urna) de cada "O voto do eleitor foi computado" do dia do 2º turno."""
    return re.findall(rf"^25/10/2026 (\d\d:\d\d:\d\d)\t[^\t]*\t[^\t]*\t[^\t]*\t{MSG_VOTO}\t", texto, flags=re.M)


def le_logs(s: pd.DataFrame) -> pd.DataFrame:
    """Regras 4 e 5: votos computados no dia do 2º turno, no horário de Brasília, por seção."""
    sel = pd.read_csv(PROCESSED / "v12_selecao_logs.csv", dtype=str)
    desl = s.set_index(CHAVE)["deslocamento_h"]
    linhas = []
    for r in sel.itertuples():
        pasta = RAW / "D12" / r.uf.lower() / f"{r.mun}-{r.zona}-{r.secao}"
        logs = sorted(pasta.glob("*/*-log.jez"))
        reg = {"uf": r.uf, "mun": r.mun, "zona": r.zona, "secao": r.secao, "grupo": r.grupo, "logs": len(logs),
               "n_log": np.nan, "n_17h00": np.nan, "n_17h15": np.nan, "ultimo_voto_bsb": pd.NaT}
        if logs:
            horas = []
            for lg in logs:
                with zipfile.ZipFile(lg) as z:
                    texto = z.read(z.namelist()[0]).decode("latin-1")
                horas += horas_de_voto(texto)
            d = desl.get((r.uf, r.mun, r.zona, r.secao), 0.0)
            t = pd.to_timedelta(pd.Series(horas, dtype=str)) - pd.Timedelta(hours=d)
            reg.update(n_log=len(t), n_17h00=int((t >= pd.Timedelta(hours=17)).sum()),
                       n_17h15=int((t >= pd.Timedelta(hours=17, minutes=15)).sum()),
                       ultimo_voto_bsb=pd.Timestamp("2026-10-25") + t.max() if len(t) else pd.NaT)
        linhas.append(reg)
    return pd.DataFrame(linhas)


def residuo_bruto(df: pd.DataFrame, xcols: list[str]) -> np.ndarray:
    """Resíduo do modelo do T2 (efeito fixo de município), em pontos de participação do 13."""
    grupo = df.groupby(["uf", "mun"]).ngroup().to_numpy()
    n = np.bincount(grupo)

    def centra(v: np.ndarray) -> np.ndarray:
        return v - (np.bincount(grupo, weights=v) / n)[grupo]

    y = centra(df["y"].to_numpy(dtype=float))
    X = np.column_stack([centra(df[c].to_numpy(dtype=float)) for c in xcols])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return y - X @ beta


def analise() -> None:
    import statsmodels.formula.api as smf

    s = pd.read_parquet(PROCESSED / "v12_secoes.parquet")
    lg = le_logs(s)
    lg = lg.merge(s[CHAVE + ["comparecimento", "v13", "v22", "encerramento_bsb", "tipo_urna"]], on=CHAVE, how="left")
    lg["dif_pct"] = 100 * (lg.n_log - lg.comparecimento).abs() / lg.comparecimento
    lg["valido"] = (lg.logs > 0) & (lg.dif_pct <= 1)
    lg.to_parquet(PROCESSED / "v12_logs.parquet", index=False)
    margem = int(s.v13.sum() - s.v22.sum())

    # A1: pior caso
    resumo = {}
    for g in ("G1", "G2", "G0"):
        x = lg[lg.grupo == g]
        v = x[x.valido]
        resumo[g] = {"secoes_no_grupo": int((s.grupo == g).sum()), "secoes_com_log": int((x.logs > 0).sum()),
                     "secoes_validas": len(v), "comparecimento_validas": int(v.comparecimento.sum()),
                     "votos_17h00": int(v.n_17h00.sum()), "votos_17h15": int(v.n_17h15.sum()),
                     "votos_17h00_incluindo_invalidas": int(x.n_17h00.fillna(0).sum())}
    a1 = pd.DataFrame(resumo).T
    tardias = lg[lg.grupo.isin(["G1", "G2"])]
    V = int(tardias[tardias.valido].n_17h00.sum())
    V_todas = int(tardias.n_17h00.fillna(0).sum())
    # expansão de G0 a partir da amostra (média por seção × nº de seções), IC 95% por bootstrap
    g0 = lg[(lg.grupo == "G0") & lg.valido].n_17h00.to_numpy(dtype=float)
    n_g0 = int((s.grupo == "G0").sum())
    rng = np.random.default_rng(SEMENTE)
    boot = np.array([rng.choice(g0, len(g0)).mean() for _ in range(2000)]) * n_g0
    g0_est, g0_ic = g0.mean() * n_g0, np.percentile(boot, [2.5, 97.5])

    # seções de G1 + G2 sem log válido: pior caso conservador conta todo o comparecimento delas
    fora = tardias[~tardias.valido]
    comp_fora = int(fora.comparecimento.sum())
    q = lambda g: ((lambda h: h.dt.hour + h.dt.minute / 60)(lg[(lg.grupo == g) & lg.valido].ultimo_voto_bsb)  # noqa: E731
                   .quantile([0.5, 0.9]).tolist())
    hora = lambda x: f"{int(x)}h{round(60 * (x - int(x))):02d}"  # noqa: E731

    # descritivo: votos após 17h divididos como a própria seção
    t = tardias[tardias.valido]
    liq_secao = float((t.n_17h00 * (t.v13 - t.v22) / (t.v13 + t.v22).where(lambda z: z > 0)).sum())

    # A2: resíduo do T2 sem d_comparecimento e d_bn sobre a fração de votos após 17h
    base = pd.read_parquet(PROCESSED / "t23_secoes_2026.parquet")
    t1 = sorted(c for c in base.columns if c.startswith("t1_c"))
    perfil = ["p_fem", "p_id_16_24", "p_id_25_44", "p_id_45_59", "p_id_60_69", "p_esc_superior", "p_esc_medio"]
    xcols = t1 + ["abst_1t", "bn_1t"] + perfil
    df = base.dropna(subset=["y", *xcols]).reset_index(drop=True)
    df["e"] = residuo_bruto(df, xcols)
    r = lg[lg.valido].merge(df[CHAVE + ["e"]], on=CHAVE)
    r["f"] = r.n_17h00 / r.n_log
    fit = smf.ols("e ~ f", data=r).fit(cov_type="cluster", cov_kwds={"groups": r.groupby(["uf", "mun"]).ngroup()})
    b, ep = fit.params["f"], fit.bse["f"]
    efeito = 2 * V * np.array([b, b - 1.96 * ep, b + 1.96 * ep]) / 100

    a1.to_csv(TAB / "v12_a1_por_grupo.csv")
    lg[~lg.valido].to_csv(TAB / "v12_logs_excluidos.csv", index=False)
    a3 = pd.read_csv(TAB / "v12_faixas_encerramento.csv")
    desl = pd.read_csv(TAB / "v12_deslocamentos.csv")
    fmt = lambda v: f"{v:,.0f}".replace(",", ".")  # noqa: E731
    md = [
        "# Plano v1.2 — votos depositados após as 17h no 2º turno (EXPLORATÓRIO)", "",
        "Plano carimbado antes da coleta: `docs/plano_v1_2_encerramento.md` (+ `.ots`). Nada aqui altera a "
        "classificação confirmatória. Fontes: TSE, BU na Web (D11) e logs de urna (D12); hashes em "
        "`data/raw/MANIFEST.csv`.", "",
        f"Margem entre os finalistas nas seções do Brasil (BU na Web, exterior excluído): **{fmt(margem)} votos** "
        "(a margem oficial, com o exterior, é de 4.430.191).", "",
        "## A3 — seções por faixa de encerramento (hora de Brasília)", "",
        a3.to_markdown(index=False), "",
        "Deslocamento de fuso aplicado (regra 1): " + "; ".join(
            f"{r.uf} {int(r.deslocamento_h):+d} h ({fmt(r.secoes)})" for r in desl.itertuples() if r.deslocamento_h)
        + ". Demais UFs: 0.", "",
        "## A1 — votos registrados no log após as 17h", "",
        a1.to_markdown(), "",
        f"- Seções que fecharam depois das 17h15 (G1 + G2): **{fmt(V)} votos após as 17h00** nos logs válidos "
        f"({fmt(V_todas)} incluindo os logs com divergência de contagem).",
        f"- Pior caso (todos esses votos para um só candidato): {100 * V / margem:.2f}% da margem.",
        f"- {len(fora)} seções de G1 + G2 ficaram sem log válido (sem log na entrada \"Totalizado\" ou com contagem "
        f"divergente). Somando **todo** o comparecimento delas ({fmt(comp_fora)}) ao pior caso: "
        f"{fmt(V + comp_fora)} votos = {100 * (V + comp_fora) / margem:.1f}% da margem.",
        f"- Horário do último voto (mediana; percentil 90): G1 {hora(q('G1')[0])}; {hora(q('G1')[1])}. "
        f"G2 {hora(q('G2')[0])}; {hora(q('G2')[1])}. Nas seções encerradas depois das 19h, a urna ficou aberta, "
        f"mas a maioria não recebeu nenhum voto depois das 17h.",
        f"- Seções que fecharam até 17h15 (G0), expansão da amostra de {len(g0)}: {fmt(g0_est)} votos após as 17h00 "
        f"(IC 95% {fmt(g0_ic[0])} a {fmt(g0_ic[1])}). São votos de quem estava na fila, previstos na lei.",
        f"- Limite extremo (todos os votos após 17h00 do país, G0 estimado no limite superior): "
        f"{fmt(V_todas + g0_ic[1])} votos = {100 * (V_todas + g0_ic[1]) / margem:.1f}% da margem.",
        f"- Se os votos após 17h00 em G1 + G2 tivessem se dividido como o resto da própria seção, o saldo para o 13 "
        f"seria de {fmt(liq_secao)} votos.", "",
        "## A2 — direção (estimativa ecológica)", "",
        f"Resíduo do modelo do T2 (sem `d_comparecimento` e `d_bn`) sobre a fração de votos após 17h, em "
        f"{len(r)} seções com log válido; erro-padrão agrupado por município.", "",
        f"- Coeficiente: {b:.2f} pontos (IC 95% {b - 1.96 * ep:.2f} a {b + 1.96 * ep:.2f}); p = {fit.pvalues['f']:.3g}.",
        f"- Efeito líquido estimado sobre a margem: {fmt(efeito[0])} votos (IC 95% {fmt(efeito[1])} a "
        f"{fmt(efeito[2])}), isto é, {100 * efeito[0] / margem:.2f}% da margem.", "",
        "Logs não registram em quem cada eleitor votou; A2 é inferência agregada por seção e não descreve o voto de "
        "nenhum eleitor. A pergunta sobre a isonomia do procedimento é institucional e não é respondida aqui.",
    ]
    (TAB / "v12_encerramento_EXPLORATORIO.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("etapa", choices=["selecao", "analise"])
    a = p.parse_args()
    {"selecao": selecao, "analise": analise}[a.etapa]()
