# Plano v1.2 — votos depositados após as 17h no 2º turno (EXPLORATÓRIO)

**Status:** redigido em 2026-10-29, **antes** de baixar ou abrir qualquer dado de horário de encerramento ou log de urna. Carimbado com OpenTimestamps antes da execução. Não estava no pré-registro: todo resultado é **exploratório** e não altera nenhuma classificação confirmatória.

## Motivação

Circula um documento ("Relatório Pericial Independente") que compara o desempenho dos candidatos conforme o horário de encerramento das seções (`DT_ENCERRAMENTO`). Segundo relato público, uma decisão judicial às 17h01 do dia da votação prorrogou o horário até as 19h; as seções já encerradas não reabriram. A pergunta deste plano é quantitativa: **quantos votos foram depositados depois das 17h e se esse número poderia, no pior caso, alterar o resultado**. A pergunta sobre isonomia do procedimento é institucional e jurídica e não é respondida aqui.

O que já foi visto antes de redigir este plano: os números agregados do documento acima (faixas 17h01–17h15, 17h16–18h59 e após 19h00; percentuais por UF), a margem oficial (4.430.191 votos) e o tamanho dos arquivos no catálogo do TSE. Um log de urna foi baixado só para medir o tamanho (≈ 187 KB) e apagado sem ser aberto.

## Fontes novas

- **D11** — BU na Web, 2º turno 2026, um arquivo por UF (27 arquivos, ≈ 144 MB), `cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_2t_<UF>_*.zip`. Usado para `DT_ABERTURA`, `DT_ENCERRAMENTO` e comparecimento por seção. Exterior (ZZ) excluído, como nos demais testes.
- **D12** — log de urna (`*-log.jez`) e índice (`aux.json`) das seções selecionadas abaixo, da entrada "Totalizado", em `resultados.tse.jus.br/oficial/ele2026/arquivo-urna/3221/dados/...`.

Ambos registrados no manifesto com SHA-256, como D1–D10. Se D12 passar de 12.000 seções ou 3 GB, o download para e pede autorização.

## Regras fixadas

1. **Hora de Brasília.** Para cada município, `deslocamento = round(mediana(DT_ABERTURA) − 08:00)` em horas inteiras; horários de D11 e dos logs são convertidos com `hora − deslocamento`. A distribuição dos deslocamentos por UF é reportada.
2. **Grupos por encerramento (hora de Brasília):** G0 = até 17h15; G1 = 17h16 a 18h59; G2 = 19h00 ou depois. Os cortes são os do documento, para permitir comparação; isso é declarado.
3. **Seleção para D12:** todas as seções de G1 e G2 (censo) e uma amostra aleatória simples de 600 seções de G0 (semente 20261025).
4. **Voto no log:** cada evento com a mensagem "O voto do eleitor foi computado". Se essa mensagem não existir no formato de 2026, a mensagem equivalente será identificada pela documentação do TSE e registrada em `DESVIOS.md` antes de qualquer contagem.
5. **Por seção:** `n_log` (votos no log), `n_17h00` (votos com horário ≥ 17:00:00) e `n_17h15` (≥ 17:15:00). Checagem: `n_log` contra o comparecimento do BU. Seções com diferença maior que 1% (ex.: urna de contingência, log parcial) são listadas e ficam fora da soma principal, com a soma alternativa que as inclui.

## Análises

- **A1 — pior caso (principal).** `V = Σ n_17h00` em G1 ∪ G2. Pior caso: todos esses votos para um só candidato. Comparação de `V` com a margem oficial. Também: estimativa para G0 inteiro (votos de fila depois das 17h em seções encerradas no horário normal), expandida da amostra, com IC 95% por bootstrap; e o limite extremo `V + G0`.
- **A2 — direção (secundária).** Nas seções com log, regressão do resíduo bruto do modelo do T2 (em pontos de participação do 13) sobre `f = n_17h00 / n_log`, com erro-padrão agrupado por município. O modelo é o do T2 confirmatório **sem** `d_comparecimento` e `d_bn`, porque essas variáveis são afetadas pela própria prorrogação. O coeficiente estima quanto a participação do 13 entre os votos depois das 17h difere da prevista para a seção. Efeito líquido estimado sobre a margem: `2 · b/100 · V`, com IC.
- **A3 — conferência do documento.** Número de seções e de eleitores por faixa de encerramento, comparado com a tabela do documento.

## Como será lido

- Se `V` < margem: a prorrogação não pode, sozinha, ter invertido o resultado, em nenhuma hipótese sobre a direção desses votos.
- Se `V` ≥ margem: o pior caso é material, e A2 passa a ser central; o resultado será reportado como está.
- A2 é estimativa ecológica (dado agregado por seção); não descreve o voto de nenhum eleitor.
- Logs não registram em quem cada eleitor votou (sigilo); nenhuma análise aqui identifica o voto depois das 17h diretamente.

## Saídas

`src/15_encerramento_v12.py`; `output/tables/v12_encerramento_EXPLORATORIO.md` e tabelas `v12_*.csv`. Registro em `DESVIOS.md`. Publicação só com autorização do autor.
