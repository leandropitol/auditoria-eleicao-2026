"""Dados e gráficos do relatório público (.docx). Todos os números vêm das saídas dos testes em output/tables.

Uso: python src/11_relatorio_publico.py   (depois: node src/relatorio/gerar_docx.js)
Saídas: output/relatorio/dados_relatorio.json, output/figures/rel_*.png
"""

import importlib.util
import json
import subprocess
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from common import OUTPUT, PROCESSED, REPO_ROOT  # noqa: E402

T = OUTPUT / "tables"
FIG = OUTPUT / "figures"
REPO_URL = "https://github.com/leandropitol/auditoria-eleicao-2026"

# paleta de referência (dataviz, modo claro): série 1 azul, série 2 laranja; texto e grade neutros
AZUL, LARANJA = "#2a78d6", "#eb6834"
TEXTO, TEXTO2, GRADE, SUPERFICIE = "#0b0b0b", "#52514e", "#e4e3df", "#ffffff"


def _consolidacao():
    spec = importlib.util.spec_from_file_location("cons", Path(__file__).with_name("10_consolidacao.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def br(x: float, casas: int = 0) -> str:
    s = f"{x:,.{casas}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def estilo(ax):
    ax.set_facecolor(SUPERFICIE)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color(GRADE)
    ax.tick_params(colors=TEXTO2, labelsize=9, length=0)
    ax.grid(axis="x", color=GRADE, linewidth=0.8)
    ax.set_axisbelow(True)


def grafico_t6() -> str:
    c = pd.read_csv(T / "t6_casos.csv")
    base = c[~c["caso_2026_brasil"]]
    caso = c[c["caso_2026_brasil"]].iloc[0]
    fig, ax = plt.subplots(figsize=(7.2, 2.9), dpi=200)
    estilo(ax)
    for y, (virou, cor, rot) in enumerate(((False, AZUL, "Líder do 1º turno venceu"),
                                          (True, LARANJA, "Houve virada"))):
        d = base[base["reversao"] == virou]
        ax.scatter(d["margem_1t_pp"], [y] * len(d), s=46, color=cor, edgecolor=SUPERFICIE, linewidth=1.5,
                   zorder=3, label=f"{rot} ({len(d)})")
    ax.scatter([caso["margem_1t_pp"]], [1], s=120, facecolor="none", edgecolor=TEXTO, linewidth=1.6, zorder=4)
    ax.annotate(f"Brasil 2026\n{br(caso['margem_1t_pp'], 1)} p.p.", (caso["margem_1t_pp"], 1), xytext=(14, 14),
                textcoords="offset points", fontsize=8.5, color=TEXTO,
                arrowprops=dict(arrowstyle="-", color=TEXTO2, lw=0.8))
    ax.set_yticks([0, 1], ["Líder venceu", "Virada"], fontsize=9, color=TEXTO)
    ax.set_ylim(-0.6, 1.8)
    ax.set_xlabel("Vantagem do 1º colocado sobre o 2º no 1º turno (pontos percentuais)", fontsize=9, color=TEXTO2)
    ax.legend(loc="upper right", fontsize=8, frameon=False, ncol=2, bbox_to_anchor=(1, 1.02))
    fig.tight_layout()
    caminho = FIG / "rel_t6_margem_reversao.png"
    fig.savefig(caminho, facecolor=SUPERFICIE)
    plt.close(fig)
    return caminho.relative_to(REPO_ROOT).as_posix()


def grafico_virada() -> str:
    a = pd.read_csv(T / "virada_aritmetica_brasil_EXPLORATORIO.csv")
    a = a[a["ano"] != 2006]  # em 2006 o 2º colocado perdeu votos entre os turnos (parcela negativa), fora da escala
    fig, ax = plt.subplots(figsize=(7.2, 3.3), dpi=200)
    estilo(ax)
    ys = list(range(len(a)))[::-1]
    for y, r in zip(ys, a.itertuples()):
        ax.plot([r.parcela_necessaria_para_virar * 100, r.parcela_obtida_pelo_segundo * 100], [y, y],
                color=GRADE, linewidth=3, zorder=1, solid_capstyle="round")
    ax.scatter(a["parcela_necessaria_para_virar"] * 100, ys, s=52, color=AZUL, edgecolor=SUPERFICIE,
               linewidth=1.5, zorder=3, label="Parcela necessária para virar")
    ax.scatter(a["parcela_obtida_pelo_segundo"] * 100, ys, s=52, color=LARANJA, edgecolor=SUPERFICIE,
               linewidth=1.5, zorder=3, label="Parcela obtida pelo 2º colocado")
    ax.set_yticks(ys, [str(x) for x in a["ano"]], fontsize=9, color=TEXTO)
    ax.set_xlabel("% dos votos novos dos dois finalistas entre o 1º e o 2º turno", fontsize=9, color=TEXTO2)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), fontsize=8, frameon=False, ncol=2)
    fig.tight_layout()
    caminho = FIG / "rel_virada_parcelas.png"
    fig.savefig(caminho, facecolor=SUPERFICIE)
    plt.close(fig)
    return caminho.relative_to(REPO_ROOT).as_posix()


def grafico_t5() -> str:
    f = pd.read_csv(T / "t5_pesquisas_finais_entre_turnos_EXPLORATORIO.csv")
    anos = sorted(f["ano"].unique())
    fig, ax = plt.subplots(figsize=(7.2, 3.0), dpi=200)
    estilo(ax)
    ax.axvline(0, color=TEXTO2, linewidth=1)
    for y, ano in zip(range(len(anos))[::-1], anos):
        d = f[f["ano"] == ano]
        cor = LARANJA if ano == 2026 else AZUL
        ax.scatter(d["erro"], [y] * len(d), s=40, color=cor, alpha=0.85, edgecolor=SUPERFICIE, linewidth=1.2,
                   zorder=3)
        ax.scatter([d["erro"].mean()], [y], marker="|", s=260, color=TEXTO, zorder=4)
    ax.set_yticks(range(len(anos))[::-1], [str(a) for a in anos], fontsize=9, color=TEXTO)
    ax.set_xlabel("Erro na margem (pesquisa − resultado), p.p. — positivo superestima o 1º colocado do 1º turno",
                  fontsize=8.5, color=TEXTO2)
    fig.tight_layout()
    caminho = FIG / "rel_t5_erros.png"
    fig.savefig(caminho, facecolor=SUPERFICIE)
    plt.close(fig)
    return caminho.relative_to(REPO_ROOT).as_posix()


def commits() -> list[dict]:
    log = subprocess.run(["git", "log", "--reverse", "--format=%h|%H|%cI|%s"], cwd=REPO_ROOT, capture_output=True,
                         text=True, encoding="utf-8", check=True).stdout.strip().splitlines()
    out = []
    for linha in log:
        h, H, data, msg = linha.split("|", 3)
        out.append({"hash": h, "url": f"{REPO_URL}/commit/{H}", "data": data[:16].replace("T", " "), "mensagem": msg})
    return out


def nomes_2026() -> dict:
    """Nome de urna dos finalistas como consta na votação por seção do TSE (D2)."""
    import zipfile
    from common import RAW
    with zipfile.ZipFile(RAW / "D2" / "votacao_secao_2026_BR.zip") as z:
        nome = next(n for n in z.namelist() if n.lower().endswith(".csv"))
        for b in pd.read_csv(z.open(nome), sep=";", encoding="latin-1", dtype=str, chunksize=500_000,
                             usecols=["NR_TURNO", "CD_CARGO", "NR_VOTAVEL", "NM_VOTAVEL"]):
            b = b[(b["NR_TURNO"] == "2") & (b["CD_CARGO"] == "1") & b["NR_VOTAVEL"].isin(["13", "22"])]
            nomes = b.drop_duplicates("NR_VOTAVEL").set_index("NR_VOTAVEL")["NM_VOTAVEL"].to_dict()
            if len(nomes) == 2:
                return nomes
    raise LookupError("finalistas não encontrados")


def indigenas() -> dict:
    """Proporção de seções em locais com nome indígena: entre as anômalas do T2 e no total de seções do modelo."""
    spec = importlib.util.spec_from_file_location("t2", Path(__file__).with_name("03_pair_sections.py"))
    t2 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(t2)
    padrao = r"ALDEIA|IND[IÍ]GENA|TUXAUA"
    nomes = t2.nomes_locais()
    base = pd.read_parquet(PROCESSED / "t23_secoes_2026.parquet")[["uf", "mun", "zona", "secao"]]
    todas = base.merge(nomes, on=["uf", "mun", "zona", "secao"], how="left")["nm_local"]
    an = pd.read_csv(T / "t2_secoes_anomalas.csv", dtype=str)["nm_local"]
    p_todas = todas.str.contains(padrao, case=False, regex=True, na=False).mean()
    p_an = an.str.contains(padrao, case=False, regex=True, na=False).mean()
    return {"pct_anomalas": br(100 * p_an, 1), "pct_todas": br(100 * p_todas, 2), "razao": br(p_an / p_todas, 0)}


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    cons = _consolidacao()
    t1 = pd.read_csv(T / "t1_resumo.csv", index_col=0)["valor"]
    t2c = cons.tabela_md("t2_resumo.md", "## A.")
    t2p = cons.tabela_md("t2_resumo.md", "## B.")
    t3s = cons.tabela_md("t3_resumo_9999perm_EXPLORATORIO.md")
    moran = pd.read_csv(T / "t3_moran.csv").set_index("ano")
    moran_s = pd.read_csv(T / "t3_moran_9999perm_EXPLORATORIO.csv").set_index("ano")
    t4 = pd.read_csv(T / "t4_digitos.csv")
    t5a = cons.tabela_md("t5_resumo.md", "## A.")
    t5crit = pd.read_csv(T / "t5_criterio_2026.csv")
    t5e = pd.read_csv(T / "t5_erro_por_eleicao_entre_turnos_EXPLORATORIO.csv").set_index("ano")
    f26 = pd.read_csv(T / "t5_pesquisas_finais.csv").query("ano == 2026")
    t6 = cons.tabela_md("t6_resumo.md")
    casos = pd.read_csv(T / "t6_casos.csv")
    ari = pd.read_csv(T / "virada_aritmetica_brasil_EXPLORATORIO.csv").set_index("ano")
    uf = pd.read_csv(T / "virada_decomposicao_uf_2026_EXPLORATORIO.csv").set_index("uf")
    des = pd.read_csv(T / "virada_deslocamentos_EXPLORATORIO.csv")
    coleta = pd.read_csv(T / "coleta_resumo_por_fonte.csv")
    manifesto = pd.read_csv(REPO_ROOT / "data" / "raw" / "MANIFEST.csv", dtype=str)
    v26 = pd.read_parquet(PROCESSED / "votos_presidente_2026.parquet")
    v2 = v26[v26["turno"] == 2].set_index("candidato")["votos"]
    v1 = v26[v26["turno"] == 1].set_index("candidato")["votos"]
    t5d = t5crit["dentro_hist_instituto"].dropna().astype(bool)
    br26 = casos[casos["caso_2026_brasil"]].iloc[0]
    base = casos[~casos["caso_2026_brasil"]]
    bra = base[base["pais"] == "Brasil"]
    d26 = des[des["caso_2026_brasil"]].iloc[0]
    db = des[~des["caso_2026_brasil"]]
    total = uf.loc["BRASIL"]
    spec = manifesto[manifesto["id_fonte"] == "D1_SPEC"].iloc[0]

    dados = {
        "repo": REPO_URL,
        "data_relatorio": "28 de outubro de 2026",
        "commit_preregistro": next(c for c in commits() if c["hash"].startswith("abdc482")),
        "commits": commits(),
        "coleta": [{"fonte": r.fonte, "arquivos": br(r.arquivos), "gb": br(r.GB, 3), "acesso": r.primeiro_acesso_utc[:10]}
                   for r in coleta.assign(o=coleta["fonte"].str[1:].astype(int)).sort_values("o").itertuples()],
        "n_arquivos_manifesto": br(len(manifesto)),
        "spec_sha": spec["sha256"],
        "votos_2t": {"13": br(v2["13"]), "22": br(v2["22"]), "margem": br(v2["13"] - v2["22"]),
                     "pct13": br(100 * v2["13"] / (v2["13"] + v2["22"]), 2),
                     "pct22": br(100 * v2["22"] / (v2["13"] + v2["22"]), 2)},
        "votos_1t": {"13": br(v1["13"]), "22": br(v1["22"]),
                     "pct13": br(float(br26["pct_segundo_1t"]), 2), "pct22": br(float(br26["pct_lider_1t"]), 2),
                     "margem_pp": br(float(br26["margem_1t_pp"]), 1)},
        "t1": {"universo": br(int(pd.read_csv(T / "t1_estratos.csv")["N_h"].sum())), "sorteadas": br(int(t1["seções sorteadas"])),
               "verificadas": br(int(t1["seções com BU eletrônico totalizado verificado"])),
               "agregadas": br(int(t1["seções agregadas (sem BU próprio)"])),
               "sem_bu": br(int(t1["seções sem BU eletrônico totalizado"])),
               "falhas": int(t1["falhas de assinatura (amostra)"]),
               "divergencias": int(t1["urnas com divergência BU x totalização"]),
               "votos": br(int(t1["votos totais nos BUs reconciliados"])),
               "ic_sup": br(float(t1["IC 95% Clopper-Pearson divergência (sup)"]) * 100, 3),
               "recebidos": t1["[exploratório] BUs em estado Recebido verificados"]},
        "t2": {"secoes": br(int(cons.tabela_md("t2_resumo.md")["seções pareadas e completas (modelo)"])),
               "anomalas": t2c["seções anômalas (FDR q=0,05)"],
               "pos": t2c["anômalas com resíduo positivo (acima do previsto para o 13)"],
               "neg": t2c["anômalas com resíduo negativo"],
               "pequenas": t2c[next(k for k in t2c if k.startswith("anômalas no quintil inferior"))],
               "indigenas": t2c["anômalas em locais com nome indígena (aldeia, escola indígena)"],
               "votos": br(cons.num(t2c["votos válidos (2º turno) somados nas seções anômalas"])),
               "pct_margem": br(cons.num(t2c["idem, em % da margem nacional entre os finalistas (exterior excluído)"]), 2),
               "pond_anomalas": t2p["seções anômalas (FDR q=0,05)"],
               "pond_votos": br(cons.num(t2p["votos válidos (2º turno) somados nas seções anômalas"])),
               "pond_pct": br(cons.num(t2p["idem, em % da margem nacional entre os finalistas (exterior excluído)"]), 2)},
        "t3": {"I": {str(a): br(float(moran.loc[a, "I"]), 3) for a in moran.index},
               "clusters_999": {str(a): int(moran.loc[a, "clusters_fdr"]) for a in moran.index},
               "clusters_9999": {str(a): int(moran_s.loc[a, "clusters_fdr"]) for a in moran_s.index},
               "cl26_9999": t3s["municípios em cluster em 2026 (FDR q=0,05)"]},
        "t4": {"mad26": f"{br(t4[t4.ano == 2026].benford2_MAD.min(), 4)} a {br(t4[t4.ano == 2026].benford2_MAD.max(), 4)}",
               "madctrl": f"{br(t4[t4.ano < 2026].benford2_MAD.min(), 4)} a {br(t4[t4.ano < 2026].benford2_MAD.max(), 4)}"},
        "t5": {"n26": len(f26), "erro_min": br(f26["erro"].min(), 1), "erro_max": br(f26["erro"].max(), 1),
               "erro_medio": br(cons.num(t5a["erro médio 2026 (p.p.)"]), 1),
               "todos_mesmo_sinal": bool((f26["erro"] > 0).all()),
               "dentro": int(t5d.sum()), "com_hist": len(t5d),
               "media_por_ano": {str(a): br(float(t5e.loc[a, "mean"]), 1) for a in t5e.index}},
        "t6": {"casos": t6["casos na base (sem Brasil 2026)"], "reversoes": t6["reversões na base"],
               "p": br(cons.num(t6["logística: P(reversão dada a margem de 2026)"]) * 100, 0),
               "ic": " a ".join(br(float(x) * 100, 0) for x in t6["logística: IC 95% (delta, escala logit)"].strip("()").split(",")),
               "viz": t6["10 casos de margem mais próxima: reversões"],
               "br_min": br(float(bra["margem_1t_pp"].min()), 1), "br_max": br(float(bra["margem_1t_pp"].max()), 1),
               "laplace": br(cons.num(t6["Brasil: regra de sucessão de Laplace"]) * 100, 0)},
        "virada": {"necessaria": br(ari.loc[2026, "parcela_necessaria_para_virar"] * 100, 1),
                   "obtida": br(ari.loc[2026, "parcela_obtida_pelo_segundo"] * 100, 1),
                   "obtida_2022": br(ari.loc[2022, "parcela_obtida_pelo_segundo"] * 100, 1),
                   "obtida_2018": br(ari.loc[2018, "parcela_obtida_pelo_segundo"] * 100, 1),
                   "nec_min_hist": br(ari.drop(2026)["parcela_necessaria_para_virar"].min() * 100, 0),
                   "nec_max_hist": br(ari.drop(2026)["parcela_necessaria_para_virar"].max() * 100, 0),
                   "novos": br(total["ganho_13"] + total["ganho_22"]),
                   "novos_mi": br((total["ganho_13"] + total["ganho_22"]) / 1e6, 1),
                   "demais_mi": br(total["votos_dos_demais_1t"] / 1e6, 1),
                   "comp_mi": br(total["variacao_comparecimento"] / 1e6, 1),
                   "bn_mi": br(total["reducao_brancos_nulos"] / 1e6, 1),
                   "ganho13_mi": br(total["ganho_13"] / 1e6, 1), "ganho22_mi": br(total["ganho_22"] / 1e6, 1),
                   "desloc": br(float(d26["deslocamento_pp"]), 1).replace("-", "−"),
                   "desloc_maiores": int((db["deslocamento_pp"] <= d26["deslocamento_pp"]).sum()),
                   "desloc_total": len(db)},
        "figuras": {"t6": grafico_t6(), "virada": grafico_virada(), "t5": grafico_t5()},
        "nomes": nomes_2026(),
        "indigena": indigenas(),
        "pesquisas_22_frente": int((f26["margem_pesquisa"] > 0).sum()),
        "pesquisas_13_frente": int((f26["margem_pesquisa"] < 0).sum()),
        "n_desvios": sum(1 for l in (REPO_ROOT / "DESVIOS.md").read_text(encoding="utf-8").splitlines()
                         if l.startswith("| 2026-")),
        "sha_preregistro": __import__("common").sha256_file(REPO_ROOT / "PREREGISTRO.md"),
    }
    (OUTPUT / "relatorio").mkdir(parents=True, exist_ok=True)
    (OUTPUT / "relatorio" / "dados_relatorio.json").write_text(json.dumps(dados, ensure_ascii=False, indent=1),
                                                               encoding="utf-8")
    print(json.dumps({k: v for k, v in dados.items() if k not in ("commits", "coleta")}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
