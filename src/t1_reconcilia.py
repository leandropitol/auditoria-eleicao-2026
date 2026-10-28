"""T1 — reconciliação BU × totalização (D2) e classificação pelos critérios fixados (Seção 6 do desenho)."""

import json
import zipfile

import numpy as np
import pandas as pd
from scipy import stats

from common import OUTPUT, PROCESSED, RAW

D2_ZIP = RAW / "D2" / "votacao_secao_2026_BR.zip"
COLS = ["NR_TURNO", "CD_CARGO", "SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO", "NR_VOTAVEL", "QT_VOTOS"]
LIMIAR_LINHA2 = 0.0001  # 0,01% das urnas
ALFA = 0.05


def le_totalizacao(chaves: pd.DataFrame) -> pd.DataFrame:
    """Linhas do 2º turno, Presidente, apenas das seções da amostra."""
    with zipfile.ZipFile(D2_ZIP) as z:
        nomes = [n for n in z.namelist() if n.lower().endswith(".csv")]
        partes = []
        for nome in nomes:
            with z.open(nome) as f:
                for bloco in pd.read_csv(f, sep=";", encoding="latin-1", usecols=COLS, dtype=str,
                                         chunksize=2_000_000):
                    bloco = bloco[(bloco["NR_TURNO"] == "2") & (bloco["CD_CARGO"] == "1")]
                    partes.append(bloco)
    tot = pd.concat(partes, ignore_index=True)
    tot["mun"] = tot["CD_MUNICIPIO"].str.zfill(5)
    tot["zona"] = tot["NR_ZONA"].str.zfill(4)
    tot["secao"] = tot["NR_SECAO"].str.zfill(4)
    tot["uf"] = tot["SG_UF"]
    tot["QT_VOTOS"] = tot["QT_VOTOS"].astype(int)
    return tot.merge(chaves, on=["uf", "mun", "zona", "secao"], how="inner")


def clopper_pearson(k: int, n: int, conf: float = 0.95) -> tuple[float, float]:
    a = (1 - conf) / 2
    lo = 0.0 if k == 0 else stats.beta.ppf(a, k, n - k + 1)
    hi = 1.0 if k == n else stats.beta.ppf(1 - a, k + 1, n - k)
    return float(lo), float(hi)


def reconcilia_bus(bu_ok: pd.DataFrame, tot_w: pd.DataFrame) -> pd.DataFrame:
    """Compara os votos de cada BU verificado com a totalização da mesma seção."""
    linhas = []
    for r in bu_ok.itertuples():
        chave = (r.uf, r.mun, r.zona, r.secao)
        votos_bu = {k: int(v) for k, v in json.loads(r.votos).items()}
        if chave in tot_w.index:
            votos_tot = {k: int(v) for k, v in tot_w.loc[chave].items() if v != 0}
            presente = True
        else:
            votos_tot, presente = {}, False
        todos = sorted(set(votos_bu) | set(votos_tot))
        difs = {k: votos_bu.get(k, 0) - votos_tot.get(k, 0) for k in todos}
        soma_abs = sum(abs(d) for d in difs.values())
        total_bu = sum(votos_bu.values())
        linhas.append({
            "uf": r.uf, "mun": r.mun, "zona": r.zona, "secao": r.secao, "estrato": r.estrato,
            "peso": r.peso, "hash_tse": r.hash_tse, "presente_totalizacao": presente,
            "total_votos_bu": total_bu, "total_votos_totalizacao": sum(votos_tot.values()),
            "divergente": (not presente) or soma_abs > 0,
            "soma_abs_dif": soma_abs,
            "pct_dif_urna": (soma_abs / total_bu) if total_bu else np.nan,
            "difs": json.dumps({k: d for k, d in difs.items() if d}, sort_keys=True),
        })
    return pd.DataFrame(linhas)


def main() -> None:
    val = pd.read_parquet(PROCESSED / "t1_bu_validacao.parquet")
    amostra = pd.read_csv(PROCESSED / "t1_amostra.csv", dtype=str)
    verif = val[val["situacao"].isin(["bu_verificado", "erro_leitura"])].copy()

    val_rec = pd.read_parquet(PROCESSED / "t1_bu_validacao_recebidos.parquet")
    chaves = amostra[["uf", "mun", "zona", "secao"]]
    tot = le_totalizacao(chaves)
    tot_w = tot.pivot_table(index=["uf", "mun", "zona", "secao"], columns="NR_VOTAVEL",
                            values="QT_VOTOS", aggfunc="sum", fill_value=0)

    bu_ok = verif[verif["situacao"] == "bu_verificado"]
    rec = reconcilia_bus(bu_ok, tot_w)

    # candidatos do 2º turno: os dois números nominais com mais votos na totalização da amostra
    nominais = tot[~tot["NR_VOTAVEL"].isin(["95", "96"])].groupby("NR_VOTAVEL")["QT_VOTOS"].sum()
    cand = list(nominais.sort_values(ascending=False).index[:2])
    rec["dif_margem"] = rec["difs"].map(lambda s: json.loads(s).get(cand[0], 0) - json.loads(s).get(cand[1], 0))

    OUTPUT.joinpath("tables").mkdir(parents=True, exist_ok=True)
    rec.to_csv(OUTPUT / "tables" / "t1_reconciliacao_por_urna.csv", index=False)
    val.drop(columns=["votos"], errors="ignore").to_csv(OUTPUT / "tables" / "t1_validacao_por_urna.csv", index=False)

    # complemento exploratório (DESVIOS.md): não entra na classificação
    exp_ok = val_rec[val_rec["situacao"] == "bu_verificado"]
    rec_exp = reconcilia_bus(exp_ok, tot_w)
    rec_exp.to_csv(OUTPUT / "tables" / "t1_reconciliacao_recebidos_EXPLORATORIO.csv", index=False)

    # seções sorteadas com votos na totalização mas sem BU verificado (confirmatório nem exploratório)
    com_bu = set(map(tuple, pd.concat([bu_ok, exp_ok])[["uf", "mun", "zona", "secao"]].values))
    so_tot = sorted(set(tot_w.index) - com_bu)
    pd.DataFrame(so_tot, columns=["uf", "mun", "zona", "secao"]).merge(
        val[["uf", "mun", "zona", "secao", "situacao"]], how="left").to_csv(
        OUTPUT / "tables" / "t1_secoes_na_totalizacao_sem_bu_verificado.csv", index=False)

    # --- métricas -----------------------------------------------------------------------------
    n_amostra = len(amostra)
    n_verif = len(verif)
    falhas = verif[~verif["assinatura_valida"].fillna(False).astype(bool)]
    k_falha = len(falhas)
    w = verif["peso"].astype(float)
    taxa_falha_pond = float((w * (~verif["assinatura_valida"].fillna(False).astype(bool))).sum() / w.sum())
    div = rec[rec["divergente"]]
    k_div, n_rec = len(div), len(rec)
    wr = rec["peso"].astype(float)
    prop_div_pond = float((wr * rec["divergente"]).sum() / wr.sum())
    ic_falha = clopper_pearson(k_falha, n_verif)
    ic_div = clopper_pearson(k_div, n_rec)

    # --- classificação (ordem fixada: linha 1, linha 3, linha 2) ------------------------------
    p_direcao = p_espacial = None
    if k_falha == 0 and k_div == 0:
        classe = "Linha 1 — 100% das assinaturas válidas e divergência zero: H1 rejeitada no escopo amostrado."
    else:
        sinais = div.loc[div["dif_margem"] != 0, "dif_margem"]
        if len(sinais):
            p_direcao = float(stats.binomtest(int((sinais > 0).sum()), len(sinais), 0.5).pvalue)
        if k_div:
            tab = pd.crosstab(rec["uf"], rec["divergente"])
            if tab.shape[1] == 2 and tab.shape[0] > 1:
                # Fisher para UF divergente vs. demais, UF com mais urnas divergentes (menor p entre UFs)
                ps = []
                for uf in tab.index:
                    a = tab.loc[uf, True]
                    b = tab.loc[uf, False]
                    c = tab[True].sum() - a
                    d = tab[False].sum() - b
                    ps.append(stats.fisher_exact([[a, b], [c, d]], alternative="greater").pvalue)
                p_espacial = float(min(1.0, min(ps) * len(ps)))  # Bonferroni sobre UFs
        if (p_direcao is not None and p_direcao < ALFA) or (p_espacial is not None and p_espacial < ALFA):
            classe = "Linha 3 — divergências com direção consistente ou concentração espacial: achado material."
        elif k_div and ic_div[1] < LIMIAR_LINHA2:
            classe = "Linha 2 — divergências isoladas, compatíveis com erro operacional."
        elif k_div:
            classe = ("Divergências presentes sem direção/concentração significativa; a amostra não permite "
                      "enquadrar na linha 2 (limite superior do IC 95% ≥ 0,01%). Urnas listadas.")
        else:
            classe = "Fora da linha 1: há falha de assinatura com divergência zero. Ver lista de falhas."

    resumo = {
        "seções sorteadas": n_amostra,
        "seções com BU eletrônico totalizado verificado": n_verif,
        "seções agregadas (sem BU próprio)": int((val["situacao"].str.startswith("secao_agregada")).sum()),
        "seções sem BU eletrônico totalizado": int((val["situacao"].str.startswith("sem_bu")).sum()),
        "seções sem índice baixado": int((val["situacao"] == "aux_nao_baixado").sum()),
        "falhas de assinatura (amostra)": k_falha,
        "taxa de falha de assinatura (amostra)": k_falha / n_verif if n_verif else np.nan,
        "IC 95% Clopper-Pearson falha (inf)": ic_falha[0],
        "IC 95% Clopper-Pearson falha (sup)": ic_falha[1],
        "taxa de falha estimada (ponderada)": taxa_falha_pond,
        "urnas reconciliadas": n_rec,
        "urnas com divergência BU x totalização": k_div,
        "proporção divergente (amostra)": k_div / n_rec if n_rec else np.nan,
        "IC 95% Clopper-Pearson divergência (inf)": ic_div[0],
        "IC 95% Clopper-Pearson divergência (sup)": ic_div[1],
        "proporção divergente estimada (ponderada)": prop_div_pond,
        "votos totais nos BUs reconciliados": int(rec["total_votos_bu"].sum()),
        "soma das diferenças absolutas BU - totalização (votos)": int(rec["soma_abs_dif"].sum()),
        "p teste binomial de direção": p_direcao,
        "p teste de concentração por UF (Fisher, Bonferroni)": p_espacial,
        "candidatos (números) usados na margem": " x ".join(cand),
        "seções sorteadas com votos na totalização e sem BU verificado": len(so_tot),
        "classificação T1": classe,
        "[exploratório] BUs em estado Recebido verificados": len(exp_ok),
        "[exploratório] falhas de assinatura": int((~exp_ok["assinatura_valida"].astype(bool)).sum()),
        "[exploratório] urnas com divergência BU x totalização": int(rec_exp["divergente"].sum()),
        "[exploratório] soma das diferenças absolutas BU - totalização (votos)": int(rec_exp["soma_abs_dif"].sum()),
    }
    pd.Series(resumo).to_csv(OUTPUT / "tables" / "t1_resumo.csv", header=["valor"])
    linhas_md = ["# T1 — resumo", "", "| Métrica | Valor |", "|---|---|"]
    for k, v in resumo.items():
        if isinstance(v, float):
            v = f"{v:.6g}"
        linhas_md.append(f"| {k} | {v} |")
        print(f"{k}: {v}")
    linhas_md += ["", "Fonte: TSE — arquivos de urna do 2º turno 2026 (pleito 3221; D1, amostra estratificada "
                  "n=6.025, semente 20261025) e votação por seção 2026 (D2, `votacao_secao_2026_BR.zip`). "
                  "Hashes e URLs em `data/raw/MANIFEST.csv`. Estimativa amostral: proporções com IC 95% "
                  "Clopper-Pearson e estimativas ponderadas por N_h/n_h. Critérios em `docs/desenho_amostral_T1.md`."]
    (OUTPUT / "tables" / "t1_resumo.md").write_text("\n".join(linhas_md) + "\n", encoding="utf-8")
