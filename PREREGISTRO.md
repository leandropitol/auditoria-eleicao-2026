# Plano de Auditoria Estatística — 2º Turno Presidencial 2026

**Versão:** 1.0
**Data de redação:** 2026-10-26
**Status:** pré-registro — redigido ANTES da coleta e da análise dos dados

---

## 0. Natureza deste documento

Este é um **plano de análise pré-registrado**. Seu objetivo é fixar hipóteses, métricas, limiares e critérios de decisão *antes* de olhar os dados, de modo que o resultado não possa ser moldado pelo que se deseja encontrar.

**Regra de ouro:** nenhuma métrica, filtro ou recorte pode ser adicionado depois de ver os resultados. Se surgir necessidade de alteração, ela deve ser registrada na Seção 9 (Log de Desvios), com data e justificativa, e os resultados correspondentes devem ser reportados como **exploratórios**, nunca como confirmatórios.

Este documento não pressupõe que houve fraude, nem que não houve. Ele define como distinguir as duas coisas com dados públicos.

---

## 1. Pergunta de pesquisa

> O resultado do 2º turno presidencial de 2026 é consistente com o processo eleitoral tal como documentado nos registros públicos, ou existem anomalias localizadas e não explicáveis por fatores demográficos, políticos e de erro amostral conhecidos?

### 1.1 Hipóteses

| ID | Hipótese | Enunciado |
|----|----------|-----------|
| H0 | Nula | O resultado é explicável por transferência de votos, mudança de abstenção e erro de pesquisa dentro de faixas historicamente observadas. Desvios são ruído e heterogeneidade regional. |
| H1 | Alternativa — contagem | Existe divergência entre os votos registrados nos boletins de urna e os valores totalizados. |
| H2 | Alternativa — padrão | Existem clusters espaciais de desvio de voto sem correlato demográfico, político ou socioeconômico. |
| H3 | Alternativa — coação | Existe evidência sistemática (não anedótica) de voto obtido sob coação, concentrada geograficamente. |

**Hipótese padrão em caso de resultado inexplicado:** erro de especificação do modelo. "Não consigo explicar" ≠ "foi fraudado". A conclusão de fraude exige achado positivo, localizável e reproduzível.

---

## 2. Fontes de dados

Todas públicas. Nenhuma etapa deste plano requer dado sigiloso ou acesso privilegiado.

| # | Fonte | Conteúdo | Origem |
|---|-------|----------|--------|
| D1 | Boletins de Urna (BU) | Arquivo assinado digitalmente por urna, 1º e 2º turno | TSE — Dados Abertos |
| D2 | Resultados por seção | Totalização oficial, seção/zona/município/UF | TSE — Dados Abertos |
| D3 | Perfil do eleitorado | Faixa etária, sexo, escolaridade, por seção/zona | TSE — Dados Abertos |
| D4 | Comparecimento e abstenção | Por seção, ambos os turnos | TSE — Dados Abertos |
| D5 | Pesquisas registradas | Microdados, metodologia, margem declarada, instituto | TSE — Registro de Pesquisas |
| D6 | Dados socioeconômicos | Renda, escolaridade, urbanização, por município/setor | IBGE |
| D7 | Malha territorial | Shapefiles municipais e de setor censitário | IBGE |
| D8 | Série histórica | Resultados presidenciais 1989–2022, 1º e 2º turno | TSE |

### 2.1 Protocolo de integridade

- Registrar hash SHA-256 de cada arquivo baixado, com data/hora e URL de origem.
- Nunca editar arquivo bruto. Toda transformação ocorre em script versionado.
- Manter `data/raw/` imutável; `data/processed/` reconstruível por pipeline.

---

## 3. Testes — ordem de poder probatório

Executar **nesta ordem**. T1 é o teste decisivo; os demais só fazem sentido condicionados ao seu resultado.

---

### T1 — Verificação criptográfica e reconciliação dos BUs

**Poder probatório: ALTO.** Este é o único teste que endereça diretamente a hipótese de fraude na contagem.

**Procedimento**
1. Baixar os BUs de uma amostra aleatória estratificada por UF e porte de município (meta: n ≥ 5.000 urnas; ideal: universo completo).
2. Validar a assinatura digital de cada BU contra a cadeia de certificação publicada pelo TSE.
3. Extrair os votos por candidato de cada BU validado.
4. Somar e comparar com a totalização oficial (D2) na mesma granularidade.

**Métricas**
- Taxa de falha de assinatura
- Nº de urnas com divergência BU × totalização
- Magnitude da divergência (votos absolutos e % do total da urna)

**Critérios de decisão — fixados antecipadamente**

| Resultado | Interpretação |
|-----------|---------------|
| 100% das assinaturas válidas e divergência zero | H1 rejeitada. Fraude na contagem descartada no escopo amostrado. |
| Divergências isoladas, < 0,01% das urnas, sem padrão espacial ou direcional | Compatível com erro operacional. Reportar, não concluir fraude. |
| Divergências com direção consistente (favorecendo sistematicamente um candidato) ou cluster espacial | **Achado material.** Escalar: identificar urnas, documentar, encaminhar formalmente. |

**Nota:** se T1 retornar reconciliação completa, as hipóteses de fraude na contagem ficam encerradas. T2–T5 passam a tratar apenas de comportamento eleitoral, não de integridade da apuração.

---

### T2 — Análise de transferência intra-seção entre turnos

**Poder probatório: MÉDIO.**

**Procedimento**
1. Parear cada seção eleitoral entre 1º e 2º turno (chave: UF + município + zona + seção).
2. Para cada seção, calcular: Δ voto por candidato, Δ comparecimento, Δ brancos/nulos.
3. Modelar o voto do 2º turno em função do perfil de 1º turno da seção.
4. Identificar seções cujo deslocamento é incompatível com o das seções vizinhas e demograficamente similares.

**Restrição metodológica obrigatória**
Isto é dado **agregado**. Não permite inferir comportamento individual de eleitor (falácia ecológica). Taxas de transferência estimadas aqui são *compatíveis com* os agregados, nunca *demonstradas*. Qualquer conjunto de fluxos que feche o agregado é igualmente admissível sem microdado — que não existe e nem deve existir, por conta do sigilo do voto.

**Critério**
Seções anômalas devem ser (a) espacialmente agrupadas, (b) direcionais, e (c) não explicáveis por covariáveis de D3/D6 para constituírem achado. Falhando qualquer um dos três, é heterogeneidade regional.

---

### T3 — Modelo preditivo com análise espacial de resíduos

**Poder probatório: MÉDIO.** Principal ferramenta para H2.

**Procedimento**
1. Ajustar modelo do % de voto no 2º turno, por seção/município:
   - Preditores: resultado do 1º turno (todos os candidatos), renda, escolaridade, grau de urbanização, faixa etária do eleitorado, UF (efeito aleatório).
   - Especificação: modelo hierárquico (seção aninhada em município aninhado em UF).
2. Extrair resíduos e georreferenciá-los.
3. Testar autocorrelação espacial: **I de Moran global** e **LISA** (clusters locais).
4. Comparar o padrão de resíduos de 2026 com os de 2014, 2018 e 2022 usando a mesma especificação — a eleição anterior é o grupo de controle.

**Critérios**

| Resultado | Interpretação |
|-----------|---------------|
| I de Moran de 2026 dentro da faixa de 2014/2018/2022 | Nada anômalo. Autocorrelação espacial é esperada — vizinhos votam parecido. |
| Clusters LISA presentes mas também presentes em eleições anteriores nas mesmas regiões | Fenômeno regional estrutural, não evento de 2026. |
| Clusters significativos, exclusivos de 2026, direcionais, sem correlato demográfico | **Achado.** Localizar, listar municípios/seções, investigar causa específica. |

**Correção obrigatória:** este teste roda centenas de comparações locais. Aplicar FDR (Benjamini-Hochberg, q = 0,05). Sem correção, clusters "significativos" aparecerão por acaso — é matematicamente garantido.

---

### T4 — Testes de distribuição de dígitos

**Poder probatório: BAIXO.** Barato de rodar, fácil de superinterpretar.

**Procedimento**
- Benford de 2º dígito sobre contagens por urna
- Distribuição do último dígito (esperada: uniforme)
- Teste de agrupamento em múltiplos de 5 e 10

**Advertência explícita**
Contagens de voto por urna têm faixa estreita e limite superior rígido (nº de eleitores da seção). Benford **não é válido** nessas condições e produz falsos positivos rotineiramente. Este teste é incluído apenas para completude e porque sua ausência será questionada. **Desvio em T4 isoladamente não constitui achado** e não deve ser reportado como evidência sob nenhuma circunstância.

---

### T5 — Auditoria do desempenho das pesquisas

**Poder probatório: BAIXO para fraude; ALTO para avaliar a alegação de improbabilidade.**

**Procedimento**
1. Compilar as pesquisas finais registradas: instituto, data de campo, n, margem declarada, resultado.
2. Calcular o erro de cada uma **na margem entre os candidatos**, não no percentual individual.
3. Comparar com o erro histórico do mesmo instituto em 2010, 2014, 2018, 2022.
4. Estimar a correlação entre erros de institutos diferentes na mesma eleição.

**Pontos que o teste precisa resolver**
- O desvio-padrão da **diferença** entre dois candidatos é aproximadamente **2×** o do percentual individual. Cálculos de improbabilidade que usam o sigma individual sobre a margem estão errados por construção e superestimam a anomalia.
- Margem de erro cobre **apenas erro amostral**. Não cobre viés de modelo de eleitor provável, não-resposta diferencial, efeito de casa nem erro de ponderação — que historicamente dominam.
- Institutos erram de forma **correlacionada**. Duas pesquisas convergentes não multiplicam a confiança; frequentemente compartilham o mesmo viés.

**Critério**
Se o erro de 2026 estiver dentro da distribuição histórica de erros do mesmo instituto, a alegação de improbabilidade estatística fica refutada, independentemente do que os outros testes mostrarem.

---

### T6 — Análise da série histórica de reversões de 2º turno

**Poder probatório: BAIXO.** Corrige o argumento do "zero em sete".

**Procedimento**
1. Para cada 2º turno desde 1989, registrar a margem do 1º turno e se houve reversão.
2. Estimar a probabilidade de reversão **condicionada à margem do 1º turno**, não incondicionalmente.
3. Ampliar a base com 2ºs turnos presidenciais de outros países com sistema comparável (França, Chile, Colômbia, Argentina, Peru) para aumentar o n.

**Pontos a estabelecer**
- 0 ocorrências em 7 tentativas não implica probabilidade zero. Regra de sucessão de Laplace: ~11%. Limite superior do IC 95% pela regra de três: ~35%.
- Os 7 casos **não são intercambiáveis**: a série mistura vantagens de 1º turno amplas com estreitas. O caso de 2026 pertence à categoria de margem estreita, que tem n muito menor.
- Calcular a improbabilidade de um resultado **depois** de observá-lo é o erro do atirador texano. Todo desfecho específico é improvável a priori.

---

## 4. Sobre relatos de coação de eleitores idosos (H3)

**Isto não é objeto de análise estatística agregada.** É objeto de denúncia individual.

### 4.1 Enquadramento legal relevante

- Voto é **facultativo** acima de 70 anos. Comparecimento de eleitor nonagenário não é, por si, irregularidade.
- **Voto assistido** é legal e previsto: eleitor com dificuldade física ou visual pode ser acompanhado por pessoa de sua confiança, inclusive dentro da cabine. Acompanhamento físico não é, por si, irregularidade.
- A linha é a **vontade do eleitor**. Voto obtido de pessoa sem discernimento, ou cuja vontade é substituída pela do acompanhante, configura crime eleitoral — e, em paralelo, violência contra pessoa idosa.

### 4.2 Por que não entra como evidência sobre o resultado

| Limitação | Consequência |
|-----------|--------------|
| Sem denominador | Vídeos compartilhados não são amostra. Não há como estimar prevalência. |
| Sem direção | O fenômeno ocorre em todo o território e em todos os espectros. Vídeo mostra que ocorre, não que ocorreu assimetricamente. |
| Escala incompatível | Mover uma diferença de milhões de votos exigiria operação de magnitude não ocultável. |
| Risco de recontextualização | Material de outras eleições ou outros países recircula com legenda falsa. "O vídeo é real" ≠ "o vídeo é do que dizem que é". |

### 4.3 Encaminhamento correto

Cada caso deve ser denunciado individualmente ao **Ministério Público Eleitoral**, com local, data, seção e, se possível, identificação. Para os casos que configuram também violência contra idoso, cabe denúncia independente do contexto eleitoral.

**Não agregar relatos de rede social em métrica.** Fazê-lo é construir um denominador fictício e contamina todo o resto da análise.

---

## 5. Critérios globais de decisão

Fixados antes da coleta.

- **α = 0,05** para testes individuais
- **FDR (Benjamini-Hochberg) com q = 0,05** para famílias de testes múltiplos — obrigatório em T3
- **Tamanho de efeito mínimo relevante:** desvio capaz de alterar o resultado nacional. Anomalia estatisticamente significativa mas numericamente irrelevante deve ser reportada como tal, explicitamente.

### 5.1 Os três desfechos admissíveis

| Desfecho | Condição | Encaminhamento |
|----------|----------|----------------|
| **A — Nada anômalo** | T1 reconcilia; T3 dentro da faixa histórica; T5 erro dentro do padrão do instituto | Publicar. Resultado negativo é resultado. |
| **B — Anomalia com causa mundana** | Achado localizado explicável por erro operacional, particularidade regional ou artefato de dado | Publicar com a explicação. Não escalar. |
| **C — Anomalia inexplicada** | Achado material, localizável, direcional, reprodutível, sobrevivendo a correção de múltiplos testes | Documentar urnas/seções específicas. Encaminhar formalmente. **Único desfecho que sustenta questionamento jurídico.** |

**Nenhum desfecho autoriza conclusão nacional baseada em raciocínio agregado.** Alegação formal exige apontar urnas específicas.

---

## 6. Armadilhas — checklist de autocontrole

Revisar antes de cada rodada de análise.

- [ ] **Parada oportunista** — encerrar a análise quando o resultado agrada. Todos os testes planejados devem rodar e ser reportados, inclusive os que não deram nada.
- [ ] **Garimpo de métrica** — trocar de teste até algum acusar anomalia. Lista de testes fechada nesta versão do documento.
- [ ] **Falácia ecológica** — ler agregado como comportamento individual. Proibido em T2.
- [ ] **Atirador texano** — calcular improbabilidade post-hoc do resultado observado.
- [ ] **Múltiplos testes sem correção** — rodar centenas de comparações locais e reportar as "significativas".
- [ ] **Ausência de grupo de controle** — toda métrica de 2026 precisa ser comparada à mesma métrica em 2014/2018/2022.
- [ ] **Confundir inexplicado com fraudado** — a hipótese padrão é erro de modelo.
- [ ] **Assimetria de ceticismo** — aplicar o mesmo rigor ao achado que confirma quanto ao que refuta.

### 6.1 Controle externo recomendado

Antes de publicar qualquer achado, submeter o código e os dados a alguém que **não compartilhe a expectativa inicial** do analista. Achado que não sobrevive a leitor adversarial não deveria sair.

---

## 7. Pipeline técnico

```
projeto/
├── data/
│   ├── raw/              # imutável, com manifest de hashes
│   └── processed/        # reconstruível pelo pipeline
├── src/
│   ├── 01_download.py           # D1–D8, com registro de hash
│   ├── 02_validate_bu.py        # T1 — assinatura + reconciliação
│   ├── 03_pair_sections.py      # T2 — pareamento entre turnos
│   ├── 04_model_residuals.py    # T3 — modelo hierárquico
│   ├── 05_spatial.py            # T3 — Moran / LISA
│   ├── 06_digits.py             # T4
│   ├── 07_polls.py              # T5
│   └── 08_historical.py         # T6
├── output/
│   ├── figures/
│   ├── tables/
│   └── report.md
├── PREREGISTRO.md        # este documento, congelado
└── DESVIOS.md            # log da Seção 9
```

**Stack sugerida:** Python (pandas, statsmodels, geopandas, libpysal/esda, pymc para o modelo hierárquico), ou R (tidyverse, lme4, spdep, sf).

**Requisitos de reprodutibilidade**
- Semente aleatória fixa e registrada
- Ambiente versionado (`requirements.txt` ou `renv.lock`)
- Commit do pré-registro **antes** do primeiro download
- Nenhum resultado em notebook não versionado

---

## 8. Sequência de execução

| Etapa | Conteúdo | Pré-requisito |
|-------|----------|---------------|
| 1 | Congelar este documento em commit. Criar `DESVIOS.md` vazio. | — |
| 2 | Coleta D1–D8 com manifest de hashes | Etapa 1 |
| 3 | **T1** — verificação de BUs | Etapa 2 |
| 4 | **T5** e **T6** — pesquisas e série histórica (independentes, rodam em paralelo) | Etapa 2 |
| 5 | **T2** e **T3** — pareamento e modelo espacial | Etapa 3 |
| 6 | **T4** — dígitos (completude) | Etapa 3 |
| 7 | Consolidação, correção de múltiplos testes, classificação no desfecho A/B/C | Etapas 3–6 |
| 8 | Revisão adversarial externa | Etapa 7 |
| 9 | Publicação — **incluindo os testes negativos** | Etapa 8 |

**T1 e T5 são os melhores pontos de partida:** ambos usam dado público direto, são autocontidos e qualquer um dos dois já resolve sozinho uma parte substancial da pergunta.

---

## 9. Log de desvios

Toda alteração ao plano após o congelamento deve ser registrada aqui, com data, descrição e justificativa. Resultados afetados por desvio são **exploratórios**, não confirmatórios.

| Data | Desvio | Justificativa | Impacto na classificação |
|------|--------|---------------|--------------------------|
| — | — | — | — |

---

## 10. Compromisso de publicação

O resultado será publicado **qualquer que seja**, incluindo o desfecho A (nada anômalo). Análise que só é divulgada quando confirma a suspeita inicial não é investigação — é advocacia com aparência de estatística, e o valor de todo o restante do trabalho depende de não ser isso.
