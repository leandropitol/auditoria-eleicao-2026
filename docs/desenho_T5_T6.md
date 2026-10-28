# T5 e T6: fontes e regras operacionais

**Status:** fixado em 2026-10-28, **antes** de baixar ou abrir qualquer resultado de pesquisa ou de eleição estrangeira. O documento detalha o que as seções T5 e T6 do `PREREGISTRO.md` deixam em aberto e não acrescenta métricas. Registro correspondente em `DESVIOS.md`.

Já visto neste momento: os resultados oficiais brasileiros que aparecem no T1 (só os números dos candidatos, 13 e 22) e a estrutura de colunas de D5. Nenhum percentual de pesquisa, nenhuma margem de 1º turno e nenhum dado estrangeiro foi aberto.

## Fontes (escolhidas pelo usuário em 2026-10-28)

- **T5, resultados das pesquisas:** páginas da Wikipedia em inglês "Opinion polling for the {ano} Brazilian presidential election" (2010, 2014, 2018, 2022, 2026). Cada página é fixada pelo ID de revisão vigente no download, e o HTML dessa revisão é salvo em `data/raw/D9/` com SHA-256 no manifesto. É uma fonte secundária, que compila os relatórios dos institutos. Para 2014–2026, cada pesquisa final é cruzada com o registro do TSE (D5) pelo instituto, pela data de fim de campo e pelo tamanho de amostra. Para 2010 não existe registro no portal.
- **T5, resultado oficial:** TSE. Para 2010–2022, D8 `votacao_candidato_munzona_{ano}.zip`. Para 2026, D2 `votacao_secao_2026_BR.zip`.
- **T6, Brasil:** TSE, D8 (1989 por UF; 2002–2022 por município/zona). Para 2026, D2.
- **T6, outros países:** páginas da Wikipedia em inglês "{ano} {país} presidential election" de todas as eleições presidenciais com 2º turno realizado até 2026-10-28 na França (desde 1965), no Chile (desde 1989), na Colômbia (desde 1994), na Argentina (desde 1995) e no Peru (desde 1990). As páginas são fixadas por ID de revisão, com o HTML salvo em `data/raw/D10/` e SHA-256 no manifesto. Também é fonte secundária.

## T5: regras

1. **Escopo:** 2º turno presidencial de 2010, 2014, 2018, 2022 e 2026; pesquisas nacionais.
2. **Pesquisa final de um instituto numa eleição:** a pesquisa do instituto com a data de fim de campo mais recente, desde que essa data seja anterior ao dia do 2º turno. Em caso de empate, vale a de maior amostra; persistindo o empate, a primeira listada na fonte.
3. **Candidato A:** o mais votado no 1º turno daquela eleição. **Candidato B:** o outro participante do 2º turno.
4. **Margem da pesquisa:** `100 · (A − B) / (A + B)`, em pontos percentuais da soma dos dois candidatos. Equivale à margem em votos válidos e independe de a pesquisa publicar votos totais ou válidos.
5. **Margem real:** a mesma fórmula sobre os votos oficiais de A e B no 2º turno.
6. **Erro da pesquisa:** margem da pesquisa − margem real, em p.p. O sinal positivo indica que a pesquisa superestimou A.
7. **Erro amostral de referência:** desvio-padrão da margem sob amostragem aleatória simples, `200 · sqrt(p(1−p)/n)`, com p = participação de A na soma A+B segundo a pesquisa e n = amostra declarada. O plano chama isso de "aproximadamente 2× o sigma do percentual individual".
8. **Critério do plano:** o erro de 2026 de um instituto está "dentro da distribuição histórica do mesmo instituto" se |erro 2026| ≤ maior |erro| desse instituto em 2010–2022. Institutos sem histórico são comparados à distribuição combinada de |erro| de todos os institutos em 2010–2022 e recebem o percentil correspondente. O resultado é reportado instituto a instituto.
9. **Correlação entre institutos:** para cada eleição, erro médio e desvio-padrão entre institutos. Também a proporção da variância dos erros explicada pela eleição (ANOVA de um fator, 2010–2026) e a concordância de sinal entre pares de institutos na mesma eleição.
10. **Nomes de institutos:** a padronização entre anos (por exemplo, Ibope → Ipec) usa um dicionário explícito em código, com a justificativa de cada fusão.

## T6: regras

1. **Base:** todo 2º turno presidencial realizado até 2026-10-28 nos seis países. Cada caso registra a margem do 1º turno, `(1º − 2º colocado)` em % dos votos válidos, e se houve reversão, isto é, se o 2º colocado do 1º turno venceu o 2º turno.
2. **O caso de 2026 entra na tabela, mas fica fora de todas as estimativas**, para que o resultado observado não seja usado para avaliar a si mesmo.
3. **Brasil isolado (1989–2022):** contagem de reversões; regra de sucessão de Laplace `(k+1)/(n+2)`; limite superior do IC 95%. Com k = 0, o limite vem da regra de três (`3/n`) e também do Clopper-Pearson exato. Os dois são reportados.
4. **Probabilidade condicional à margem (base combinada, sem 2026):** regressão logística de reversão sobre a margem do 1º turno (p.p.), com efeito fixo de país omitido por falta de n. Reporta a probabilidade prevista na margem do 1º turno de 2026, com IC 95% pelo método delta na escala logit. Como verificação, reporta também a proporção de reversões entre os 10 casos de margem mais próxima da de 2026, com IC 95% Clopper-Pearson.
5. **Atirador texano:** nenhuma improbabilidade é calculada para o resultado de 2026 depois de observado. O T6 só estima a probabilidade de reversão dada a margem do 1º turno.
