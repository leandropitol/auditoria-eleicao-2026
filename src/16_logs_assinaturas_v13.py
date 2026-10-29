"""v1.3 (EXPLORATÓRIO) — checagem descritiva dos logs de urna baixados no plano v1.2 (D12).

Feita depois de ver os logs, para responder a perguntas públicas sobre arquivos de assinatura e mensagens de erro do
2º turno. Sem plano prévio: tudo aqui é descritivo e exploratório.

v1.3.1: os erros de assinatura passam a ser procurados em todos os formatos de mensagem (não só "Verificação de
assinatura ... [ERRO]"), agrupados por inicialização da urna, com o desfecho de cada uma; tabela das quatro mensagens
de um desafio público; limites amostrais explícitos.

Uso: python src/16_logs_assinaturas_v13.py
Saídas: output/tables/v13_logs_EXPLORATORIO.md, v13_falhas_assinatura.csv, v13_mensagens_desafio.csv,
        v13_msg_mr_por_dia.csv, v13_arquivos_assinatura.csv
"""

import re
from collections import Counter, defaultdict

import pandas as pd

from common import OUTPUT, PROCESSED, RAW, textos_log_urna

TAB = OUTPUT / "tables"
MSG_MR = "Problema ao desmontar a MR"
RE_VERIF = re.compile(r"Verifica\S* de assinatura.*\[(SUCESSO|ERRO|[A-Z]+)\]\s*$")
RE_ARQ = re.compile(r"\[(?:Pacote: )?(/[^\]]+\.vs[a-z])\]")
RE_ASSIN = re.compile(r"assinatura", re.I)
INICIO_LOGD = "Início das operações do logd"
DESAFIO = {"Problema ao desmontar a MR": re.compile(re.escape(MSG_MR)),
           "GAP erro 73": re.compile(r"GAP erro 73\b"),
           "turno2.jez": re.compile(r"turno2\.jez"),
           "turno2.vsc": re.compile(r"turno2\.vsc"),
           "Verificação de assinatura": re.compile(r"Verifica\S* de assinatura")}
DIAS = {"2026-10-04": "1º turno (04/10)", "2026-10-25": "2º turno (25/10)"}


def data_iso(d: str) -> str:
    return f"{d[6:10]}-{d[3:5]}-{d[:2]}"


def erro_de_assinatura(p: list[str]) -> bool:
    """Verificação com resultado diferente de SUCESSO, ou linha de nível ERRO que cita assinatura."""
    m = RE_VERIF.search(p[4])
    return bool(m and m.group(1) != "SUCESSO") or (p[1] == "ERRO" and bool(RE_ASSIN.search(p[4])))


def inicializacoes(linhas: list[list[str]]) -> list[list[list[str]]]:
    """Divide o log em inicializações da urna (cada "Início das operações do logd" abre uma)."""
    blocos, atual = [], []
    for p in linhas:
        if p[4].startswith(INICIO_LOGD) and atual:
            blocos.append(atual)
            atual = []
        atual.append(p)
    return blocos + ([atual] if atual else [])


def desfecho(bloco: list[list[str]], i: int) -> str:
    """Depois do primeiro erro da inicialização: o aplicativo de votação chegou a iniciar?"""
    for p in bloco[i + 1:]:
        if p[3] == "VOTA" and p[4].startswith("Iniciando aplica"):
            return "aplicativo de votação iniciado"
    return "aplicativo de votação não iniciado"


def cp_limites(k: int, n: int) -> tuple[float, float]:
    from scipy.stats import beta

    lo = beta.ppf(0.025, k, n - k + 1) if k > 0 else 0.0
    hi = beta.ppf(0.975, k + 1, n - k) if k < n else 1.0
    return lo, hi


def main() -> None:
    sel = pd.read_csv(PROCESSED / "v12_selecao_logs.csv", dtype=str).set_index(["uf", "mun", "zona", "secao"])
    verif = Counter()
    falhas, por_secao = [], []
    mr_dia = defaultdict(set)
    arquivos = Counter()
    for lg in sorted((RAW / "D12").rglob("*-log.jez")):
        pasta = lg.parent.parent
        uf = pasta.parent.name.upper()
        mun, zona, secao = pasta.name.split("-")
        chave = (uf, mun, zona, secao)
        reg = {"uf": uf, "mun": mun, "zona": zona, "secao": secao, "grupo": sel.loc[chave, "grupo"], "dias": set()}
        reg.update({(d, msg): False for msg in DESAFIO for d in (*DIAS, "qualquer")})
        for texto in textos_log_urna(lg):
            linhas = [p for p in (ln.split("\t") for ln in texto.splitlines()) if len(p) >= 5]
            for bloco in inicializacoes(linhas):
                primeiro = None
                for i, p in enumerate(bloco):
                    dia = data_iso(p[0][:10])
                    reg["dias"].add(dia)
                    m = RE_VERIF.search(p[4])
                    if m:
                        verif[(dia == "2026-10-25", m.group(1) == "SUCESSO")] += 1
                        a = RE_ARQ.search(p[4])
                        nome = re.sub(r"\d", "N", a.group(1)) if a else "?"
                        arquivos[(nome.rsplit(".", 1)[1], nome)] += 1
                    for msg, rx in DESAFIO.items():
                        if rx.search(p[4]):
                            reg[("qualquer", msg)] = True
                            if dia in DIAS:
                                reg[(dia, msg)] = True
                    if MSG_MR in p[4]:
                        mr_dia[dia].add(chave)
                    if erro_de_assinatura(p):
                        if primeiro is None:
                            primeiro = (i, p, [])
                        primeiro[2].append(p[4])
                if primeiro:
                    i, p, msgs = primeiro
                    falhas.append({"uf": uf, "mun": mun, "zona": zona, "secao": secao, "grupo": reg["grupo"],
                                   "urna": p[2], "data_hora_urna": p[0], "desfecho": desfecho(bloco, i),
                                   "mensagens": " || ".join(dict.fromkeys(m[:160] for m in msgs))})
        por_secao.append(reg)
    s = pd.DataFrame(por_secao)
    f = pd.DataFrame(falhas)
    f.to_csv(TAB / "v13_falhas_assinatura.csv", index=False)
    mr = pd.DataFrame([{"data": d, "urnas_com_mensagem": len(v)} for d, v in sorted(mr_dia.items())])
    mr.to_csv(TAB / "v13_msg_mr_por_dia.csv", index=False)
    arq = pd.DataFrame([{"extensao": e, "arquivo": n, "verificacoes": c} for (e, n), c in arquivos.items()])
    arq.sort_values(["extensao", "arquivo"]).to_csv(TAB / "v13_arquivos_assinatura.csv", index=False)

    g0 = s[s.grupo == "G0"]
    linhas_desafio = []
    for msg in DESAFIO:
        linha = {"mensagem": msg}
        for rotulo, df in (("todas", s), ("sorteadas", g0)):
            for d, nome in DIAS.items():
                linha[f"{rotulo}: {nome}"] = int(df[(d, msg)].sum())
            linha[f"{rotulo}: qualquer data"] = int(df[("qualquer", msg)].sum())
        linhas_desafio.append(linha)
    desafio = pd.DataFrame(linhas_desafio)
    desafio.to_csv(TAB / "v13_mensagens_desafio.csv", index=False)

    fmt = lambda v: f"{v:,.0f}".replace(",", ".")  # noqa: E731
    pct = lambda v: f"{100 * v:.2f}".replace(".", ",")  # noqa: E731
    n_g0 = len(g0)
    k_mr = int(g0[("2026-10-25", MSG_MR)].sum())
    lo_mr, _ = cp_limites(k_mr, n_g0)
    _, hi_zero = cp_limites(0, n_g0)
    secoes_brasil = len(pd.read_parquet(PROCESSED / "v12_secoes.parquet"))
    turno = [n for _, n in arquivos if "turno" in n.lower()]
    no_dia = f[f.data_hora_urna.str.startswith("25/10/2026")] if len(f) else f
    seguiu = f[f.desfecho == "aplicativo de votação iniciado"] if len(f) else f
    md = [
        "# v1.3.1 — checagem dos logs de urna (EXPLORATÓRIO)", "",
        "Checagem descritiva feita **depois** de abrir os logs baixados no plano v1.2 (D12), para responder a "
        "perguntas públicas. Não houve plano prévio; nada aqui altera a classificação confirmatória. Fonte: TSE, logs "
        "de urna (D12); hashes em `data/raw/MANIFEST.csv`.", "",
        "## Alcance: amostra, não o país", "",
        f"São {fmt(len(s))} logs de seções do 2º turno, de um total de {fmt(secoes_brasil)} seções no Brasil:",
        f"- {fmt(len(s) - n_g0)} seções encerradas depois das 17h15 (quase todas as desse grupo). **Não é amostra "
        "aleatória**: concentra-se em RJ, SP, BA, PE e PB;",
        f"- {fmt(n_g0)} seções sorteadas entre as que encerraram no horário normal (G0). Só esta parte representa o "
        "conjunto das urnas.", "",
        f"Com {fmt(n_g0)} urnas sorteadas, uma mensagem ausente de todas elas ocorre, com 95% de confiança, em menos de "
        f"{pct(hi_zero)}% das urnas (até cerca de {fmt(hi_zero * secoes_brasil)} seções); eventos raros só podem ser "
        "contados no país com todos os logs.", "",
        "## Quatro mensagens de um desafio público", "",
        "Número de urnas cujo log contém a mensagem, por data do evento:", "",
        desafio.to_markdown(index=False), "",
        f"- \"{MSG_MR}\": {k_mr} de {n_g0} urnas sorteadas no 2º turno; com 95% de confiança, ocorre em pelo menos "
        f"{pct(lo_mr)}% das urnas do país nesse turno. Aparece na inicialização, logo depois de a urna reconhecer a "
        "\"mídia de resultado de 2º turno\", e a urna segue para o aplicativo de votação. A causa não está "
        "documentada no material consultado.",
        f"- Arquivos de assinatura distintos citados nas verificações (dígitos trocados por N): {len(arquivos)} "
        f"({sum(1 for e, _ in arquivos if e == 'vst')} `.vst`, {sum(1 for e, _ in arquivos if e == 'vsc')} `.vsc`, "
        f"{sum(1 for e, _ in arquivos if e == 'vsu')} `.vsu`); com \"turno\" no nome: {len(turno)}. `turno2.jez` e "
        "`turno2.vsc` aparecem só dentro da mensagem \"GAP erro 73\", na mídia de resultado (`/dsk/mr/`).", "",
        "## Erros de assinatura, em todos os formatos de mensagem", "",
        f"Verificações no formato \"Verificação de assinatura … [resultado]\": {fmt(sum(verif.values()))}, das quais "
        f"{fmt(verif[(True, False)] + verif[(False, False)])} sem \"SUCESSO\". Somando as linhas de nível ERRO que "
        f"citam assinatura e agrupando por inicialização da urna: **{len(f)} inicializações com erro de assinatura**, "
        f"{len(no_dia)} delas no dia do 2º turno. Em {len(f) - len(seguiu)}, o aplicativo de votação não foi "
        f"iniciado; em {len(seguiu)}, foi iniciado depois do erro.", "",
        (f[["uf", "mun", "zona", "secao", "grupo", "data_hora_urna", "desfecho", "mensagens"]].to_markdown(index=False)
         if len(f) else "nenhuma"), "",
        "O caso em que o aplicativo foi iniciado depois de um erro de assinatura não tem explicação no material "
        "consultado; o que o arquivo citado cobre e por que o erro não bloqueou a inicialização são perguntas para o "
        "TSE.", "",
        "## Limite", "",
        "O log é escrito pelo próprio software da urna. Ele mostra consistência interna, não prova independente de "
        "qual software foi executado. Essa prova depende de procedimentos externos (cerimônia de assinatura e "
        "lacração, publicação de hashes, testes de autenticidade e integridade em urnas sorteadas), que este trabalho "
        "não verificou.",
    ]
    (TAB / "v13_logs_EXPLORATORIO.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
