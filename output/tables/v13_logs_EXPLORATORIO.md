# v1.3.1 — checagem dos logs de urna (EXPLORATÓRIO)

Checagem descritiva feita **depois** de abrir os logs baixados no plano v1.2 (D12), para responder a perguntas públicas. Não houve plano prévio; nada aqui altera a classificação confirmatória. Fonte: TSE, logs de urna (D12); hashes em `data/raw/MANIFEST.csv`.

## Alcance: amostra, não o país

São 9.026 logs de seções do 2º turno, de um total de 497.897 seções no Brasil:
- 8.447 seções encerradas depois das 17h15 (quase todas as desse grupo). **Não é amostra aleatória**: concentra-se em RJ, SP, BA, PE e PB;
- 579 seções sorteadas entre as que encerraram no horário normal (G0). Só esta parte representa o conjunto das urnas.

Com 579 urnas sorteadas, uma mensagem ausente de todas elas ocorre, com 95% de confiança, em menos de 0,64% das urnas (até cerca de 3.162 seções); eventos raros só podem ser contados no país com todos os logs.

## Quatro mensagens de um desafio público

Número de urnas cujo log contém a mensagem, por data do evento:

| mensagem                   |   todas: 1º turno (04/10) |   todas: 2º turno (25/10) |   todas: qualquer data |   sorteadas: 1º turno (04/10) |   sorteadas: 2º turno (25/10) |   sorteadas: qualquer data |
|:---------------------------|--------------------------:|--------------------------:|-----------------------:|------------------------------:|------------------------------:|---------------------------:|
| Problema ao desmontar a MR |                         0 |                      9010 |                   9026 |                             0 |                           579 |                        579 |
| GAP erro 73                |                         0 |                         0 |                      2 |                             0 |                             0 |                          0 |
| turno2.jez                 |                         0 |                         0 |                      2 |                             0 |                             0 |                          0 |
| turno2.vsc                 |                         0 |                         0 |                      2 |                             0 |                             0 |                          0 |
| Verificação de assinatura  |                      8982 |                      9013 |                   9026 |                           577 |                           579 |                        579 |

- "Problema ao desmontar a MR": 579 de 579 urnas sorteadas no 2º turno; com 95% de confiança, ocorre em pelo menos 99,36% das urnas do país nesse turno. Aparece na inicialização, logo depois de a urna reconhecer a "mídia de resultado de 2º turno", e a urna segue para o aplicativo de votação. A causa não está documentada no material consultado.
- Arquivos de assinatura distintos citados nas verificações (dígitos trocados por N): 171 (26 `.vst`, 143 `.vsc`, 2 `.vsu`); com "turno" no nome: 0. `turno2.jez` e `turno2.vsc` aparecem só dentro da mensagem "GAP erro 73", na mídia de resultado (`/dsk/mr/`).

## Erros de assinatura, em todos os formatos de mensagem

Verificações no formato "Verificação de assinatura … [resultado]": 3.411.127, das quais 5 sem "SUCESSO". Somando as linhas de nível ERRO que citam assinatura e agrupando por inicialização da urna: **10 inicializações com erro de assinatura**, 0 delas no dia do 2º turno. Em 9, o aplicativo de votação não foi iniciado; em 1, foi iniciado depois do erro.

| uf   |   mun |   zona |   secao | grupo   | data_hora_urna      | desfecho                           | mensagens                                                                                                                                                                                                                                |
|:-----|------:|-------:|--------:|:--------|:--------------------|:-----------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| BA   | 36595 |   0049 |    0007 | G1      | 30/09/2026 08:48:10 | aplicativo de votação não iniciado | Inicialização do aplicativo | Validando assinaturas da MV (9336) | Erro na verificação de integridade do sistema. Desligue e ligue a urna. Se o erro persistir,                                                                          |
| PE   | 24139 |   0072 |    0021 | G2      | 28/09/2026 09:32:30 | aplicativo de votação não iniciado | Verificação de assinatura - Etapa [26] - [/dsk/fe/estatico/infomidia.vsc] - [ERRO] || Inicialização do aplicativo | Validando assinaturas (9336) | Erro na verificação de integridade do sistema. Desligue a urna e faça uma nova carga. |
| RJ   | 58971 |   0135 |    0043 | G2      | 04/10/2026 07:17:49 | aplicativo de votação não iniciado | Verificação de assinatura - Etapa [26] - [/dsk/fe/estatico/infomidia.vsc] - [ERRO] || Inicialização do aplicativo | Validando assinaturas (9336) | Erro na verificação de integridade do sistema. Desligue a urna e faça uma nova carga. |
| RJ   | 60011 |   0016 |    0223 | G2      | 21/09/2026 12:09:35 | aplicativo de votação não iniciado | Verificação de assinatura - Etapa [26] - [/dsk/fe/estatico/infomidia.vsc] - [ERRO] || Inicialização do aplicativo | Validando assinaturas (9336) | Erro na verificação de integridade do sistema. Desligue a urna e faça uma nova carga. |
| RJ   | 60011 |   0025 |    0966 | G1      | 25/09/2026 15:56:03 | aplicativo de votação não iniciado | Verificação de assinatura - Etapa [26] - [/dsk/fe/estatico/infomidia.vsc] - [ERRO] || Inicialização do aplicativo | Validando assinaturas (9336) | Erro na verificação de integridade do sistema. Desligue a urna e faça uma nova carga. |
| RJ   | 60011 |   0122 |    0386 | G2      | 21/09/2026 10:46:17 | aplicativo de votação não iniciado | Verificação de assinatura - Etapa [26] - [/dsk/fe/estatico/infomidia.vsc] - [ERRO] || Inicialização do aplicativo | Validando assinaturas (9336) | Erro na verificação de integridade do sistema. Desligue a urna e faça uma nova carga. |
| RJ   | 60011 |   0179 |    0331 | G2      | 19/10/2026 08:22:41 | aplicativo de votação não iniciado | GAP erro 73 | Validação do VOTA | Erro verificando assinatura do arquivo turno2.jez em /dsk/mr/turno2.vsc. Desligue a urna, insira uma nova mídia de resultado d                                                                         |
| SP   | 63711 |   0119 |    0133 | G2      | 15/10/2026 16:29:20 | aplicativo de votação não iniciado | GAP erro 73 | Validação do VOTA | Erro verificando assinatura do arquivo turno2.jez em /dsk/mr/turno2.vsc. Desligue a urna, insira uma nova mídia de resultado d                                                                         |
| SP   | 63711 |   0119 |    0133 | G2      | 15/10/2026 16:32:26 | aplicativo de votação não iniciado | GAP erro 73 | Validação do VOTA | Erro verificando assinatura do arquivo turno2.jez em /dsk/mr/turno2.vsc. Desligue a urna, insira uma nova mídia de resultado d                                                                         |
| SP   | 71072 |   0389 |    0154 | G2      | 04/10/2026 12:57:59 | aplicativo de votação iniciado     | Erro na verificação de assinatura do arquivo - uenux.vsu                                                                                                                                                                                 |

O caso em que o aplicativo foi iniciado depois de um erro de assinatura não tem explicação no material consultado; o que o arquivo citado cobre e por que o erro não bloqueou a inicialização são perguntas para o TSE.

## Limite

O log é escrito pelo próprio software da urna. Ele mostra consistência interna, não prova independente de qual software foi executado. Essa prova depende de procedimentos externos (cerimônia de assinatura e lacração, publicação de hashes, testes de autenticidade e integridade em urnas sorteadas), que este trabalho não verificou.
