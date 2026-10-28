# T3 — resumo (999 permutações)

| Métrica | Valor |
|---|---|
| I de Moran 2026 | 0.2225 |
| I de Moran 2014–2022 (mín.) | 0.1834 |
| I de Moran 2014–2022 (máx.) | 0.2721 |
| I de 2026 dentro da faixa | True |
| municípios em cluster em 2026 (FDR q=0,05) | 0 |
| dos quais recorrentes (cluster em algum ano anterior) | 0 |
| dos quais exclusivos de 2026 | 0 |
| exclusivos de 2026 por tipo | {} |
| exclusivos de 2026 por UF | {} |
| classificação T3 | Nada anômalo: I de 2026 dentro da faixa de 2014–2022 e nenhum cluster exclusivo de 2026. |

## Modelos por ano

|   ano |   municipios_no_painel |   municipios_no_modelo |   linhas_com_ibge_duplicado | preditores_1t        |   r2_condicional |   dp_residuo |   var_uf | convergiu   |
|------:|-----------------------:|-----------------------:|----------------------------:|:---------------------|-----------------:|-------------:|---------:|:------------|
|  2014 |                   5570 |                   5570 |                           0 | 13 40 45 50          |           0.9761 |       2.8002 |   4.5356 | True        |
|  2018 |                   5570 |                   5570 |                           0 | 12 13 15 17 30 45 51 |           0.9962 |       1.3725 |   2.6146 | True        |
|  2022 |                   5570 |                   5570 |                           0 | 12 13 15 22          |           0.9982 |       0.792  |   0.2335 | True        |
|  2026 |                   5571 |                   5570 |                           0 | 13 14 22 55 70       |           0.9979 |       0.8448 |   0.2401 | True        |

## Moran global e LISA por ano

|   ano |   municipios |   ilhas_ligadas_por_knn |      I |   p_sim |   z_sim |   clusters_fdr |   alto_alto |   baixo_baixo |
|------:|-------------:|------------------------:|-------:|--------:|--------:|---------------:|------------:|--------------:|
|  2014 |         5570 |                       2 | 0.2721 |   0.001 | 33.9824 |              0 |           0 |             0 |
|  2018 |         5570 |                       2 | 0.1959 |   0.001 | 24.5708 |              0 |           0 |             0 |
|  2022 |         5570 |                       2 | 0.1834 |   0.001 | 22.7738 |              0 |           0 |             0 |
|  2026 |         5570 |                       2 | 0.2225 |   0.001 | 27.7886 |              0 |           0 |             0 |

Resíduos do modelo misto municipal (`src/04_model_residuals.py`); pesos de contiguidade queen na malha municipal de 2022 (D7); 999 permutações, semente 20261025; LISA com Benjamini-Hochberg q = 0,05. Fontes: TSE (D2, D8), IBGE (D6, D7); hashes em `data/raw/MANIFEST.csv`. Regras em `docs/desenho_T2_T3.md`. Variável: participação do candidato 13 no 2º turno (referência de sinal); resíduo positivo = acima do previsto para o 13.
