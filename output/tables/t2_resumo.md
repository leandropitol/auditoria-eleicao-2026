# T2 — resumo

| Base | Valor |
|---|---|
| seções na base (exceto exterior) | 497897 |
| sem 2º turno | 0 |
| sem 1º turno | 0 |
| sem perfil do eleitorado (D3) | 389 |
| seções pareadas e completas (modelo) | 497508 |
| seções com coordenadas válidas (critério a) | 495789 |

## A. Confirmatório (regras de `docs/desenho_T2_T3.md`)

| Métrica | Valor |
|---|---|
| seções anômalas (FDR q=0,05) | 461 |
| proporção anômala | 0.0009266 |
| anômalas com resíduo positivo (acima do previsto para o 13) | 268 |
| anômalas com resíduo negativo | 193 |
| (b) p binomial de direção | 0.0005536 |
| (a) pares vizinhos anômalo-anômalo: observado | 83 |
| (a) pares vizinhos anômalo-anômalo: esperado sob permutação | 2.097 |
| (a) p de permutação (unilateral) | 0.001 |
| componentes com ≥ 3 seções anômalas | 6 |
| anômalas no quintil inferior de tamanho (até 207 votos) | 405 |
| anômalas em locais com nome indígena (aldeia, escola indígena) | 31 |
| votos válidos (2º turno) somados nas seções anômalas | 55378 |
| idem, em % da margem nacional entre os finalistas (exterior excluído) | 1.262 |
| classificação T2 | Critérios (a), (b) e (c) atendidos: seções anômalas agrupadas e direcionais, condicionais ao perfil e ao município. Achado a localizar (componentes listados); hipótese padrão: erro de especificação do modelo. |

### Componentes com ≥ 3 seções anômalas

|   componente |   n_secoes | uf   | nm_mun               |   municipios |   locais | local                                                   |   votos_2t_medio |   z_medio |   z_positivos |
|-------------:|-----------:|:-----|:---------------------|-------------:|---------:|:--------------------------------------------------------|-----------------:|----------:|--------------:|
|          399 |          5 | AC   | CRUZEIRO DO SUL      |            1 |        2 | ESCOLA SÃO FRANCISCO                                    |            93    |      5.22 |             5 |
|       455895 |          5 | SP   | SÃO PAULO            |            1 |        1 | COLÉGIO EQUIPE                                          |           304    |     -5.75 |             0 |
|          156 |          3 | AC   | MARECHAL THAUMATURGO |            1 |        3 | ESCOLA SAO RAIMUNDO                                     |           130    |      5.59 |             3 |
|          685 |          3 | AC   | JORDÃO               |            3 |        3 | ESCOLA DE ENSINO FUNDAMENTAL CORONEL FLORENCIO DA CUNHA |            90.33 |      9.85 |             3 |
|       211044 |          3 | PA   | PORTEL               |            1 |        3 | EMEF CONCEIÇÃO                                          |           106.67 |     -1.21 |             1 |
|       336468 |          3 | RR   | BOA VISTA            |            1 |        3 | ESCOLA MUNICIPAL INDÍGENA TUXAUA ALBINO MORAIS          |           151.67 |      5.34 |             3 |

## B. Sensibilidade exploratória: ponderação pelos votos da seção (DESVIOS.md)

| Métrica | Valor |
|---|---|
| seções anômalas (FDR q=0,05) | 52 |
| proporção anômala | 0.0001045 |
| anômalas com resíduo positivo (acima do previsto para o 13) | 34 |
| anômalas com resíduo negativo | 18 |
| (b) p binomial de direção | 0.03648 |
| (a) pares vizinhos anômalo-anômalo: observado | 18 |
| (a) pares vizinhos anômalo-anômalo: esperado sob permutação | 0.03103 |
| (a) p de permutação (unilateral) | 0.001 |
| componentes com ≥ 3 seções anômalas | 1 |
| anômalas no quintil inferior de tamanho (até 207 votos) | 27 |
| anômalas em locais com nome indígena (aldeia, escola indígena) | 11 |
| votos válidos (2º turno) somados nas seções anômalas | 10563 |
| idem, em % da margem nacional entre os finalistas (exterior excluído) | 0.2406 |
| classificação T2 | Critérios (a), (b) e (c) atendidos: seções anômalas agrupadas e direcionais, condicionais ao perfil e ao município. Achado a localizar (componentes listados); hipótese padrão: erro de especificação do modelo. |

### Componentes com ≥ 3 seções anômalas

|   componente |   n_secoes | uf   | nm_mun    |   municipios |   locais | local          |   votos_2t_medio |   z_medio |   z_positivos |
|-------------:|-----------:|:-----|:----------|-------------:|---------:|:---------------|-----------------:|----------:|--------------:|
|       455929 |          5 | SP   | SÃO PAULO |            1 |        1 | COLÉGIO EQUIPE |              304 |     -6.61 |             0 |

Modelo: participação do candidato 13 no 2º turno (votos nominais dos dois finalistas) sobre o 1º turno da seção, abstenção e brancos/nulos, variações entre turnos e perfil do eleitorado (D3), com efeito fixo de município. Resíduo padronizado; Benjamini-Hochberg q = 0,05. Dado agregado: os coeficientes não descrevem comportamento individual. Fontes: TSE (D2, D3, D4); hashes em `data/raw/MANIFEST.csv`. Regras em `docs/desenho_T2_T3.md`.
