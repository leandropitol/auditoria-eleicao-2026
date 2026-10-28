# T5 — resumo

Linhas de pesquisa de 2º turno extraídas da fonte: 312.

## A. Regra 2 como fixada em `docs/desenho_T5_T6.md`

Inclui, para institutos sem pesquisa entre os turnos, pesquisas de confronto direto feitas antes do 1º turno.

| Métrica | Valor |
|---|---|
| pesquisas finais (instituto × eleição) | 51 |
| pesquisas finais por eleição | {2010: 4, 2014: 4, 2018: 9, 2022: 15, 2026: 19} |
| margem real 2026 (p.p., A − B sobre A+B) | -3.57 |
| institutos 2026 com histórico | 10 |
| dos quais com erro absoluto 2026 ≤ maior erro absoluto histórico do instituto | 2 |
| institutos 2026 sem histórico | 9 |
| erro médio 2026 (p.p.) | 5.209 |
| variância dos erros explicada pela eleição (η²) | 0.076 |
| ANOVA erro ~ eleição: p | 0.4451 |
| concordância média de sinal entre pares de institutos na mesma eleição | 0.631 |

### Erro por eleição (p.p. na margem)

|   ano |   count |   mean |   std |   min |   max |
|------:|--------:|-------:|------:|------:|------:|
|  2010 |       4 |   0.82 |  1.5  | -1.24 |  2.34 |
|  2014 |       4 |   1.07 |  3.68 | -3.88 |  4.72 |
|  2018 |       9 |   4.85 |  7.24 | -3.44 | 19.28 |
|  2022 |      15 |   5.3  |  8.32 | -6.25 | 25.84 |
|  2026 |      19 |   5.21 |  1.48 |  2.34 |  7.83 |

### Critério do plano — 2026 por instituto

| instituto          |   erro_2026 |   n_hist |   max_abs_erro_hist |   dentro_hist_instituto |   percentil_no_historico_combinado |
|:-------------------|------------:|---------:|--------------------:|------------------------:|-----------------------------------:|
| alfa               |        7.64 |        0 |              nan    |                     nan |                              81.25 |
| atlasintel         |        5.1  |        1 |                5.02 |                       0 |                              68.75 |
| colectta           |        3.03 |        0 |              nan    |                     nan |                              46.88 |
| datafolha          |        4.62 |        4 |                2.45 |                       0 |                              62.5  |
| datatrends         |        7.74 |        0 |              nan    |                     nan |                              81.25 |
| futura             |        3.88 |        1 |                2.44 |                       0 |                              59.38 |
| gerp               |        6.73 |        1 |                6.25 |                       0 |                              81.25 |
| ideia              |        5.7  |        2 |                2.4  |                       0 |                              71.88 |
| indexa             |        4.8  |        0 |              nan    |                     nan |                              65.62 |
| instituto franca   |        5.84 |        0 |              nan    |                     nan |                              75    |
| ipespe             |        4.62 |        2 |                5.65 |                       1 |                              62.5  |
| mda                |        4.99 |        3 |                3.88 |                       0 |                              65.62 |
| nexus              |        4.65 |        0 |              nan    |                     nan |                              62.5  |
| palver             |        4.58 |        0 |              nan    |                     nan |                              62.5  |
| poderdata          |        4.6  |        2 |               19.28 |                       1 |                              62.5  |
| quaest             |        4.67 |        1 |                1.64 |                       0 |                              62.5  |
| real time big data |        7.83 |        1 |                2.38 |                       0 |                              81.25 |
| verita             |        5.62 |        0 |              nan    |                     nan |                              68.75 |
| vox brasil         |        2.34 |        0 |              nan    |                     nan |                              28.12 |

### Pesquisas finais

|   ano | instituto          | fim_campo   |     n |   pct_A |   pct_B |   margem_pesquisa |   margem_real |   erro |   dp_amostral_margem |   erro_em_dp | registro_tse               | protocolo_tse                                                                       |
|------:|:-------------------|:------------|------:|--------:|--------:|------------------:|--------------:|-------:|---------------------:|-------------:|:---------------------------|:------------------------------------------------------------------------------------|
|  2010 | datafolha          | 2010-10-30  |   nan |    51   |    41   |             10.87 |         12.11 |  -1.24 |               nan    |       nan    | sem registro no portal     |                                                                                     |
|  2010 | ibope              | 2010-10-30  |   nan |    52   |    40   |             13.04 |         12.11 |   0.94 |               nan    |       nan    | sem registro no portal     |                                                                                     |
|  2010 | sensus             | 2010-10-29  |   nan |    50.3 |    37.6 |             14.45 |         12.11 |   2.34 |               nan    |       nan    | sem registro no portal     |                                                                                     |
|  2010 | vox populi         | 2010-10-30  |   nan |    51   |    39   |             13.33 |         12.11 |   1.23 |               nan    |       nan    | sem registro no portal     |                                                                                     |
|  2014 | datafolha          | 2014-10-25  | 19318 |    52   |    48   |              4    |          3.28 |   0.72 |                 0.72 |         1    | registro na data, n difere | BR012102014                                                                         |
|  2014 | ibope              | 2014-10-25  |  3010 |    53   |    47   |              6    |          3.28 |   2.72 |                 1.82 |         1.5  | n confere                  | BR011952014                                                                         |
|  2014 | mda                | 2014-10-24  |  2002 |    49.7 |    50.3 |             -0.6  |          3.28 |  -3.88 |                 2.23 |        -1.74 | n confere                  | BR011992014                                                                         |
|  2014 | vox populi         | 2014-10-25  |  2000 |    54   |    46   |              8    |          3.28 |   4.72 |                 2.23 |         2.12 | n confere                  | BR011852014                                                                         |
|  2018 | datafolha          | 2018-10-27  | 18731 |    47   |    39   |              9.3  |         10.26 |  -0.96 |                 0.73 |        -1.32 | registro na data, n difere | BR024602018                                                                         |
|  2018 | fsb                | 2018-10-21  |  2000 |    52   |    35   |             19.54 |         10.26 |   9.28 |                 2.19 |         4.23 | n confere                  | BR036892018                                                                         |
|  2018 | ibope              | 2018-10-27  |  3010 |    47   |    41   |              6.82 |         10.26 |  -3.44 |                 1.82 |        -1.89 | n confere                  | BR029342018                                                                         |
|  2018 | ideia              | 2018-10-10  |  2036 |    48   |    41   |              7.87 |         10.26 |  -2.4  |                 2.21 |        -1.08 | n confere                  | BR096872018                                                                         |
|  2018 | ipespe             | 2018-10-24  |  2000 |    51   |    37   |             15.91 |         10.26 |   5.65 |                 2.21 |         2.56 | n confere                  | BR082832018                                                                         |
|  2018 | mda                | 2018-10-27  |  2002 |    49   |    37   |             13.95 |         10.26 |   3.69 |                 2.21 |         1.67 | n confere                  | BR069332018                                                                         |
|  2018 | parana pesquisas   | 2018-10-25  |  2120 |    53   |    35   |             20.45 |         10.26 |  10.19 |                 2.13 |         4.8  | n confere                  | BR067852018                                                                         |
|  2018 | poderdata          | 2018-10-18  |  4000 |    57   |    31   |             29.55 |         10.26 |  19.28 |                 1.51 |        12.77 | n confere                  | BR088522018                                                                         |
|  2018 | real time big data | 2018-10-24  |  5000 |    49   |    38   |             12.64 |         10.26 |   2.38 |                 1.4  |         1.7  | n confere                  | BR089802018                                                                         |
|  2022 | atlasintel         | 2022-10-29  |  7500 |    52.4 |    45.7 |              6.83 |          1.8  |   5.02 |                 1.15 |         4.36 | n confere                  | BR048382022                                                                         |
|  2022 | datafolha          | 2022-10-29  |  8308 |    49   |    45   |              4.26 |          1.8  |   2.45 |                 1.1  |         2.24 | registro na data, n difere | BR082972022                                                                         |
|  2022 | datatempo          | 2021-09-15  | 20250 |    53.1 |    30.1 |             27.64 |          1.8  |  25.84 |                 0.68 |        38.26 | não localizado             |                                                                                     |
|  2022 | fsb                | 2022-09-25  | 20000 |    52   |    40   |             13.04 |          1.8  |  11.24 |                 0.7  |        16.03 | registro na data, n difere | BR081232022                                                                         |
|  2022 | futura             | 2022-10-26  |  2000 |    46.6 |    47.2 |             -0.64 |          1.8  |  -2.44 |                 2.24 |        -1.09 | n confere                  | BR079032022                                                                         |
|  2022 | gerp               | 2022-10-26  |  2095 |    43   |    47   |             -4.44 |          1.8  |  -6.25 |                 2.18 |        -2.86 | n confere                  | BR054182022                                                                         |
|  2022 | ideia              | 2022-10-19  |  1500 |    50   |    46   |              4.17 |          1.8  |   2.36 |                 2.58 |         0.92 | n confere                  | BR000532022                                                                         |
|  2022 | ipec               | 2022-10-29  |  4272 |    50   |    43   |              7.53 |          1.8  |   5.72 |                 1.53 |         3.75 | n confere                  | BR052562022                                                                         |
|  2022 | ipespe             | 2022-10-24  |  1100 |    50   |    44   |              6.38 |          1.8  |   4.58 |                 3.01 |         1.52 | n confere                  | BR080442022                                                                         |
|  2022 | mda                | 2022-10-28  |  2002 |    46.9 |    44.9 |              2.18 |          1.8  |   0.37 |                 2.23 |         0.17 | n confere                  | BR018202022                                                                         |
|  2022 | parana pesquisas   | 2022-10-28  |  2400 |    47.1 |    46.3 |              0.86 |          1.8  |  -0.95 |                 2.04 |        -0.46 | n confere                  | BR095732022                                                                         |
|  2022 | poderdata          | 2022-10-25  |  5000 |    49   |    44   |              5.38 |          1.8  |   3.57 |                 1.41 |         2.53 | n confere                  | BR011592022                                                                         |
|  2022 | ponteio politica   | 2021-11-18  | 10000 |    50   |    32   |             21.95 |          1.8  |  20.15 |                 0.98 |        20.65 | não localizado             |                                                                                     |
|  2022 | quaest             | 2022-10-29  |  2000 |    45   |    42   |              3.45 |          1.8  |   1.64 |                 2.23 |         0.74 | n confere                  | BR057652022                                                                         |
|  2022 | ranking brasil     | 2022-03-12  | 30000 |    45   |    38.3 |              8.04 |          1.8  |   6.24 |                 0.58 |        10.84 | registro na data, n difere | BR047242022                                                                         |
|  2026 | alfa               | 2026-10-22  |  2700 |    49.9 |    46   |              4.07 |         -3.57 |   7.64 |                 1.92 |         3.97 | registro na data, n difere | BR084962026                                                                         |
|  2026 | atlasintel         | 2026-10-23  |  4990 |    49.9 |    48.4 |              1.53 |         -3.57 |   5.1  |                 1.42 |         3.6  | registro na data, n difere | BR088482026;BR063802026;BR055812026;BR003392026;BR009572026;BR094992026;BR040622026 |
|  2026 | colectta           | 2026-10-23  |  3000 |    46   |    46.5 |             -0.54 |         -3.57 |   3.03 |                 1.83 |         1.66 | n confere                  | BR056012026                                                                         |
|  2026 | datafolha          | 2026-10-24  |  4050 |    48   |    47   |              1.05 |         -3.57 |   4.62 |                 1.57 |         2.94 | n confere                  | BR095402026                                                                         |
|  2026 | datatrends         | 2026-10-21  |  2000 |    50   |    46   |              4.17 |         -3.57 |   7.74 |                 2.23 |         3.46 | n confere                  | BR033652026                                                                         |
|  2026 | futura             | 2026-10-24  |  2000 |    48.2 |    47.9 |              0.31 |         -3.57 |   3.88 |                 2.24 |         1.74 | não localizado             |                                                                                     |
|  2026 | gerp               | 2026-10-24  |  2400 |    49   |    46   |              3.16 |         -3.57 |   6.73 |                 2.04 |         3.3  | n confere                  | BR093272026                                                                         |
|  2026 | ideia              | 2026-10-19  |  1500 |    48   |    46   |              2.13 |         -3.57 |   5.7  |                 2.58 |         2.21 | n confere                  | BR082512026                                                                         |
|  2026 | indexa             | 2026-10-21  |  2000 |    45.2 |    44.1 |              1.23 |         -3.57 |   4.8  |                 2.24 |         2.15 | n confere                  | BR023482026                                                                         |
|  2026 | instituto franca   | 2026-10-23  |  1537 |    45.1 |    43.1 |              2.27 |         -3.57 |   5.84 |                 2.55 |         2.29 | n confere                  | BR048632026                                                                         |
|  2026 | ipespe             | 2026-10-22  |  1500 |    48   |    47   |              1.05 |         -3.57 |   4.62 |                 2.58 |         1.79 | n confere                  | BR043502026                                                                         |
|  2026 | mda                | 2026-10-23  |  2032 |    46.3 |    45   |              1.42 |         -3.57 |   4.99 |                 2.22 |         2.25 | registro na data, n difere | BR021362026                                                                         |
|  2026 | nexus              | 2026-10-24  |  2000 |    47   |    46   |              1.08 |         -3.57 |   4.65 |                 2.24 |         2.08 | n confere                  | BR082342026                                                                         |
|  2026 | palver             | 2026-10-24  |  5000 |    50   |    49   |              1.01 |         -3.57 |   4.58 |                 1.41 |         3.24 | n confere                  | BR017942026                                                                         |
|  2026 | poderdata          | 2026-10-24  |  4000 |    49   |    48   |              1.03 |         -3.57 |   4.6  |                 1.58 |         2.91 | n confere                  | BR028282026                                                                         |
|  2026 | quaest             | 2026-10-24  |  3702 |    46   |    45   |              1.1  |         -3.57 |   4.67 |                 1.64 |         2.84 | n confere                  | BR091582026                                                                         |
|  2026 | real time big data | 2026-10-22  |  2000 |    49   |    45   |              4.26 |         -3.57 |   7.83 |                 2.23 |         3.5  | n confere                  | BR096702026                                                                         |
|  2026 | verita             | 2026-10-23  | 15554 |    49.8 |    47.8 |              2.05 |         -3.57 |   5.62 |                 0.8  |         7.01 | n confere                  | BR031812026                                                                         |
|  2026 | vox brasil         | 2026-10-22  |  2100 |    44.3 |    45.4 |             -1.23 |         -3.57 |   2.34 |                 2.18 |         1.07 | n confere                  | BR032592026                                                                         |

## B. Correção exploratória (DESVIOS.md): só pesquisas com fim de campo entre os turnos

| Métrica | Valor |
|---|---|
| pesquisas finais (instituto × eleição) | 47 |
| pesquisas finais por eleição | {2010: 4, 2014: 4, 2018: 9, 2022: 11, 2026: 19} |
| margem real 2026 (p.p., A − B sobre A+B) | -3.57 |
| institutos 2026 com histórico | 10 |
| dos quais com erro absoluto 2026 ≤ maior erro absoluto histórico do instituto | 2 |
| institutos 2026 sem histórico | 9 |
| erro médio 2026 (p.p.) | 5.209 |
| variância dos erros explicada pela eleição (η²) | 0.211 |
| ANOVA erro ~ eleição: p | 0.03727 |
| concordância média de sinal entre pares de institutos na mesma eleição | 0.613 |

### Erro por eleição (p.p. na margem)

|   ano |   count |   mean |   std |   min |   max |
|------:|--------:|-------:|------:|------:|------:|
|  2010 |       4 |   0.82 |  1.5  | -1.24 |  2.34 |
|  2014 |       4 |   1.07 |  3.68 | -3.88 |  4.72 |
|  2018 |       9 |   4.85 |  7.24 | -3.44 | 19.28 |
|  2022 |      11 |   1.46 |  3.59 | -6.25 |  5.72 |
|  2026 |      19 |   5.21 |  1.48 |  2.34 |  7.83 |

### Critério do plano — 2026 por instituto

| instituto          |   erro_2026 |   n_hist |   max_abs_erro_hist |   dentro_hist_instituto |   percentil_no_historico_combinado |
|:-------------------|------------:|---------:|--------------------:|------------------------:|-----------------------------------:|
| alfa               |        7.64 |        0 |              nan    |                     nan |                              89.29 |
| atlasintel         |        5.1  |        1 |                5.02 |                       0 |                              78.57 |
| colectta           |        3.03 |        0 |              nan    |                     nan |                              53.57 |
| datafolha          |        4.62 |        4 |                2.45 |                       0 |                              71.43 |
| datatrends         |        7.74 |        0 |              nan    |                     nan |                              89.29 |
| futura             |        3.88 |        1 |                2.44 |                       0 |                              67.86 |
| gerp               |        6.73 |        1 |                6.25 |                       0 |                              89.29 |
| ideia              |        5.7  |        2 |                2.4  |                       0 |                              82.14 |
| indexa             |        4.8  |        0 |              nan    |                     nan |                              75    |
| instituto franca   |        5.84 |        0 |              nan    |                     nan |                              85.71 |
| ipespe             |        4.62 |        2 |                5.65 |                       1 |                              71.43 |
| mda                |        4.99 |        3 |                3.88 |                       0 |                              75    |
| nexus              |        4.65 |        0 |              nan    |                     nan |                              71.43 |
| palver             |        4.58 |        0 |              nan    |                     nan |                              71.43 |
| poderdata          |        4.6  |        2 |               19.28 |                       1 |                              71.43 |
| quaest             |        4.67 |        1 |                1.64 |                       0 |                              71.43 |
| real time big data |        7.83 |        1 |                2.38 |                       0 |                              89.29 |
| verita             |        5.62 |        0 |              nan    |                     nan |                              78.57 |
| vox brasil         |        2.34 |        0 |              nan    |                     nan |                              32.14 |

### Pesquisas finais

|   ano | instituto          | fim_campo   |     n |   pct_A |   pct_B |   margem_pesquisa |   margem_real |   erro |   dp_amostral_margem |   erro_em_dp | registro_tse               | protocolo_tse                                                                       |
|------:|:-------------------|:------------|------:|--------:|--------:|------------------:|--------------:|-------:|---------------------:|-------------:|:---------------------------|:------------------------------------------------------------------------------------|
|  2010 | datafolha          | 2010-10-30  |   nan |    51   |    41   |             10.87 |         12.11 |  -1.24 |               nan    |       nan    | sem registro no portal     |                                                                                     |
|  2010 | ibope              | 2010-10-30  |   nan |    52   |    40   |             13.04 |         12.11 |   0.94 |               nan    |       nan    | sem registro no portal     |                                                                                     |
|  2010 | sensus             | 2010-10-29  |   nan |    50.3 |    37.6 |             14.45 |         12.11 |   2.34 |               nan    |       nan    | sem registro no portal     |                                                                                     |
|  2010 | vox populi         | 2010-10-30  |   nan |    51   |    39   |             13.33 |         12.11 |   1.23 |               nan    |       nan    | sem registro no portal     |                                                                                     |
|  2014 | datafolha          | 2014-10-25  | 19318 |    52   |    48   |              4    |          3.28 |   0.72 |                 0.72 |         1    | registro na data, n difere | BR012102014                                                                         |
|  2014 | ibope              | 2014-10-25  |  3010 |    53   |    47   |              6    |          3.28 |   2.72 |                 1.82 |         1.5  | n confere                  | BR011952014                                                                         |
|  2014 | mda                | 2014-10-24  |  2002 |    49.7 |    50.3 |             -0.6  |          3.28 |  -3.88 |                 2.23 |        -1.74 | n confere                  | BR011992014                                                                         |
|  2014 | vox populi         | 2014-10-25  |  2000 |    54   |    46   |              8    |          3.28 |   4.72 |                 2.23 |         2.12 | n confere                  | BR011852014                                                                         |
|  2018 | datafolha          | 2018-10-27  | 18731 |    47   |    39   |              9.3  |         10.26 |  -0.96 |                 0.73 |        -1.32 | registro na data, n difere | BR024602018                                                                         |
|  2018 | fsb                | 2018-10-21  |  2000 |    52   |    35   |             19.54 |         10.26 |   9.28 |                 2.19 |         4.23 | n confere                  | BR036892018                                                                         |
|  2018 | ibope              | 2018-10-27  |  3010 |    47   |    41   |              6.82 |         10.26 |  -3.44 |                 1.82 |        -1.89 | n confere                  | BR029342018                                                                         |
|  2018 | ideia              | 2018-10-10  |  2036 |    48   |    41   |              7.87 |         10.26 |  -2.4  |                 2.21 |        -1.08 | n confere                  | BR096872018                                                                         |
|  2018 | ipespe             | 2018-10-24  |  2000 |    51   |    37   |             15.91 |         10.26 |   5.65 |                 2.21 |         2.56 | n confere                  | BR082832018                                                                         |
|  2018 | mda                | 2018-10-27  |  2002 |    49   |    37   |             13.95 |         10.26 |   3.69 |                 2.21 |         1.67 | n confere                  | BR069332018                                                                         |
|  2018 | parana pesquisas   | 2018-10-25  |  2120 |    53   |    35   |             20.45 |         10.26 |  10.19 |                 2.13 |         4.8  | n confere                  | BR067852018                                                                         |
|  2018 | poderdata          | 2018-10-18  |  4000 |    57   |    31   |             29.55 |         10.26 |  19.28 |                 1.51 |        12.77 | n confere                  | BR088522018                                                                         |
|  2018 | real time big data | 2018-10-24  |  5000 |    49   |    38   |             12.64 |         10.26 |   2.38 |                 1.4  |         1.7  | n confere                  | BR089802018                                                                         |
|  2022 | atlasintel         | 2022-10-29  |  7500 |    52.4 |    45.7 |              6.83 |          1.8  |   5.02 |                 1.15 |         4.36 | n confere                  | BR048382022                                                                         |
|  2022 | datafolha          | 2022-10-29  |  8308 |    49   |    45   |              4.26 |          1.8  |   2.45 |                 1.1  |         2.24 | registro na data, n difere | BR082972022                                                                         |
|  2022 | futura             | 2022-10-26  |  2000 |    46.6 |    47.2 |             -0.64 |          1.8  |  -2.44 |                 2.24 |        -1.09 | n confere                  | BR079032022                                                                         |
|  2022 | gerp               | 2022-10-26  |  2095 |    43   |    47   |             -4.44 |          1.8  |  -6.25 |                 2.18 |        -2.86 | n confere                  | BR054182022                                                                         |
|  2022 | ideia              | 2022-10-19  |  1500 |    50   |    46   |              4.17 |          1.8  |   2.36 |                 2.58 |         0.92 | n confere                  | BR000532022                                                                         |
|  2022 | ipec               | 2022-10-29  |  4272 |    50   |    43   |              7.53 |          1.8  |   5.72 |                 1.53 |         3.75 | n confere                  | BR052562022                                                                         |
|  2022 | ipespe             | 2022-10-24  |  1100 |    50   |    44   |              6.38 |          1.8  |   4.58 |                 3.01 |         1.52 | n confere                  | BR080442022                                                                         |
|  2022 | mda                | 2022-10-28  |  2002 |    46.9 |    44.9 |              2.18 |          1.8  |   0.37 |                 2.23 |         0.17 | n confere                  | BR018202022                                                                         |
|  2022 | parana pesquisas   | 2022-10-28  |  2400 |    47.1 |    46.3 |              0.86 |          1.8  |  -0.95 |                 2.04 |        -0.46 | n confere                  | BR095732022                                                                         |
|  2022 | poderdata          | 2022-10-25  |  5000 |    49   |    44   |              5.38 |          1.8  |   3.57 |                 1.41 |         2.53 | n confere                  | BR011592022                                                                         |
|  2022 | quaest             | 2022-10-29  |  2000 |    45   |    42   |              3.45 |          1.8  |   1.64 |                 2.23 |         0.74 | n confere                  | BR057652022                                                                         |
|  2026 | alfa               | 2026-10-22  |  2700 |    49.9 |    46   |              4.07 |         -3.57 |   7.64 |                 1.92 |         3.97 | registro na data, n difere | BR084962026                                                                         |
|  2026 | atlasintel         | 2026-10-23  |  4990 |    49.9 |    48.4 |              1.53 |         -3.57 |   5.1  |                 1.42 |         3.6  | registro na data, n difere | BR088482026;BR063802026;BR055812026;BR003392026;BR009572026;BR094992026;BR040622026 |
|  2026 | colectta           | 2026-10-23  |  3000 |    46   |    46.5 |             -0.54 |         -3.57 |   3.03 |                 1.83 |         1.66 | n confere                  | BR056012026                                                                         |
|  2026 | datafolha          | 2026-10-24  |  4050 |    48   |    47   |              1.05 |         -3.57 |   4.62 |                 1.57 |         2.94 | n confere                  | BR095402026                                                                         |
|  2026 | datatrends         | 2026-10-21  |  2000 |    50   |    46   |              4.17 |         -3.57 |   7.74 |                 2.23 |         3.46 | n confere                  | BR033652026                                                                         |
|  2026 | futura             | 2026-10-24  |  2000 |    48.2 |    47.9 |              0.31 |         -3.57 |   3.88 |                 2.24 |         1.74 | não localizado             |                                                                                     |
|  2026 | gerp               | 2026-10-24  |  2400 |    49   |    46   |              3.16 |         -3.57 |   6.73 |                 2.04 |         3.3  | n confere                  | BR093272026                                                                         |
|  2026 | ideia              | 2026-10-19  |  1500 |    48   |    46   |              2.13 |         -3.57 |   5.7  |                 2.58 |         2.21 | n confere                  | BR082512026                                                                         |
|  2026 | indexa             | 2026-10-21  |  2000 |    45.2 |    44.1 |              1.23 |         -3.57 |   4.8  |                 2.24 |         2.15 | n confere                  | BR023482026                                                                         |
|  2026 | instituto franca   | 2026-10-23  |  1537 |    45.1 |    43.1 |              2.27 |         -3.57 |   5.84 |                 2.55 |         2.29 | n confere                  | BR048632026                                                                         |
|  2026 | ipespe             | 2026-10-22  |  1500 |    48   |    47   |              1.05 |         -3.57 |   4.62 |                 2.58 |         1.79 | n confere                  | BR043502026                                                                         |
|  2026 | mda                | 2026-10-23  |  2032 |    46.3 |    45   |              1.42 |         -3.57 |   4.99 |                 2.22 |         2.25 | registro na data, n difere | BR021362026                                                                         |
|  2026 | nexus              | 2026-10-24  |  2000 |    47   |    46   |              1.08 |         -3.57 |   4.65 |                 2.24 |         2.08 | n confere                  | BR082342026                                                                         |
|  2026 | palver             | 2026-10-24  |  5000 |    50   |    49   |              1.01 |         -3.57 |   4.58 |                 1.41 |         3.24 | n confere                  | BR017942026                                                                         |
|  2026 | poderdata          | 2026-10-24  |  4000 |    49   |    48   |              1.03 |         -3.57 |   4.6  |                 1.58 |         2.91 | n confere                  | BR028282026                                                                         |
|  2026 | quaest             | 2026-10-24  |  3702 |    46   |    45   |              1.1  |         -3.57 |   4.67 |                 1.64 |         2.84 | n confere                  | BR091582026                                                                         |
|  2026 | real time big data | 2026-10-22  |  2000 |    49   |    45   |              4.26 |         -3.57 |   7.83 |                 2.23 |         3.5  | n confere                  | BR096702026                                                                         |
|  2026 | verita             | 2026-10-23  | 15554 |    49.8 |    47.8 |              2.05 |         -3.57 |   5.62 |                 0.8  |         7.01 | n confere                  | BR031812026                                                                         |
|  2026 | vox brasil         | 2026-10-22  |  2100 |    44.3 |    45.4 |             -1.23 |         -3.57 |   2.34 |                 2.18 |         1.07 | n confere                  | BR032592026                                                                         |

A = mais votado no 1º turno; erro = margem da pesquisa − margem real (positivo superestima A). Fontes: resultados das pesquisas na Wikipedia em inglês com revisões fixadas (D9, fonte secundária); registro do TSE (D5; não existe para 2010); resultados oficiais do TSE (D8; 2026 em D2). Hashes em `data/raw/MANIFEST.csv`. Regras em `docs/desenho_T5_T6.md`. O desvio-padrão amostral cobre só erro amostral sob amostragem aleatória simples; 2010 não tem n na fonte.
