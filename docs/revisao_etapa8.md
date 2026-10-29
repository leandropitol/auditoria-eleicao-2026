# Etapa 8 — revisão adversarial

Registro das revisões críticas recebidas e da resposta a cada ponto. As revisões são resumidas e não identificadas; o texto original só é publicado com autorização de quem o escreveu.

## Revisão nº 1 (recebida em 2026-10-28/29, autor não identificado)

**Avaliação geral do revisor:** a estrutura metodológica está acima da média para uma auditoria independente. Pontos fortes: a separação entre integridade da contagem, comportamento geográfico e transferência entre turnos; a verificação dos boletins, com teste de adulteração; o pré-registro e a transparência; o reconhecimento das limitações. Mesmo assim, o trabalho ainda não deveria ser apresentado como auditoria conclusiva.

| Ponto do revisor | Avaliação | Resposta (v1.1) |
|---|---|---|
| A. O horário do commit Git não prova, sozinho, que o pré-registro existia antes da coleta | **Procede.** Os commits só chegaram ao GitHub em 2026-10-28T20:42:54Z; antes disso, as datas são locais | Limitação declarada no relatório. Carimbo OpenTimestamps do plano v1.1 e do estado anterior antes das novas análises. Regra daqui em diante: todo plano novo é carimbado antes de ser executado |
| B. A amostra não elimina irregularidades no universo; detalhar as seções excluídas; mostrar a memória de cálculo do intervalo; boletim igual à totalização não prova a intenção do eleitor | **Procede** | Apêndice do T1 com a memória de cálculo (Clopper-Pearson, com e sem pesos), as seções agregadas e as sem BU, e a nota de escopo sobre a intenção do eleitor |
| C. Modelo geográfico: mostrar as 461 seções, a magnitude, os p antes e depois da correção, a análise ponderada completa e a sensibilidade; esclarecer o efeito do Censo 2022 nos anos anteriores | **Procede em parte.** As tabelas completas já estavam publicadas, mas sem indicação no relatório; a sensibilidade não tinha sido feita | Distribuição das 461 seções; especificações alternativas S1–S3; T3 sem as covariáveis do Censo |
| D. A comparação internacional é limitada (países não equivalentes, n = 42); evitar tratar 49% como valor preciso | **Procede** | Texto passa a "da ordem de metade, com grande incerteza (27% a 71%)", com a ressalva |
| E. O erro das pesquisas merece estudo próprio; as 19 pesquisas não são independentes | **Procede.** Os mecanismos citados exigem microdados dos institutos, que não são públicos | Não independência explicitada; mecanismos registrados como estudo futuro |
| 3. O veredito "anomalia com causa mundana" pode ser lido como explicação causal definitiva; o trabalho não demonstra ausência de fraude | **Procede** | Veredito reescrito; frase explícita sobre o que o trabalho não demonstra |

Observação do autor: a conta de "1,26% da margem" somava votos; o efeito máximo de uma troca de lado é o dobro (pior caso), e o texto passou a apresentar esse valor.
