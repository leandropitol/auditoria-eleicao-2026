# T2 e T3: desenho e regras operacionais

**Status:** fixado em 2026-10-28, antes de montar as bases e de ajustar qualquer modelo. Detalha as seções T2 e T3 do `PREREGISTRO.md`; o registro correspondente está em `DESVIOS.md`.

O que já foi visto: os totais nacionais por candidato (T1, T5, T6) e os cabeçalhos de colunas de D2, D3, D4, D6 e D7. Nenhum resultado por município ou por seção foi tabulado.

## Elementos comuns

- **Candidato de referência:** o de número 13, único presente nos quatro 2ºs turnos comparados (2014, 2018, 2022 e 2026). A escolha só fixa o sinal dos resíduos; o I de Moran não depende dele. A variável resposta é `y = 100 · v13 / (v13 + v_outro)` no 2º turno.
- **Exterior (UF = ZZ):** fica fora de T2 e T3, porque não tem geometria nem perfil por seção.
- **Ponte entre códigos de município TSE e IBGE:** os locais de votação de 2026 (D3, `eleitorado_local_votacao_2026`, com latitude e longitude) são cruzados com a malha municipal de 2022 (D7). Cada município do TSE recebe o código IBGE onde caem mais locais. Reporto a concordância e listo os municípios em que menos de 90% dos locais caem no mesmo polígono. Como conferência, comparo também os nomes normalizados dos municípios no TSE e no IBGE.
- **Semente aleatória:** 20261025 em todas as permutações.

## T2: transferência entre turnos, por seção (2026)

1. **Pareamento:** seções presentes nos dois turnos em D2 (cargo Presidente), pela chave UF + município + zona + seção. Reporto quantas ficaram sem par.
2. **Variáveis por seção:**
   - 1º turno: participação de cada candidato com ≥ 1% nacional nos votos nominais, mais a dos "demais" como categoria omitida;
   - abstenção no 1º turno (`QT_ABSTENCOES / QT_APTOS`, D4) e brancos + nulos no 1º turno (`/ QT_COMPARECIMENTO`);
   - Δ comparecimento (2º − 1º turno, `/ QT_APTOS`) e Δ brancos + nulos;
   - perfil do eleitorado da seção (D3): proporção feminina; faixas etárias 16–24, 25–44, 45–59 e 60–69, com 70+ omitida; escolaridade superior (completo ou incompleto) e ensino médio (completo ou incompleto), com fundamental ou menos omitida.
3. **Modelo:** regressão linear de `y` sobre essas variáveis, com efeito fixo de município (transformação dentro do município). O efeito fixo absorve tudo o que é municipal, inclusive as covariáveis de D6. A seção é comparada com as do mesmo município.
4. **Seção anômala:** resíduo padronizado `z = e / dp(e)`, com p-valor bilateral pela normal e correção de Benjamini-Hochberg com q = 0,05 sobre todas as seções.
5. **Critérios (todos necessários para constituir achado):**
   - **(a) agrupamento espacial:** cada seção recebe as coordenadas do seu local de votação, e sem coordenada válida fica fora deste critério, com contagem reportada. Monto um grafo dos 5 vizinhos mais próximos. A estatística é o número de pares de vizinhos em que as duas seções são anômalas, comparado com 999 permutações dos rótulos (p unilateral, α = 0,05). Componentes conexos com ≥ 3 seções anômalas são listados.
   - **(b) direção:** teste binomial bilateral do sinal dos resíduos das seções anômalas (α = 0,05).
   - **(c) sem explicação pelas covariáveis:** atendido por construção, já que o resíduo é condicional ao perfil de D3 e ao município.
   - Se faltar qualquer um dos três, o resultado é heterogeneidade regional.
6. **Falácia ecológica:** nenhuma taxa de transferência individual é estimada ou reportada. Os coeficientes descrevem associações entre agregados.

## T3: modelo preditivo e resíduos espaciais, por município (2014, 2018, 2022, 2026)

1. **Unidade:** município (código IBGE pela ponte TSE→IBGE). A especificação é a mesma para os quatro anos.
2. **Preditores:**
   - 1º turno do mesmo ano: participação de cada candidato com ≥ 1% nacional nos votos nominais, com "demais" omitida;
   - renda: log do rendimento nominal médio mensal dos responsáveis (Censo 2022, `V06004`);
   - escolaridade: taxa de alfabetização de 15 anos ou mais (Censo 2022: alfabetizados, `V00644`–`V00656`, divididos pela população de 15+, `V01034`–`V01041`);
   - urbanização: proporção da população em setores de situação urbana (Censo 2022, setores, `SITUACAO` e `v0001`);
   - faixa etária: proporção de 60+ na população de 15+ (Censo 2022, `V01040` + `V01041`).
   - As covariáveis do Censo 2022 valem para todos os anos, como aproximação de características estruturais.
3. **Especificação:** modelo linear misto com intercepto aleatório de UF (`statsmodels.MixedLM`, REML). Variáveis contínuas padronizadas dentro de cada ano.
4. **Pesos espaciais:** contiguidade *queen* na malha municipal de 2022, padronizada por linha. Municípios sem vizinho recebem o vizinho mais próximo pelo centroide.
5. **I de Moran global** dos resíduos de cada ano, com 999 permutações.
6. **LISA** (Moran local) dos resíduos de cada ano, com 999 permutações condicionais. Um município está em cluster se o p-valor, após Benjamini-Hochberg com q = 0,05 sobre todos os municípios do ano, for ≤ 0,05 e o quadrante for alto-alto ou baixo-baixo.
7. **Critérios (Seção 3/T3 do pré-registro):**
   - **I de 2026 dentro da faixa:** entre o mínimo e o máximo dos I de 2014, 2018 e 2022. Resultado: nada anômalo.
   - **Cluster recorrente:** município em cluster em 2026 que também esteve em cluster, de qualquer tipo, em pelo menos um dos anos anteriores. É fenômeno regional estrutural. Também reporto a concordância de tipo (alto-alto ou baixo-baixo).
   - **Cluster exclusivo de 2026:** em cluster só em 2026. É **achado** se o conjunto exclusivo for direcional, isto é, se a proporção de um mesmo tipo for ≥ 80% (por exemplo, todos baixo-baixo). Com o resíduo condicional às covariáveis, "sem correlato demográfico" vale por construção. Os municípios são listados.
   - Hipótese padrão para qualquer achado: erro de especificação do modelo.
8. **Limitação registrada:** o pré-registro descreve um modelo com seção aninhada em município. Para 2014–2022 não foram coletadas coordenadas nem perfil por seção, então a comparação com os anos anteriores (o grupo de controle) só é viável no nível municipal. A análise por seção fica restrita ao T2 de 2026.
