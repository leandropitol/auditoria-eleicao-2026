# Adendo ao plano v1.1 — diagnóstico da especificação S2

**Status:** redigido em 2026-10-29, **depois** de ver o resultado de S2 e **antes** de rodar o diagnóstico abaixo. Carimbado com OpenTimestamps antes da execução. Exploratório.

## Resultado que motivou o adendo

S2, executada como planejada (`log(v13/v22)` ponderado pelos votos dos dois finalistas): 3.091 seções anômalas, 2.456 acima do previsto para o 13 e 635 abaixo, pior caso de 29,3% da margem. Esse resultado é reportado integralmente, como saiu.

## Hipótese a testar (erro de especificação do próprio plano)

Num modelo em logit, a variância da resposta numa seção com n votos e proporção p é aproximadamente `1 / (n · p · (1 − p))`. Ponderar só por n subestima a variância das seções em que um candidato tem quase todos os votos (p perto de 0 ou de 1). Essas seções aparecem como "anômalas" por construção. Se a hipótese estiver certa:

1. as anômalas de S2 se concentram em seções com participação do 13 abaixo de 10% ou acima de 90% (D1);
2. com o peso de variância inversa correto, `n · p̂ · (1 − p̂)`, em que p̂ é a proporção observada limitada a [0,02; 0,98], o número de anômalas cai para a ordem de grandeza das demais especificações (S2b).

## O que será rodado

- **D1:** distribuição das anômalas de S2 por faixa de participação do 13 (0–10%, 10–25%, 25–50%, 50–75%, 75–90%, 90–100%), comparada com a distribuição de todas as seções.
- **S2b:** igual a S2, mas com peso `n · p̂ · (1 − p̂)`. Mesmos critérios (a), (b) e (c), FDR q = 0,05, 5 vizinhos, 999 permutações, e pior caso.

## Como será lido

- Se (1) e (2) se confirmarem, S2 é registrada como especificação incorreta do plano, mantida no relatório com essa explicação.
- Se não se confirmarem, o resultado de S2 permanece sem explicação e é tratado como tal: a hipótese padrão continua sendo erro de modelo, mas o relatório diz explicitamente que não foi demonstrada.
