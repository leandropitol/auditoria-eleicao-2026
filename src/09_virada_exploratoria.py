"""EXPLORATÓRIO (DESVIOS.md) — dimensão da virada entre turnos em 2026, sem improbabilidade post hoc.

1. Deslocamento da margem entre turnos (margens medidas entre os dois finalistas), contra a base do T6.
2. Decomposição agregada, por UF, da variação de votos dos finalistas entre turnos (fluxos compatíveis com os
   totais; nenhuma inferência sobre eleitores individuais).
3. Aritmética mínima da virada: parcela dos votos novos dos finalistas que o 2º colocado precisava obter, contra a
   observada, em 2026 e nos 2ºs turnos brasileiros anteriores.

Uso: python src/09_virada_exploratoria.py
Saídas: output/tables/virada_*_EXPLORATORIO.csv e virada_EXPLORATORIO.md
"""

import zipfile

import numpy as np
import pandas as pd
from scipy import stats

from common import OUTPUT, PROCESSED, RAW

NAO_NOMINAIS = {"95", "96", "97", "98"}
ANOS_BR = [1989, 2002, 2006, 2010, 2014, 2018, 2022, 2026]


def deslocamentos() -> pd.DataFrame:
    c = pd.read_csv(OUTPUT / "tables" / "t6_casos.csv")
    lider_2t = np.where(c["reversao"], c["pct_vencedor_2t"] + c["margem_2t_lider_menos_segundo_pp"],
                        c["pct_vencedor_2t"])
    segundo_2t = lider_2t - c["margem_2t_lider_menos_segundo_pp"]
    c["margem_1t_entre_finalistas"] = 100 * (c["pct_lider_1t"] - c["pct_segundo_1t"]) / (
        c["pct_lider_1t"] + c["pct_segundo_1t"])
    c["margem_2t_entre_finalistas"] = 100 * (lider_2t - segundo_2t) / (lider_2t + segundo_2t)
    c["deslocamento_pp"] = c["margem_2t_entre_finalistas"] - c["margem_1t_entre_finalistas"]
    return c[["pais", "ano", "margem_1t_entre_finalistas", "margem_2t_entre_finalistas", "deslocamento_pp",
              "reversao", "caso_2026_brasil"]]


def aritmetica_brasil() -> pd.DataFrame:
    linhas = []
    for ano in ANOS_BR:
        v = pd.read_parquet(PROCESSED / f"votos_presidente_{ano}.parquet")
        r1 = v[v["turno"] == 1].set_index("candidato")["votos"].sort_values(ascending=False)
        r2 = v[v["turno"] == 2].set_index("candidato")["votos"]
        lid, seg = r1.index[0], r1.index[1]
        L1, S1, L2, S2 = r1[lid], r1[seg], r2[lid], r2[seg]
        P = (L2 + S2) - (L1 + S1)  # votos novos dos dois finalistas entre os turnos
        linhas.append({"ano": ano, "lider_1t": lid, "segundo_1t": seg, "vantagem_1t_votos": int(L1 - S1),
                       "votos_dos_demais_1t": int(r1.drop([lid, seg]).sum()),
                       "votos_novos_dos_finalistas": int(P),
                       "parcela_necessaria_para_virar": 0.5 + (L1 - S1) / (2 * P),
                       "parcela_obtida_pelo_segundo": (S2 - S1) / P,
                       "virou": bool(S2 > L2)})
    return pd.DataFrame(linhas)


def decomposicao_uf_2026() -> pd.DataFrame:
    chave_uf = "SG_UF"
    nominal = []
    with zipfile.ZipFile(RAW / "D2" / "votacao_secao_2026_BR.zip") as z:
        nome = next(n for n in z.namelist() if n.lower().endswith(".csv"))
        for b in pd.read_csv(z.open(nome), sep=";", encoding="latin-1", dtype=str, chunksize=2_000_000,
                             usecols=["NR_TURNO", "CD_CARGO", chave_uf, "NR_VOTAVEL", "QT_VOTOS"]):
            b = b[(b["CD_CARGO"] == "1") & ~b["NR_VOTAVEL"].isin(NAO_NOMINAIS)]
            nominal.append(b.assign(QT_VOTOS=b["QT_VOTOS"].astype(int))
                           .groupby([chave_uf, "NR_TURNO", "NR_VOTAVEL"])["QT_VOTOS"].sum())
    nom = pd.concat(nominal).groupby(level=[0, 1, 2]).sum().unstack("NR_VOTAVEL", fill_value=0)
    det = []
    with zipfile.ZipFile(RAW / "D4" / "detalhe_votacao_secao_2026.zip") as z:
        for n in [n for n in z.namelist() if n.lower().endswith(".csv")]:
            d = pd.read_csv(z.open(n), sep=";", encoding="latin-1", dtype=str,
                            usecols=["NR_TURNO", "CD_CARGO", chave_uf, "NR_ZONA", "NR_SECAO", "CD_MUNICIPIO",
                                     "QT_APTOS", "QT_COMPARECIMENTO", "QT_VOTOS_BRANCOS", "QT_VOTOS_NULOS"])
            det.append(d[d["CD_CARGO"] == "1"])
    d = pd.concat(det).drop_duplicates(["NR_TURNO", chave_uf, "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"])
    for col in ("QT_APTOS", "QT_COMPARECIMENTO", "QT_VOTOS_BRANCOS", "QT_VOTOS_NULOS"):
        d[col] = d[col].astype(int)
    d["bn"] = d["QT_VOTOS_BRANCOS"] + d["QT_VOTOS_NULOS"]
    det = d.groupby([chave_uf, "NR_TURNO"])[["QT_APTOS", "QT_COMPARECIMENTO", "bn"]].sum()

    linhas = []
    for uf in sorted(nom.index.get_level_values(0).unique()):
        n1, n2 = nom.loc[(uf, "1")], nom.loc[(uf, "2")]
        d1, d2 = det.loc[(uf, "1")], det.loc[(uf, "2")]
        a1, b1, a2, b2 = n1["22"], n1["13"], n2["22"], n2["13"]
        demais = n1.drop(["22", "13"]).sum()
        variacao = (a2 + b2) - (a1 + b1)
        comp = d2["QT_COMPARECIMENTO"] - d1["QT_COMPARECIMENTO"]
        bn = d1["bn"] - d2["bn"]
        linhas.append({"uf": uf, "margem_1t_22_menos_13": int(a1 - b1), "margem_2t_22_menos_13": int(a2 - b2),
                       "variacao_margem_a_favor_do_13": int((a1 - b1) - (a2 - b2)),
                       "ganho_22": int(a2 - a1), "ganho_13": int(b2 - b1),
                       "votos_dos_demais_1t": int(demais), "variacao_comparecimento": int(comp),
                       "reducao_brancos_nulos": int(bn),
                       "residuo_contabil": int(variacao - (demais + comp + bn)),
                       "parcela_dos_votos_novos_obtida_pelo_13": (b2 - b1) / variacao if variacao else np.nan})
    df = pd.DataFrame(linhas)
    tot = df.drop(columns=["uf", "parcela_dos_votos_novos_obtida_pelo_13"]).sum()
    tot["uf"] = "BRASIL"
    tot["parcela_dos_votos_novos_obtida_pelo_13"] = tot["ganho_13"] / (tot["ganho_13"] + tot["ganho_22"])
    return pd.concat([df, tot.to_frame().T], ignore_index=True)


def main() -> None:
    OUTPUT.joinpath("tables").mkdir(parents=True, exist_ok=True)
    des = deslocamentos()
    des.to_csv(OUTPUT / "tables" / "virada_deslocamentos_EXPLORATORIO.csv", index=False)
    base = des[~des["caso_2026_brasil"]]
    d26 = float(des.loc[des["caso_2026_brasil"], "deslocamento_pp"].iloc[0])
    pct = stats.percentileofscore(base["deslocamento_pp"], d26, kind="weak")
    ari = aritmetica_brasil()
    ari.to_csv(OUTPUT / "tables" / "virada_aritmetica_brasil_EXPLORATORIO.csv", index=False)
    uf = decomposicao_uf_2026()
    uf.to_csv(OUTPUT / "tables" / "virada_decomposicao_uf_2026_EXPLORATORIO.csv", index=False)

    br_hist = base[base["pais"] == "Brasil"]["deslocamento_pp"]
    resumo = {
        "deslocamento da margem entre turnos, Brasil 2026 (p.p., margem entre finalistas)": round(d26, 2),
        "casos da base com deslocamento igual ou mais negativo": f"{int((base['deslocamento_pp'] <= d26).sum())} de {len(base)}",
        "percentil de 2026 na base (menor = maior perda do líder)": round(pct, 1),
        "deslocamentos brasileiros 1989–2022 (p.p.)": ", ".join(f"{a}: {x:+.1f}" for a, x in zip(
            base[base["pais"] == "Brasil"]["ano"], br_hist)),
        "2026: parcela dos votos novos dos finalistas necessária ao 13 para virar":
            round(float(ari.loc[ari["ano"] == 2026, "parcela_necessaria_para_virar"].iloc[0]), 4),
        "2026: parcela obtida pelo 13": round(float(ari.loc[ari["ano"] == 2026, "parcela_obtida_pelo_segundo"].iloc[0]), 4),
    }
    linhas = ["# Virada entre turnos — análise EXPLORATÓRIA", "",
              "Registrada em `DESVIOS.md`; não entra na classificação A/B/C. Não calcula a improbabilidade do resultado "
              "observado (Seção 6 do pré-registro): dimensiona a virada contra a experiência histórica.", "",
              "| Métrica | Valor |", "|---|---|"]
    linhas += [f"| {k} | {v} |" for k, v in resumo.items()]
    linhas += ["", "## 1. Deslocamento da margem (base do T6)", "",
               des.sort_values("deslocamento_pp").round(2).to_markdown(index=False), "",
               "## 3. Aritmética mínima da virada — Brasil", "",
               ari.round(4).to_markdown(index=False), "",
               "## 2. Decomposição por UF, 2026 (votos)", "",
               uf.round(4).to_markdown(index=False), "",
               "Leitura da decomposição: `ganho_22 + ganho_13 = votos_dos_demais_1t + variacao_comparecimento + "
               "reducao_brancos_nulos + residuo_contabil`. São fluxos compatíveis com os totais, não transferências "
               "individuais (falácia ecológica). Fontes: TSE (D2, D4, D8), Wikipedia com revisões fixadas (D10, "
               "via T6); hashes em `data/raw/MANIFEST.csv`."]
    (OUTPUT / "tables" / "virada_EXPLORATORIO.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    for k, v in resumo.items():
        print(f"{k}: {v}")
    print(ari.round(4).to_string())
    print(uf[uf["uf"] == "BRASIL"].T.to_string())


if __name__ == "__main__":
    main()
