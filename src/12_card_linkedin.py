"""Imagem de divulgação (LinkedIn, 1080 × 1350) com os principais resultados.

Os números vêm de output/relatorio/dados_relatorio.json (gerado por src/11_relatorio_publico.py).
Uso: python src/12_card_linkedin.py   → output/divulgacao/card_linkedin.png
"""

import json
import textwrap

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

from common import OUTPUT  # noqa: E402

AZUL, LARANJA, TEXTO, TEXTO2, FUNDO, CARTAO = "#1F4E79", "#B8481C", "#0b0b0b", "#52514e", "#F4F6F9", "#FFFFFF"
SERIF, SANS = "Georgia", "Segoe UI"


def main() -> None:
    d = json.loads((OUTPUT / "relatorio" / "dados_relatorio.json").read_text(encoding="utf-8"))
    fig = plt.figure(figsize=(10.8, 13.5), dpi=100)
    fig.patch.set_facecolor(FUNDO)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1080)
    ax.set_ylim(0, 1350)
    ax.axis("off")

    ax.text(70, 1270, "AUDITORIA ESTATÍSTICA · DADOS PÚBLICOS", fontsize=15, color=LARANJA, fontweight="bold",
            family=SANS)
    ax.text(70, 1235, "O que os dados públicos\ndizem sobre o 2º turno\npresidencial de 2026", fontsize=40,
            color=AZUL, fontweight="bold", family=SERIF, va="top", linespacing=1.15)
    ax.text(70, 1015, "Plano registrado antes da coleta · dados do TSE e do IBGE · código aberto", fontsize=16,
            color=TEXTO2, family=SANS)

    cartoes = [
        (f"{d['t1']['divergencias']} divergências",
         f"entre boletins de urna e resultado oficial\nem {d['t1']['verificadas']} urnas sorteadas "
         f"({d['t1']['votos']} votos conferidos)"),
        ("Mapa no padrão",
         "padrão geográfico de 2026 dentro do observado\nem 2014, 2018 e 2022; nenhum aglomerado exclusivo"),
        (f"≈ {d['t6']['p']}%",
         f"chance histórica de virada com vantagem de\n{d['votos_1t']['margem_pp']} ponto no 1º turno "
         f"({d['t6']['casos']} segundos turnos, 6 países)"),
        (f"+{d['t5']['erro_medio']} pontos",
         f"erro médio das {d['t5']['n26']} pesquisas finais na margem,\ntodas na mesma direção"),
    ]
    larg, alt, gap = 455, 300, 30
    pos = [(70, 650), (70 + larg + gap, 650), (70, 650 - alt - gap), (70 + larg + gap, 650 - alt - gap)]
    for (x, y), (numero, texto) in zip(pos, cartoes):
        ax.add_patch(FancyBboxPatch((x, y), larg, alt, boxstyle="round,pad=0,rounding_size=18",
                                    facecolor=CARTAO, edgecolor="#D0D5DD", linewidth=1.2))
        ax.add_patch(FancyBboxPatch((x, y + alt - 8), larg, 8, boxstyle="square,pad=0", facecolor=AZUL,
                                    edgecolor="none"))
        ax.text(x + 32, y + alt - 55, numero, fontsize=34, color=AZUL, fontweight="bold", family=SANS, va="top")
        ax.text(x + 32, y + alt - 140, textwrap.fill(" ".join(texto.split()), 40), fontsize=15, color=TEXTO,
                family=SANS, va="top", linespacing=1.4)

    ax.text(70, 245, "Veredito pelas regras fixadas antes da análise:", fontsize=17, color=TEXTO, family=SANS,
            fontweight="bold")
    ax.text(70, 210, "anomalia com causa mundana (desfecho B). Nenhum achado com tamanho\n"
                     "para alterar o resultado; versão preliminar, aberta à revisão.",
            fontsize=16, color=TEXTO2, family=SANS, va="top", linespacing=1.35)
    ax.plot([70, 1010], [110, 110], color="#D0D5DD", linewidth=1.2)
    ax.text(70, 65, d["repo"].replace("https://", ""), fontsize=17, color=AZUL, family=SANS, fontweight="bold")
    ax.text(1010, 65, "Leandro Marques Pitol", fontsize=15, color=TEXTO2, family=SANS, ha="right")

    destino = OUTPUT / "divulgacao"
    destino.mkdir(parents=True, exist_ok=True)
    fig.savefig(destino / "card_linkedin.png", facecolor=FUNDO)
    print(destino / "card_linkedin.png")


if __name__ == "__main__":
    main()
