# Revisão v1.1 — sensibilidades e detalhamentos (EXPLORATÓRIO)

Plano carimbado antes da execução: `docs/plano_v1_1.md` (+ `.ots`). Nada aqui altera a classificação confirmatória.

## T1 — intervalo e seções excluídas

- Clopper-Pearson exato, k = 0, n = 5692: limite superior 1 − 0,025^(1/n) = 0,0648%.
- Com pesos amostrais (tamanho efetivo de Kish = 5.676): limite superior 0,0650%.
- Seções agregadas sorteadas: 205; em 0 delas a seção principal também foi sorteada e verificada (as demais têm votos no BU de uma principal não sorteada).
- Seções sem BU "Totalizado": {'sem_bu_totalizado[Recebida|Recebido]': 127, 'sem_bu_totalizado[Nao instalada|Sem arquivo]': 1}.
- Escopo: a reconciliação BU × totalização não verifica se a urna registrou a intenção do eleitor.

## T2 — pior caso

- Confirmatório (461 seções): 2,50% da margem oficial de 4.430.191 votos.
- Ponderado (52 seções): 0,48% da margem.

## T2 — distribuição das 461 seções (confirmatório)

| votos_2t    |   secoes_total |   anomalas |   pct_anomalas_na_faixa |
|:------------|---------------:|-----------:|------------------------:|
| até 100     |           5467 |        209 |                   3.823 |
| 101–150     |          15344 |        113 |                   0.736 |
| 151–200     |          64605 |         78 |                   0.121 |
| 201–250     |         147623 |         41 |                   0.028 |
| 251–300     |         193691 |         16 |                   0.008 |
| mais de 300 |          71167 |          4 |                   0.006 |

|z| entre 4,08 e 19,57; p corrigido (BH) máximo 0.04956; p sem correção máximo 4.59e-05.

| z     |   anomalas |
|:------|-----------:|
| 4,5–5 |        302 |
| 5–6   |         94 |
| 6–8   |         47 |
| > 8   |         18 |

## T2 — especificações alternativas

| especificacao                     |   secoes_no_modelo |   anomalas |   positivas_13 |   negativas_13 |   p_direcao |   p_agrupamento |   votos_nas_anomalas |   pior_caso_pct_margem | classificacao_pelos_criterios                                                                                                                                                                                    |
|:----------------------------------|-------------------:|-----------:|---------------:|---------------:|------------:|----------------:|---------------------:|-----------------------:|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| S1_sem_perfil_D3                  |             497508 |        424 |            259 |            165 |      0      |           0.001 |                50794 |                 2.2931 | Critérios (a), (b) e (c) atendidos: seções anômalas agrupadas e direcionais, condicionais ao perfil e ao município. Achado a localizar (componentes listados); hipótese padrão: erro de especificação do modelo. |
| S2_logit_ponderado                |             497508 |       3091 |           2456 |            635 |      0      |           0.001 |               648561 |                29.2791 | Critérios (a), (b) e (c) atendidos: seções anômalas agrupadas e direcionais, condicionais ao perfil e ao município. Achado a localizar (componentes listados); hipótese padrão: erro de especificação do modelo. |
| S3_ponderado_sem_locais_indigenas |             496680 |         38 |             22 |             16 |      0.4177 |           0.001 |                 8129 |                 0.367  | Heterogeneidade regional: falta (b) direção.                                                                                                                                                                     |

## T3 — sem covariáveis do Censo 2022

|   ano |   permutacoes |   r2_condicional |      I |   p_sim |   clusters_fdr |   clusters_2026_exclusivos |
|------:|--------------:|-----------------:|-------:|--------:|---------------:|---------------------------:|
|  2014 |           999 |           0.9749 | 0.3002 |  0.001  |              0 |                        nan |
|  2014 |          9999 |           0.9749 | 0.3002 |  0.0001 |             14 |                        nan |
|  2018 |           999 |           0.9961 | 0.2107 |  0.001  |              0 |                        nan |
|  2018 |          9999 |           0.9961 | 0.2107 |  0.0001 |              0 |                        nan |
|  2022 |           999 |           0.9982 | 0.1965 |  0.001  |              0 |                        nan |
|  2022 |          9999 |           0.9982 | 0.1965 |  0.0001 |             20 |                        nan |
|  2026 |           999 |           0.9977 | 0.2508 |  0.001  |              0 |                          0 |
|  2026 |          9999 |           0.9977 | 0.2508 |  0.0001 |              0 |                          0 |

Fontes: TSE (D1–D4), IBGE (D7); hashes em `data/raw/MANIFEST.csv`.

## Adendo — diagnóstico de S2 (plano carimbado em `docs/plano_v1_1_adendo.md`)

### D1: anômalas de S2 por faixa de participação do 13

| y       |   secoes_total |   anomalas_S2 |   pct_das_secoes |   pct_das_anomalas_S2 |   anomalas_S2b |   pct_das_anomalas_S2b |
|:--------|---------------:|--------------:|-----------------:|----------------------:|---------------:|-----------------------:|
| 0–10%   |            374 |           216 |             0.08 |                  6.99 |            102 |                   7.99 |
| 10–25%  |          20450 |            49 |             4.11 |                  1.59 |             28 |                   2.19 |
| 25–50%  |         226965 |            24 |            45.58 |                  0.78 |             23 |                   1.8  |
| 50–75%  |         190741 |           261 |            38.31 |                  8.44 |             48 |                   3.76 |
| 75–90%  |          52565 |           114 |            10.56 |                  3.69 |             16 |                   1.25 |
| 90–100% |           6802 |          2427 |             1.37 |                 78.52 |           1059 |                  82.99 |

Proporção das anômalas de S2 em faixas extremas (abaixo de 10% ou acima de 90%): 85.5%.

### S2b: logit com peso de variância inversa n·p̂·(1−p̂)

| especificacao                    |   secoes_no_modelo |   anomalas |   positivas_13 |   negativas_13 |   p_direcao |   p_agrupamento |   votos_nas_anomalas |   pior_caso_pct_margem | classificacao_pelos_criterios                                                                                                                                                                                    |
|:---------------------------------|-------------------:|-----------:|---------------:|---------------:|------------:|----------------:|---------------------:|-----------------------:|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| S2b_logit_peso_variancia_inversa |             497508 |       1276 |           1106 |            170 |           0 |           0.001 |               295627 |                 13.346 | Critérios (a), (b) e (c) atendidos: seções anômalas agrupadas e direcionais, condicionais ao perfil e ao município. Achado a localizar (componentes listados); hipótese padrão: erro de especificação do modelo. |
