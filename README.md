# Auditoria estatística — 2º turno presidencial 2026

Execução do plano pré-registrado em [`PREREGISTRO.md`](PREREGISTRO.md) (v1.0, redigido em 2026-10-26, cópia byte a byte, SHA-256 `5a8dced7…3e42fd`). O pré-registro foi congelado no commit `abdc482`, antes de qualquer download. Alterações e detalhamentos posteriores estão em [`DESVIOS.md`](DESVIOS.md); resultados afetados por desvio são exploratórios.

## Status por etapa (Seção 8 do pré-registro)

| Etapa | Conteúdo | Status |
|-------|----------|--------|
| 1 | Congelar pré-registro em commit; `DESVIOS.md` vazio | concluída (2026-10-28) |
| 2 | Coleta D1–D8 com manifesto de hashes | concluída (2026-10-28) |
| 3 | T1 — verificação de BUs | concluída na amostra (2026-10-28): linha 1 |
| 4 | T5 e T6 — pesquisas e série histórica | concluída (2026-10-28); T5 com versão exploratória em `DESVIOS.md` |
| 5 | T2 e T3 — pareamento e modelo espacial | concluída (2026-10-28): T3 nada anômalo; T2 com achado formal de causa provável mundana e numericamente irrelevante |
| 6 | T4 — dígitos (completude) | pendente |
| 7 | Consolidação e classificação A/B/C | pendente |
| 8 | Revisão adversarial externa | pendente |
| 9 | Publicação, incluindo testes negativos | pendente |

## Etapa 2 — coleta

Todos os arquivos estão registrados em [`data/raw/MANIFEST.csv`](data/raw/MANIFEST.csv) (URL, data/hora UTC, bytes, SHA-256). `src/00_manifesto.py` confere `data/raw` contra o manifesto; na última execução: 17.611 arquivos, 0 divergências. Resumo por fonte em [`output/tables/coleta_resumo_por_fonte.csv`](output/tables/coleta_resumo_por_fonte.csv).

| Fonte | Conteúdo coletado | Origem |
|---|---|---|
| D1 | Configuração de seções do 2º turno (quadro amostral) e `bu.dat` + `vota.vsc` de 6.025 seções sorteadas; especificação oficial do BU/assinatura | resultados.tse.jus.br, tse.jus.br |
| D2 | Votação por seção 2026 (Presidente) e por município/zona | cdn.tse.jus.br |
| D3 | Perfil do eleitorado por seção (27 UFs), por município/zona e por local de votação | cdn.tse.jus.br |
| D4 | Detalhe da apuração por seção 2026; perfil de comparecimento e abstenção | cdn.tse.jus.br |
| D5 | Registro de pesquisas 2014, 2018, 2022, 2026 | cdn.tse.jus.br |
| D6 | Censo 2022: agregados por município e setor (básico, alfabetização, demografia, renda do responsável) | ftp.ibge.gov.br |
| D7 | Malha municipal 2022 e malha de setores censitários 2022 | geoftp.ibge.gov.br |
| D8 | 1989 por UF; 1994–2022 por município/zona; 2014, 2018, 2022 por seção (controles do T3) | cdn.tse.jus.br |
| D9 | Resultados de pesquisas de 2º turno 2010–2026 (revisões fixadas; fonte secundária) | en.wikipedia.org |
| D10 | Eleições presidenciais de França, Chile, Colômbia, Argentina e Peru (revisões fixadas; fonte secundária) | en.wikipedia.org |

Lacunas de disponibilidade (detalhes em `DESVIOS.md`): o portal não tem registro de pesquisas de 2010, e o registro do TSE não traz os resultados das pesquisas; 1989 só existe por UF.

## Etapa 3 — T1 (verificação criptográfica e reconciliação)

Desenho fixado antes do sorteio em [`docs/desenho_amostral_T1.md`](docs/desenho_amostral_T1.md). Amostra estratificada por UF × porte do município: universo de 517.179 seções, 81 estratos, n = 6.025 (semente 20261025). Resumo completo em [`output/tables/t1_resumo.md`](output/tables/t1_resumo.md); resultados por urna em `output/tables/t1_validacao_por_urna.csv` e `output/tables/t1_reconciliacao_por_urna.csv`.

| Métrica | Resultado |
|---|---|
| Seções sorteadas | 6.025 |
| Urnas com BU "Totalizado" verificadas | 5.692 |
| Seções agregadas (votam na urna da seção principal, sem BU próprio) | 205 |
| Seções sem BU "Totalizado" | 128 (127 com índice em estado "Recebido" em 28/10; 1 urna não instalada) |
| Falhas de assinatura | 0 de 5.692 (IC 95% Clopper-Pearson: 0 a 0,065%) |
| Urnas com divergência BU × totalização | 0 de 5.692 (IC 95%: 0 a 0,065%) |
| Votos conferidos | 1.459.681; soma das diferenças absolutas: 0 |
| Certificados das urnas | emitidos por AC UE2020 (2.371), AC UE2022 (2.196) e AC URNA (1.125), todos validados contra as AC raiz publicadas pelo TSE |

**Classificação (critério fixado no T1):** linha 1. Todas as assinaturas válidas e nenhuma divergência; H1 (divergência na contagem) rejeitada **no escopo amostrado**. Com n = 5.692 urnas, o resultado é compatível com uma proporção de urnas divergentes no universo de até 0,065% (limite superior do IC 95%). Não autoriza conclusão sobre urnas específicas não amostradas.

Complemento **exploratório** (fora da classificação, ver `DESVIOS.md`): as 127 seções em estado "Recebido" também foram verificadas. Nenhuma falha de assinatura e nenhuma divergência.

Testes de invariantes em `tests/`: o verificador rejeita BU, assinatura e certificado adulterados, e a reconciliação acusa divergências e ausências injetadas.

Fonte: TSE, arquivos de urna do 2º turno 2026 (pleito 3221) e votação por seção 2026 (`votacao_secao_2026_BR.zip`); IDs e hashes em `data/raw/MANIFEST.csv`. Estimativa amostral.

## Etapa 4 — T5 (pesquisas) e T6 (série histórica de reversões)

Fontes e regras fixadas antes da coleta em [`docs/desenho_T5_T6.md`](docs/desenho_T5_T6.md). Os resultados das pesquisas (D9) e os 2ºs turnos de outros países (D10) vêm da Wikipedia em inglês, com revisões fixadas e SHA-256 no manifesto. **D9 e D10 são fontes secundárias.**

### T6 — reversões de 2º turno

Resumo completo em [`output/tables/t6_resumo.md`](output/tables/t6_resumo.md); casos em `output/tables/t6_casos.csv`.

| Métrica | Resultado |
|---|---|
| Base (sem o caso Brasil 2026) | 42 segundos turnos: Brasil 7, França 11, Chile 7, Colômbia 7, Peru 8, Argentina 2 |
| Reversões na base | 12 de 42 |
| Brasil 1989–2022 | 0 reversões em 7; regra de Laplace 11,1%; limite superior do IC 95%: 42,9% (regra de três) e 41,0% (Clopper-Pearson) |
| Margem do 1º turno no Brasil em 2026 | 1,87 p.p. (candidato 22 à frente do 13) |
| P(reversão) dada essa margem, regressão logística | 48,7% (IC 95%: 27,0% a 70,9%) |
| Verificação: os 10 casos de margem mais próxima (0,45 a 3,02 p.p.) | 5 reversões em 10 (IC 95%: 18,7% a 81,3%) |

No 2º turno de 2026 houve reversão: o candidato 13 venceu por 3,57 p.p. na soma dos dois. Na base combinada, essa margem estreita no 1º turno corresponde a uma probabilidade estimada de reversão próxima de 50%. Os sete casos brasileiros anteriores tiveram margens de 5,2 a 23,2 p.p. Conforme o plano, nenhuma improbabilidade foi calculada para o resultado observado.

### T5 — desempenho das pesquisas

Resumo completo em [`output/tables/t5_resumo.md`](output/tables/t5_resumo.md). Há duas versões. A **regra fixada** é a confirmatória. A versão **entre turnos** é exploratória: ela corrige um defeito da regra fixada, que deixava entrar como "finais" confrontos diretos anteriores ao 1º turno (ver `DESVIOS.md`). Os números de 2026 são iguais nas duas versões.

| Métrica (2026) | Resultado |
|---|---|
| Pesquisas finais de 2º turno (institutos) | 19 |
| Erro na margem (pesquisa − real; positivo superestima o candidato 22, mais votado no 1º turno) | de +2,34 a +7,83 p.p.; média +5,21 p.p.; todos no mesmo sentido |
| Erro em desvios-padrão amostrais da margem | de 1,1 a 7,0 |
| Critério do plano: erro dentro do maior erro histórico do mesmo instituto | 2 de 10 institutos com histórico (Ipespe, PoderData); 8 fora; 9 sem histórico |
| Erro absoluto de 2026 na distribuição combinada de 2010–2022 | percentis 28 a 81 (regra fixada) e 32 a 89 (entre turnos): dentro da faixa histórica |
| Erro médio por eleição (entre turnos) | 2010: +0,8; 2014: +1,1; 2018: +4,9; 2022: +1,5; 2026: +5,2 p.p. |
| Variância dos erros explicada pela eleição (entre turnos) | η² = 0,21 (ANOVA p = 0,037): erros de institutos diferentes na mesma eleição tendem a se mover juntos |

Leitura pelo critério do plano: para 8 dos 10 institutos com histórico, o erro de 2026 ficou acima do maior erro anterior do próprio instituto. Por isso o T5 **não refuta**, pelo critério por instituto, a alegação de improbabilidade estatística. Esse critério, porém, depende de séries curtas, com 1 a 4 eleições por instituto. Na distribuição combinada, os erros de 2026 ficam dentro da faixa observada em 2010–2022. O erro médio de 2026 tem a mesma ordem de grandeza do de 2018. Os erros de todos os institutos foram na mesma direção, o que é compatível com erro correlacionado entre institutos. O plano atribui ao T5 poder probatório baixo para fraude: este resultado trata do desempenho das pesquisas, não da apuração.

Limitações: os percentuais vêm de compilação secundária. Das 51 pesquisas finais da regra fixada, o n confere com o registro do TSE em 36; em 8, há registro na mesma data com n diferente; em 3, o registro não foi localizado; as 4 de 2010 não têm registro no portal. Alguns valores históricos extremos merecem conferência na fonte primária antes de qualquer publicação, por exemplo DataPoder360 em 2018 (erro de +19,3 p.p.).

## Etapa 5 — T2 (seções entre turnos) e T3 (modelo espacial)

Desenho fixado antes de montar as bases em [`docs/desenho_T2_T3.md`](docs/desenho_T2_T3.md). Os ajustes posteriores estão em `DESVIOS.md`: ponte TSE→IBGE por nome e espacial, correção do código da variável de alfabetização e duas sensibilidades exploratórias. Candidato de referência para o sinal dos resíduos: 13, o único presente nos quatro 2ºs turnos comparados.

### T3 — resíduos espaciais por município (2014, 2018, 2022, 2026)

Resumo em [`output/tables/t3_resumo.md`](output/tables/t3_resumo.md).

| Métrica | Resultado |
|---|---|
| Modelo misto (intercepto de UF), 5.570 municípios por ano | R² condicional de 0,976 a 0,998; todos convergiram |
| I de Moran dos resíduos | 2014: 0,272; 2018: 0,196; 2022: 0,183; **2026: 0,222** |
| I de 2026 dentro da faixa de 2014–2022 | sim |
| Clusters LISA após FDR (999 permutações) | 0 em todos os anos |
| Sensibilidade exploratória, 9.999 permutações | 2014: 10; 2018: 0; 2022: 10; **2026: 0** |

**Classificação (critério fixado no T3): nada anômalo.** A autocorrelação espacial dos resíduos de 2026 está dentro da faixa das três eleições de controle, e não há cluster exclusivo de 2026. Com 999 permutações o teste local tinha resolução insuficiente para o FDR. Na sensibilidade com 9.999, os anos de controle mostram clusters e 2026 continua sem nenhum.

### T2 — seções pareadas entre turnos (2026)

Resumo em [`output/tables/t2_resumo.md`](output/tables/t2_resumo.md); seções listadas em `output/tables/t2_secoes_anomalas.csv`.

| Métrica | Confirmatório | Ponderado pelo tamanho da seção (exploratório) |
|---|---|---|
| Seções no modelo | 497.508 | 497.508 |
| Seções anômalas (FDR q = 0,05) | 461 (0,09%) | 52 (0,01%) |
| Direção (acima/abaixo do previsto para o 13) | 268 / 193 (p = 0,0006) | 34 / 18 (p = 0,036) |
| Agrupamento: pares vizinhos anômalos, observado contra esperado | 83 contra 2,1 (p = 0,001) | 18 contra 0,03 (p = 0,001) |
| Anômalas em seções pequenas (até 207 votos, quintil inferior) | 405 | 27 |
| Anômalas em locais indígenas (aldeia, escola indígena) | 31 | 11 |
| Votos válidos somados nas seções anômalas | 55.378 (1,26% da margem nacional) | 10.563 (0,24% da margem nacional) |

**Classificação (critério fixado no T2):** os três critérios formais são atendidos (agrupamento, direção e resíduo condicional ao perfil). Pelo plano, isso é um **achado a localizar**, com a hipótese padrão de erro de especificação do modelo. A investigação aponta nessa direção:
- 88% das seções anômalas estão entre as menores, onde a proporção varia muito mais e o modelo sem ponderação trata todas com a mesma variância;
- locais indígenas aparecem 40 vezes acima da média, o que é compatível com voto comunitário;
- na versão ponderada, o único agrupamento com 3 ou mais seções é um mesmo local em São Paulo (5 seções do Colégio Equipe, todas abaixo do previsto para o 13), um efeito de composição local que o perfil por seção não capta.

O conjunto é **numericamente irrelevante** para o resultado (Seção 5 do plano): mesmo que todos os votos dessas seções mudassem de lado, a margem nacional de 4.430.191 votos não seria alcançada. A classificação final A/B/C fica para a Etapa 7.

## Análise exploratória — dimensão da virada entre turnos

Pedida pelo usuário e registrada em `DESVIOS.md`; **não entra na classificação**. Não calcula a improbabilidade do resultado observado, o que o plano proíbe (Seção 6). Dimensiona a virada contra a experiência histórica. Detalhes em [`output/tables/virada_EXPLORATORIO.md`](output/tables/virada_EXPLORATORIO.md).

| Métrica | Resultado |
|---|---|
| Deslocamento da margem entre turnos, 2026 (margens entre os dois finalistas) | −5,6 p.p. para o líder do 1º turno (candidato 22) |
| 2ºs turnos da base (42) com deslocamento igual ou maior contra o líder | 29 |
| Deslocamentos brasileiros contra o líder | 1989: −21,8; 2002: −10,8; 2010: −5,9; 2014: −8,2; 2018: −12,0; 2022: −3,9 (2006: +13,9) |
| Parcela dos votos novos dos finalistas que o 2º colocado precisava obter para virar | 2026: **57,9%**, a menor da série (anteriores: 63% a 89%) |
| Parcela efetivamente obtida pelo 2º colocado | 2026: **73,6%**, a maior da série (2022: 69,8%; 2018: 64,8%; 2014: 60,0%; 1989: 57,3%) |
| Origem dos 14,1 milhões de votos novos dos finalistas | 9,3 milhões dos demais candidatos do 1º turno; 3,0 milhões de comparecimento a mais; 1,8 milhão de brancos e nulos a menos |
| Divisão desses votos | 10,4 milhões para o 13; 3,7 milhões para o 22 |

Leitura descritiva:
- Em 2026, a virada exigia menos do que em qualquer 2º turno brasileiro anterior, porque a vantagem do 1º turno era a menor da série.
- O 2º colocado teve o melhor desempenho da série entre os votos novos (73,6%), cerca de 4 p.p. acima de 2022.
- A perda de margem do líder (−5,6 p.p.) foi menor que a de 29 dos 42 segundos turnos da base.
- O ponto fora do padrão não é a virada em si. É o tamanho da captação dos votos novos, combinado com o erro das pesquisas no mesmo sentido (T5).
- A decomposição é contábil e agregada: não identifica de quem vieram os votos individualmente (falácia ecológica).

## Reprodução

```bash
python -m venv .venv && .venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python src/01_download.py lote
.venv/Scripts/python src/01_download.py bu-quadro
.venv/Scripts/python src/02_validate_bu.py sorteia
.venv/Scripts/python src/01_download.py bu-amostra
.venv/Scripts/python src/01_download.py bu-recebidos
.venv/Scripts/python src/00_manifesto.py
.venv/Scripts/python src/02_validate_bu.py valida
.venv/Scripts/python src/02_validate_bu.py valida-recebidos
.venv/Scripts/python src/02_validate_bu.py reconcilia
.venv/Scripts/python src/01_download.py wiki
.venv/Scripts/python src/08_historical.py
.venv/Scripts/python src/07_polls.py
.venv/Scripts/python src/t23_bases.py
.venv/Scripts/python src/03_pair_sections.py
.venv/Scripts/python src/04_model_residuals.py
.venv/Scripts/python src/05_spatial.py
.venv/Scripts/python src/05_spatial.py --sensibilidade
.venv/Scripts/python src/09_virada_exploratoria.py
.venv/Scripts/python -m pytest tests
```

A especificação oficial (`data/raw/tse_doc/formato-arquivos-de-bu-rdv-e-assinatura-digital.zip`) precisa ser baixada por navegador, porque tse.jus.br responde 403 a clientes de linha de comando. Depois disso, ela é extraída em `data/processed/tse_spec/`.

## Espaço em disco

`data/raw` ocupa cerca de 8,8 GB. Os brutos não ficam no git: o manifesto permite baixá-los de novo e conferir os hashes. Quando o trabalho terminar, os brutos podem ser apagados.
