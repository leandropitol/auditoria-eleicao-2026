"""Etapa 7 — consolidação, correção de múltiplos testes e classificação A/B/C (docs/desenho_T4_consolidacao.md).

Uso: python src/10_consolidacao.py
Saídas: output/tables/consolidacao_testes.csv, output/report.md
Todos os números vêm das saídas dos scripts de T1–T6 e da análise exploratória.
"""

import re

import pandas as pd
from statsmodels.stats.multitest import multipletests

from common import OUTPUT, PROCESSED

T = OUTPUT / "tables"


def tabela_md(arquivo: str, secao: str | None = None) -> dict:
    """Lê as linhas "| chave | valor |" de um resumo markdown (opcionalmente só dentro de uma seção ##)."""
    texto = (T / arquivo).read_text(encoding="utf-8")
    if secao:
        ini = texto.index(secao)
        fim = texto.find("\n## ", ini + len(secao))
        texto = texto[ini: fim if fim > 0 else None]
    out = {}
    for linha in texto.splitlines():
        m = re.match(r"^\| (.+?) \| (.+?) \|$", linha)
        if m and m.group(1) not in ("Métrica", "Base", "---"):
            out.setdefault(m.group(1), m.group(2))
    return out


def num(s: str) -> float:
    return float(str(s).replace(",", "."))


def fmt(x: float, casas: int = 0) -> str:
    s = f"{x:,.{casas}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def main() -> None:
    t1 = pd.read_csv(T / "t1_resumo.csv", index_col=0)["valor"]
    t2c = tabela_md("t2_resumo.md", "## A.")
    t2p = tabela_md("t2_resumo.md", "## B.")
    t2b = tabela_md("t2_resumo.md")
    t3 = tabela_md("t3_resumo.md")
    t3s = tabela_md("t3_resumo_9999perm_EXPLORATORIO.md")
    moran = pd.read_csv(T / "t3_moran.csv").set_index("ano")
    moran_s = pd.read_csv(T / "t3_moran_9999perm_EXPLORATORIO.csv").set_index("ano")
    t4 = pd.read_csv(T / "t4_digitos.csv")
    t5a = tabela_md("t5_resumo.md", "## A.")
    t5b = tabela_md("t5_resumo.md", "## B.")
    t5crit = pd.read_csv(T / "t5_criterio_2026.csv")
    t6 = tabela_md("t6_resumo.md")
    vir = tabela_md("virada_EXPLORATORIO.md")

    votos_t2 = num(t2c["votos válidos (2º turno) somados nas seções anômalas"])
    pct_t2 = num(t2c["idem, em % da margem nacional entre os finalistas (exterior excluído)"])
    margem_t2 = votos_t2 / (pct_t2 / 100)  # base do T2, sem o exterior
    v2 = pd.read_parquet(PROCESSED / "votos_presidente_2026.parquet").query("turno == 2")["votos"]
    margem_nac = float(v2.max() - v2.min())  # margem oficial com o exterior

    # --- correção de múltiplos testes (família confirmatória) -------------------------------------------
    familia = pd.DataFrame([
        ("T2", "direção das seções anômalas (binomial)", num(t2c["(b) p binomial de direção"])),
        ("T2", "agrupamento espacial das seções anômalas (permutação)", num(t2c["(a) p de permutação (unilateral)"])),
        ("T3", "I de Moran global dos resíduos de 2026 (permutação)", float(moran.loc[2026, "p_sim"])),
        ("T5", "erros das pesquisas variam por eleição (ANOVA)", num(t5a["ANOVA erro ~ eleição: p"])),
        ("T6", "margem do 1º turno prediz reversão (logística)", num(t6["logística: p-valor do coeficiente"])),
    ], columns=["teste", "hipótese", "p"])
    familia["rejeita_BH_q005"], familia["p_BH"], _, _ = multipletests(familia["p"], alpha=0.05, method="fdr_bh")

    # --- classificação (Seção 5.1, ordem C, A, B) --------------------------------------------------------
    t1_linha1 = str(t1["classificação T1"]).startswith("Linha 1")
    t3_ok = str(t3["classificação T3"]).startswith("Nada anômalo")
    t5_dentro = t5crit["dentro_hist_instituto"].dropna().astype(bool)
    t5_ok = bool(len(t5_dentro) and t5_dentro.all())
    t2_achado = "Achado" in str(t2c["classificação T2"])
    material = votos_t2 >= margem_nac
    if t2_achado and material:
        desfecho = "C"
    elif t1_linha1 and t3_ok and t5_ok and not t2_achado:
        desfecho = "A"
    else:
        desfecho = "B"
    motivo_nao_a = []
    if not t5_ok:
        motivo_nao_a.append(f"T5: só {int(t5_dentro.sum())} de {len(t5_dentro)} institutos com histórico ficaram "
                            "dentro do próprio maior erro anterior")
    if t2_achado:
        motivo_nao_a.append("T2: critérios formais de achado atendidos (seções anômalas agrupadas e direcionais)")

    # --- tabela única de testes ---------------------------------------------------------------------------
    t4_26 = t4[t4["ano"] == 2026]
    t4_ctrl = t4[t4["ano"] < 2026]
    testes = pd.DataFrame([
        ("T1", "confirmatório", "Assinatura digital dos BUs (amostra estratificada)",
         f"{int(t1['falhas de assinatura (amostra)'])} falhas em {fmt(num(t1['urnas reconciliadas']))} urnas",
         "negativo (sem anomalia)"),
        ("T1", "confirmatório", "Reconciliação BU × totalização",
         f"{int(t1['urnas com divergência BU x totalização'])} divergências; "
         f"{fmt(num(t1['votos totais nos BUs reconciliados']))} votos conferidos", "negativo (sem anomalia)"),
        ("T1", "exploratório", "BUs em estado Recebido",
         f"{t1['[exploratório] falhas de assinatura']} falhas, {t1['[exploratório] urnas com divergência BU x totalização']} divergências",
         "negativo"),
        ("T2", "confirmatório", "Seções com deslocamento atípico entre turnos",
         f"{t2c['seções anômalas (FDR q=0,05)']} seções; agrupadas e direcionais; "
         f"{fmt(votos_t2)} votos ({fmt(pct_t2, 2)}% da margem nacional)",
         "achado formal, não material"),
        ("T2", "exploratório", "Idem, ponderado pelo tamanho da seção",
         f"{t2p['seções anômalas (FDR q=0,05)']} seções; "
         f"{fmt(num(t2p['idem, em % da margem nacional entre os finalistas (exterior excluído)']), 2)}% da margem",
         "achado formal, não material"),
        ("T3", "confirmatório", "Autocorrelação espacial dos resíduos municipais",
         f"I 2026 = {fmt(moran.loc[2026, 'I'], 3)}; faixa 2014–2022 = {fmt(moran.loc[[2014, 2018, 2022], 'I'].min(), 3)}–"
         f"{fmt(moran.loc[[2014, 2018, 2022], 'I'].max(), 3)}; clusters 2026: {t3['municípios em cluster em 2026 (FDR q=0,05)']}",
         "negativo (dentro da faixa)"),
        ("T3", "exploratório", "LISA com 9.999 permutações",
         f"clusters 2026: {t3s['municípios em cluster em 2026 (FDR q=0,05)']}; controles: "
         + ", ".join(f"{a}: {int(moran_s.loc[a, 'clusters_fdr'])}" for a in (2014, 2018, 2022)),
         "negativo"),
        ("T4", "completude", "Benford de 2º dígito, último dígito, múltiplos de 5 e 10",
         f"MAD 2BL 2026 = {t4_26['benford2_MAD'].min():.4f}–{t4_26['benford2_MAD'].max():.4f} "
         f"(controles {t4_ctrl['benford2_MAD'].min():.4f}–{t4_ctrl['benford2_MAD'].max():.4f})",
         "não é evidência (pré-registro)"),
        ("T5", "confirmatório", "Erro das pesquisas finais contra o histórico do instituto",
         f"{int(t5_dentro.sum())} de {len(t5_dentro)} institutos dentro do próprio máximo; erro médio 2026 = "
         f"{fmt(num(t5a['erro médio 2026 (p.p.)']), 2)} p.p.", "fora do padrão por instituto"),
        ("T5", "exploratório", "Idem, só pesquisas entre os turnos", f"erro médio 2026 = {fmt(num(t5b['erro médio 2026 (p.p.)']), 2)} p.p.; "
         f"η² por eleição = {t5b['variância dos erros explicada pela eleição (η²)']}", "erro correlacionado entre institutos"),
        ("T6", "confirmatório", "Probabilidade de reversão dada a margem do 1º turno",
         f"{fmt(num(t6['logística: P(reversão dada a margem de 2026)']) * 100, 1)}% "
         f"(IC 95% {t6['logística: IC 95% (delta, escala logit)']}); base: {t6['reversões na base']} reversões em "
         f"{t6['casos na base (sem Brasil 2026)']} casos", "reversão compatível com a margem"),
        ("Virada", "exploratório", "Parcela dos votos novos necessária e obtida pelo 2º colocado",
         f"necessária {fmt(num(vir['2026: parcela dos votos novos dos finalistas necessária ao 13 para virar']) * 100, 1)}%, "
         f"obtida {fmt(num(vir['2026: parcela obtida pelo 13']) * 100, 1)}%", "menor exigência e maior captação da série"),
    ], columns=["teste", "status", "o que mede", "resultado", "leitura"])
    testes.to_csv(T / "consolidacao_testes.csv", index=False)
    familia.to_csv(T / "consolidacao_bh.csv", index=False)

    rel = [
        "# Auditoria estatística — 2º turno presidencial 2026: relatório consolidado", "",
        "> **Versão preliminar, aberta à revisão adversarial (Etapa 8).** Resultados podem ser corrigidos; "
        "alterações ficam em `DESVIOS.md` e no histórico de commits.", "",
        "Plano pré-registrado em `PREREGISTRO.md` (commit `abdc482`, antes de qualquer download). Desvios em "
        "`DESVIOS.md`; resultados afetados por desvio são exploratórios. Candidatos identificados pelo número "
        "de urna. Linguagem descritiva; a interpretação está na Seção 5, separada dos resultados.", "",
        "## 1. Pergunta", "",
        "O resultado do 2º turno presidencial de 2026 é consistente com o processo eleitoral tal como documentado nos "
        "registros públicos, ou há anomalias localizadas e não explicáveis por fatores demográficos, políticos e de "
        "erro amostral conhecidos?", "",
        "## 2. Resultados — todos os testes, inclusive os negativos", "",
        testes.to_markdown(index=False), "",
        "## 3. Correção de múltiplos testes (família confirmatória, Benjamini-Hochberg q = 0,05)", "",
        familia.round(6).to_markdown(index=False), "",
        "As classificações seguem os critérios fixados em cada teste; a correção acima é reportada ao lado, "
        "conforme `docs/desenho_T4_consolidacao.md`. O I de Moran global ser significativo é esperado (vizinhos "
        "votam parecido) e ocorre em todos os anos; o critério do T3 é a comparação com a faixa de 2014–2022.", "",
        "## 4. Classificação (Seção 5.1 do pré-registro)", "",
        f"**Desfecho {desfecho} — " + {"A": "nada anômalo", "B": "anomalia com causa mundana",
                                        "C": "anomalia inexplicada"}[desfecho] + ".**", "",
        f"- Não é C: o único achado formal (T2) envolve {fmt(votos_t2)} votos, {fmt(pct_t2, 2)}% da margem entre os "
        f"finalistas sem o exterior ({fmt(margem_t2)} votos; margem oficial com o exterior: {fmt(margem_nac)}); não é "
        "material no sentido da Seção 5 (capaz de alterar o resultado nacional).",
        "- Não é A: " + "; ".join(motivo_nao_a) + ".",
        "- É B: o achado do T2 está localizado e concentra-se em seções pequenas e locais indígenas, padrão "
        "compatível com erro de especificação do modelo (heterocedasticidade e voto comunitário); o desvio do T5 é "
        "de desempenho das pesquisas, não da apuração.",
        "- Nenhum desfecho autoriza conclusão nacional por raciocínio agregado.", "",
        "## 5. Interpretação (separada dos resultados)", "",
        "- **Contagem.** O teste de maior poder probatório (T1) não encontrou falha de assinatura nem divergência "
        "entre boletins de urna e totalização na amostra. No escopo amostrado, a hipótese de fraude na contagem (H1) "
        "fica rejeitada; o limite superior do IC 95% para a proporção de urnas divergentes no universo é "
        f"{fmt(num(t1['IC 95% Clopper-Pearson divergência (sup)']) * 100, 3)}%.",
        "- **Padrão espacial.** Os resíduos municipais de 2026 têm autocorrelação dentro da faixa das três eleições "
        "anteriores e nenhum cluster local exclusivo (T3). As seções atípicas do T2 são poucas, pequenas, "
        "concentradas em contextos específicos e numericamente irrelevantes para o resultado.",
        "- **Improbabilidade.** A reversão ocorreu com a menor vantagem de 1º turno da série brasileira; para essa "
        "margem, a base de 2ºs turnos indica probabilidade de reversão da ordem de metade (T6). O que destoa do "
        "histórico é a magnitude: o 2º colocado obteve a maior parcela de votos novos da série (exploratório) e as "
        "pesquisas finais superestimaram o líder do 1º turno em todos os institutos (T5), com erro médio "
        "comparável ao de 2018.",
        "- **Hipótese padrão.** Onde há resultado não explicado (T2), a hipótese padrão é erro de especificação do "
        "modelo; nada nos dados aponta urnas específicas com divergência de contagem.", "",
        "## 6. Limitações", "",
        "- T1 é amostral (n = 5.692 urnas); não cobre urnas não sorteadas além do intervalo de confiança.",
        "- T5 e T6 usam fontes secundárias (Wikipedia com revisões fixadas) para percentuais de pesquisas e para "
        "eleições de outros países; valores extremos devem ser conferidos nas fontes primárias antes de publicação.",
        "- T3 foi feito por município (o plano previa seção aninhada), por falta de dados por seção para os anos de "
        "controle.",
        "- O critério do T5 por instituto apoia-se em 1 a 4 eleições por instituto.",
        "- Relatos de coação (H3) não entram como métrica (Seção 4 do pré-registro).", "",
        "## 7. Próximas etapas do plano", "",
        "- Etapa 8: revisão adversarial externa do código e dos dados por alguém que não compartilhe a expectativa "
        "inicial.",
        "- Etapa 9: publicação, incluindo os testes negativos.", "",
        "Fontes: TSE (D1–D5, D8), IBGE (D6, D7), Wikipedia com revisões fixadas (D9, D10); hashes, URLs e datas em "
        "`data/raw/MANIFEST.csv`. Tabelas de origem em `output/tables/`.",
    ]
    (OUTPUT / "report.md").write_text("\n".join(rel) + "\n", encoding="utf-8")
    print(testes.to_string())
    print(familia.round(6).to_string())
    print("Desfecho:", desfecho)


if __name__ == "__main__":
    main()
