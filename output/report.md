# Auditoria estatística — 2º turno presidencial 2026: relatório consolidado

Plano pré-registrado em `PREREGISTRO.md` (commit `abdc482`, antes de qualquer download). Desvios em `DESVIOS.md`; resultados afetados por desvio são exploratórios. Candidatos identificados pelo número de urna. Linguagem descritiva; a interpretação está na Seção 5, separada dos resultados.

## 1. Pergunta

O resultado do 2º turno presidencial de 2026 é consistente com o processo eleitoral tal como documentado nos registros públicos, ou há anomalias localizadas e não explicáveis por fatores demográficos, políticos e de erro amostral conhecidos?

## 2. Resultados — todos os testes, inclusive os negativos

| teste   | status        | o que mede                                                   | resultado                                                                    | leitura                                   |
|:--------|:--------------|:-------------------------------------------------------------|:-----------------------------------------------------------------------------|:------------------------------------------|
| T1      | confirmatório | Assinatura digital dos BUs (amostra estratificada)           | 0 falhas em 5.692 urnas                                                      | negativo (sem anomalia)                   |
| T1      | confirmatório | Reconciliação BU × totalização                               | 0 divergências; 1.459.681 votos conferidos                                   | negativo (sem anomalia)                   |
| T1      | exploratório  | BUs em estado Recebido                                       | 0 falhas, 0 divergências                                                     | negativo                                  |
| T2      | confirmatório | Seções com deslocamento atípico entre turnos                 | 461 seções; agrupadas e direcionais; 55.378 votos (1,26% da margem nacional) | achado formal, não material               |
| T2      | exploratório  | Idem, ponderado pelo tamanho da seção                        | 52 seções; 0,24% da margem                                                   | achado formal, não material               |
| T3      | confirmatório | Autocorrelação espacial dos resíduos municipais              | I 2026 = 0,222; faixa 2014–2022 = 0,183–0,272; clusters 2026: 0              | negativo (dentro da faixa)                |
| T3      | exploratório  | LISA com 9.999 permutações                                   | clusters 2026: 0; controles: 2014: 10, 2018: 0, 2022: 10                     | negativo                                  |
| T4      | completude    | Benford de 2º dígito, último dígito, múltiplos de 5 e 10     | MAD 2BL 2026 = 0.0091–0.0102 (controles 0.0030–0.0103)                       | não é evidência (pré-registro)            |
| T5      | confirmatório | Erro das pesquisas finais contra o histórico do instituto    | 2 de 10 institutos dentro do próprio máximo; erro médio 2026 = 5,21 p.p.     | fora do padrão por instituto              |
| T5      | exploratório  | Idem, só pesquisas entre os turnos                           | erro médio 2026 = 5,21 p.p.; η² por eleição = 0.211                          | erro correlacionado entre institutos      |
| T6      | confirmatório | Probabilidade de reversão dada a margem do 1º turno          | 48,7% (IC 95% (0.2698, 0.7094)); base: 12 reversões em 42 casos              | reversão compatível com a margem          |
| Virada  | exploratório  | Parcela dos votos novos necessária e obtida pelo 2º colocado | necessária 57,9%, obtida 73,6%                                               | menor exigência e maior captação da série |

## 3. Correção de múltiplos testes (família confirmatória, Benjamini-Hochberg q = 0,05)

| teste   | hipótese                                              |        p | rejeita_BH_q005   |     p_BH |
|:--------|:------------------------------------------------------|---------:|:------------------|---------:|
| T2      | direção das seções anômalas (binomial)                | 0.000554 | True              | 0.001667 |
| T2      | agrupamento espacial das seções anômalas (permutação) | 0.001    | True              | 0.001667 |
| T3      | I de Moran global dos resíduos de 2026 (permutação)   | 0.001    | True              | 0.001667 |
| T5      | erros das pesquisas variam por eleição (ANOVA)        | 0.4451   | False             | 0.4451   |
| T6      | margem do 1º turno prediz reversão (logística)        | 0.03498  | True              | 0.043725 |

As classificações seguem os critérios fixados em cada teste; a correção acima é reportada ao lado, conforme `docs/desenho_T4_consolidacao.md`. O I de Moran global ser significativo é esperado (vizinhos votam parecido) e ocorre em todos os anos; o critério do T3 é a comparação com a faixa de 2014–2022.

## 4. Classificação (Seção 5.1 do pré-registro)

**Desfecho B — anomalia com causa mundana.**

- Não é C: o único achado formal (T2) envolve 55.378 votos, 1,26% da margem entre os finalistas sem o exterior (4.388.114 votos; margem oficial com o exterior: 4.430.191); não é material no sentido da Seção 5 (capaz de alterar o resultado nacional).
- Não é A: T5: só 2 de 10 institutos com histórico ficaram dentro do próprio maior erro anterior; T2: critérios formais de achado atendidos (seções anômalas agrupadas e direcionais).
- É B: o achado do T2 está localizado e concentra-se em seções pequenas e locais indígenas, padrão compatível com erro de especificação do modelo (heterocedasticidade e voto comunitário); o desvio do T5 é de desempenho das pesquisas, não da apuração.
- Nenhum desfecho autoriza conclusão nacional por raciocínio agregado.

## 5. Interpretação (separada dos resultados)

- **Contagem.** O teste de maior poder probatório (T1) não encontrou falha de assinatura nem divergência entre boletins de urna e totalização na amostra. No escopo amostrado, a hipótese de fraude na contagem (H1) fica rejeitada; o limite superior do IC 95% para a proporção de urnas divergentes no universo é 0,065%.
- **Padrão espacial.** Os resíduos municipais de 2026 têm autocorrelação dentro da faixa das três eleições anteriores e nenhum cluster local exclusivo (T3). As seções atípicas do T2 são poucas, pequenas, concentradas em contextos específicos e numericamente irrelevantes para o resultado.
- **Improbabilidade.** A reversão ocorreu com a menor vantagem de 1º turno da série brasileira; para essa margem, a base de 2ºs turnos indica probabilidade de reversão da ordem de metade (T6). O que destoa do histórico é a magnitude: o 2º colocado obteve a maior parcela de votos novos da série (exploratório) e as pesquisas finais superestimaram o líder do 1º turno em todos os institutos (T5), com erro médio comparável ao de 2018.
- **Hipótese padrão.** Onde há resultado não explicado (T2), a hipótese padrão é erro de especificação do modelo; nada nos dados aponta urnas específicas com divergência de contagem.

## 6. Limitações

- T1 é amostral (n = 5.692 urnas); não cobre urnas não sorteadas além do intervalo de confiança.
- T5 e T6 usam fontes secundárias (Wikipedia com revisões fixadas) para percentuais de pesquisas e para eleições de outros países; valores extremos devem ser conferidos nas fontes primárias antes de publicação.
- T3 foi feito por município (o plano previa seção aninhada), por falta de dados por seção para os anos de controle.
- O critério do T5 por instituto apoia-se em 1 a 4 eleições por instituto.
- Relatos de coação (H3) não entram como métrica (Seção 4 do pré-registro).

## 7. Próximas etapas do plano

- Etapa 8: revisão adversarial externa do código e dos dados por alguém que não compartilhe a expectativa inicial.
- Etapa 9: publicação, incluindo os testes negativos.

Fontes: TSE (D1–D5, D8), IBGE (D6, D7), Wikipedia com revisões fixadas (D9, D10); hashes, URLs e datas em `data/raw/MANIFEST.csv`. Tabelas de origem em `output/tables/`.
