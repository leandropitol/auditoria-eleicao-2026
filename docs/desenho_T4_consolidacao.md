# T4 e Etapa 7: desenho e regras de consolidação

**Status:** fixado em 2026-10-28, antes de calcular qualquer distribuição de dígitos. As classificações de T1, T2, T3, T5 e T6 já são conhecidas; as regras da Etapa 7 abaixo só operacionalizam a Seção 5.1 do pré-registro, sem acrescentar critério novo.

## T4 — dígitos (incluído apenas para completude)

**Advertência do pré-registro, mantida integralmente:** contagens por urna têm faixa estreita e teto rígido. Benford não vale nessas condições e gera falsos positivos com regularidade. **Um desvio em T4, sozinho, não constitui achado e não é reportado como evidência em nenhuma hipótese.**

1. **Dados:** votos de cada finalista do 2º turno presidencial por seção, em 2014, 2018 e 2022 (D8, `votacao_secao_{ano}_BR.zip`) e em 2026 (D2), incluindo o exterior. Os anos anteriores servem de controle (Seção 6 do pré-registro).
2. **Testes por ano e por candidato,** sobre as contagens ≥ 10, para que haja 2º dígito:
   - **Benford de 2º dígito:** qui-quadrado contra a distribuição de Benford do 2º dígito; desvio absoluto médio (MAD); média do 2º dígito (4,187 sob Benford);
   - **último dígito:** qui-quadrado contra a distribuição uniforme; MAD;
   - **múltiplos de 5 e de 10:** proporção de contagens terminadas em 0 ou 5, contra 0,2, e terminadas em 0, contra 0,1, com teste binomial bilateral.
3. **Leitura:** com cerca de 500 mil seções, qualquer desvio mínimo produz p-valor baixíssimo. A comparação relevante é o tamanho do desvio (MAD, proporções) em 2026 contra 2014–2022 com o mesmo procedimento. Todos os valores são reportados.

## Etapa 7 — consolidação

1. **Tabela única** com todos os testes confirmatórios e exploratórios de T1 a T6, incluindo os negativos, cada um com status (confirmatório ou exploratório) e fonte.
2. **Correção de múltiplos testes:** Benjamini-Hochberg com q = 0,05 sobre os p-valores dos testes de hipótese confirmatórios de T2, T3, T5 e T6:
   - T2: direção e agrupamento;
   - T3: Moran global de 2026;
   - T5: ANOVA dos erros por eleição;
   - T6: coeficiente da margem na regressão logística.

   T1 não tem p-valor (contagem exata), e T4 não entra, por ser só de completude. As classificações continuam seguindo os critérios fixados em cada teste; a correção é reportada ao lado.
3. **Classificação (Seção 5.1),** aplicada nesta ordem:
   - **C (anomalia inexplicada):** exige achado material, localizável, direcional, reprodutível e que sobreviva à correção. Material quer dizer capaz de alterar o resultado nacional (Seção 5): o total de votos envolvidos precisa ser ≥ à margem nacional entre os finalistas.
   - **A (nada anômalo):** T1 reconcilia (linha 1), T3 dentro da faixa histórica, e o erro do T5 dentro do padrão dos institutos (critério por instituto da regra fixada, todos os institutos com histórico dentro).
   - **B (anomalia com causa mundana):** demais casos em que os achados são localizados e explicáveis por erro operacional, particularidade regional ou artefato de dado ou de modelo, e não são materiais.
4. Nenhum desfecho autoriza conclusão nacional por raciocínio agregado. O relatório separa resultados de interpretação, usa linguagem descritiva e lista as limitações.
5. **Relatório:** `output/report.md`.
