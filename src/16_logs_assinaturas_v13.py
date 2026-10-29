"""v1.3 (EXPLORATÓRIO) — checagem descritiva dos logs de urna baixados no plano v1.2 (D12).

Feita depois de ver os logs, para responder a perguntas públicas sobre arquivos de assinatura e a mensagem
"Problema ao desmontar a MR" registrada pelo módulo GAP. Sem plano prévio: tudo aqui é descritivo e exploratório.

Uso: python src/16_logs_assinaturas_v13.py
Saídas: output/tables/v13_logs_EXPLORATORIO.md, v13_falhas_assinatura.csv, v13_msg_mr_por_dia.csv,
        v13_arquivos_assinatura.csv
"""

import re
from collections import Counter, defaultdict

import pandas as pd

from common import OUTPUT, PROCESSED, RAW, textos_log_urna

TAB = OUTPUT / "tables"
MSG_MR = "Problema ao desmontar a MR"
RE_VERIF = re.compile(r"Verifica\S* de assinatura.*\[(SUCESSO|ERRO|[A-Z]+)\]\s*$")
RE_ARQ = re.compile(r"\[(?:Pacote: )?(/[^\]]+\.vs[a-z])\]")


def data_iso(d: str) -> str:
    return f"{d[6:10]}-{d[3:5]}-{d[:2]}"


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
        linhas = [ln for texto in textos_log_urna(lg) for ln in texto.splitlines()]
        dias_log, dias_mr = set(), set()
        for p in (ln.split("\t") for ln in linhas):
            if len(p) < 5:
                continue
            dia = data_iso(p[0][:10])
            dias_log.add(dia)
            m = RE_VERIF.search(p[4])
            if m:
                ok = m.group(1) == "SUCESSO"
                verif[(dia == "2026-10-25", ok)] += 1
                a = RE_ARQ.search(p[4])
                nome = re.sub(r"\d", "N", a.group(1)) if a else "?"
                arquivos[(nome.rsplit(".", 1)[1], nome)] += 1
                if not ok:
                    falhas.append({"uf": uf, "mun": mun, "zona": zona, "secao": secao, "data_hora_urna": p[0],
                                   "modulo": p[3], "mensagem": p[4]})
            if MSG_MR in p[4]:
                dias_mr.add(dia)
                mr_dia[dia].add(chave)
        por_secao.append({"uf": uf, "mun": mun, "zona": zona, "secao": secao, "grupo": sel.loc[chave, "grupo"],
                          "tem_1t": "2026-10-04" in dias_log, "mr_ate_1t": any(d <= "2026-10-04" for d in dias_mr),
                          "mr_25_10": "2026-10-25" in dias_mr})
    s = pd.DataFrame(por_secao).drop_duplicates(["uf", "mun", "zona", "secao"])
    f = pd.DataFrame(falhas)
    f.to_csv(TAB / "v13_falhas_assinatura.csv", index=False)
    mr = pd.DataFrame([{"data": d, "urnas_com_mensagem": len(v)} for d, v in sorted(mr_dia.items())])
    mr.to_csv(TAB / "v13_msg_mr_por_dia.csv", index=False)
    arq = pd.DataFrame([{"extensao": e, "arquivo": n, "verificacoes": c} for (e, n), c in arquivos.items()])
    arq.sort_values(["extensao", "arquivo"]).to_csv(TAB / "v13_arquivos_assinatura.csv", index=False)

    fmt = lambda v: f"{v:,.0f}".replace(",", ".")  # noqa: E731
    total = sum(verif.values())
    no_dia = verif[(True, True)] + verif[(True, False)]
    g0 = s[s.grupo == "G0"]
    tab_mr = pd.DataFrame({
        "seções com log": [len(s), len(g0)],
        "com eventos do 1º turno (04/10)": [int(s.tem_1t.sum()), int(g0.tem_1t.sum())],
        "mensagem da MR até 04/10": [int(s.mr_ate_1t.sum()), int(g0.mr_ate_1t.sum())],
        "mensagem da MR em 25/10": [int(s.mr_25_10.sum()), int(g0.mr_25_10.sum())],
    }, index=["todas (G0 + G1 + G2)", "só a amostra aleatória G0"])
    turno = [n for _, n in arquivos if "turno" in n.lower()]
    md = [
        "# v1.3 — checagem dos logs de urna (EXPLORATÓRIO)", "",
        "Checagem descritiva feita **depois** de abrir os logs baixados no plano v1.2 (D12), para responder a "
        "perguntas públicas. Não houve plano prévio; nada aqui altera a classificação confirmatória. Os logs cobrem "
        "todas as seções encerradas depois das 17h15 e uma amostra aleatória de 600 das demais (G0); os números de "
        "G0 são os únicos que representam o conjunto das urnas. Fonte: TSE, logs de urna (D12); hashes em "
        "`data/raw/MANIFEST.csv`.", "",
        "## Verificações de assinatura registradas no log", "",
        f"- Total: {fmt(total)} verificações, das quais {fmt(verif[(True, False)] + verif[(False, False)])} sem "
        f"\"SUCESSO\". No dia do 2º turno (25/10): {fmt(no_dia)} verificações, {fmt(verif[(True, False)])} sem "
        "\"SUCESSO\".",
        f"- Arquivos de assinatura distintos (dígitos trocados por N): {len(arquivos)}, sendo "
        f"{sum(1 for e, _ in arquivos if e == 'vst')} `.vst` (software), "
        f"{sum(1 for e, _ in arquivos if e == 'vsc')} `.vsc` e {sum(1 for e, _ in arquivos if e == 'vsu')} `.vsu` "
        "(dados e configuração). Lista em `v13_arquivos_assinatura.csv`.",
        f"- Arquivos com \"turno\" no nome: {len(turno)}.", "",
        "Falhas (`v13_falhas_assinatura.csv`):", "",
        (f[["uf", "mun", "zona", "secao", "data_hora_urna", "mensagem"]].to_markdown(index=False)
         if len(f) else "nenhuma"), "",
        "Em cada falha, o log registra em seguida erro de integridade na inicialização e a urna desligada pela chave; "
        "o aplicativo não é iniciado.", "",
        f"## Mensagem \"{MSG_MR}\" (módulo GAP)", "",
        tab_mr.to_markdown(), "",
        "A mensagem aparece na inicialização, logo depois de a urna reconhecer a \"mídia de resultado de 2º turno\", "
        "e a urna segue para o aplicativo de votação. Distribuição por dia em `v13_msg_mr_por_dia.csv`. A causa não "
        "está documentada no material consultado; a hipótese de ser comportamento sistemático da preparação ou do "
        "software do 2º turno decorre só de ela aparecer em quase todas as urnas e só nesse turno.", "",
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
