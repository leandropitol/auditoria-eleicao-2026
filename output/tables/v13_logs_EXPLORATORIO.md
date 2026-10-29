# v1.3 — checagem dos logs de urna (EXPLORATÓRIO)

Checagem descritiva feita **depois** de abrir os logs baixados no plano v1.2 (D12), para responder a perguntas públicas. Não houve plano prévio; nada aqui altera a classificação confirmatória. Os logs cobrem todas as seções encerradas depois das 17h15 e uma amostra aleatória de 600 das demais (G0); os números de G0 são os únicos que representam o conjunto das urnas. Fonte: TSE, logs de urna (D12); hashes em `data/raw/MANIFEST.csv`.

## Verificações de assinatura registradas no log

- Total: 3.411.127 verificações, das quais 5 sem "SUCESSO". No dia do 2º turno (25/10): 349.762 verificações, 0 sem "SUCESSO".
- Arquivos de assinatura distintos (dígitos trocados por N): 171, sendo 26 `.vst` (software), 143 `.vsc` e 2 `.vsu` (dados e configuração). Lista em `v13_arquivos_assinatura.csv`.
- Arquivos com "turno" no nome: 0.

Falhas (`v13_falhas_assinatura.csv`):

| uf   |   mun |   zona |   secao | data_hora_urna      | mensagem                                                                           |
|:-----|------:|-------:|--------:|:--------------------|:-----------------------------------------------------------------------------------|
| PE   | 24139 |   0072 |    0021 | 28/09/2026 09:32:30 | Verificação de assinatura - Etapa [26] - [/dsk/fe/estatico/infomidia.vsc] - [ERRO] |
| RJ   | 58971 |   0135 |    0043 | 04/10/2026 07:17:49 | Verificação de assinatura - Etapa [26] - [/dsk/fe/estatico/infomidia.vsc] - [ERRO] |
| RJ   | 60011 |   0016 |    0223 | 21/09/2026 12:09:35 | Verificação de assinatura - Etapa [26] - [/dsk/fe/estatico/infomidia.vsc] - [ERRO] |
| RJ   | 60011 |   0025 |    0966 | 25/09/2026 15:56:03 | Verificação de assinatura - Etapa [26] - [/dsk/fe/estatico/infomidia.vsc] - [ERRO] |
| RJ   | 60011 |   0122 |    0386 | 21/09/2026 10:46:17 | Verificação de assinatura - Etapa [26] - [/dsk/fe/estatico/infomidia.vsc] - [ERRO] |

Em cada falha, o log registra em seguida erro de integridade na inicialização e a urna desligada pela chave; o aplicativo não é iniciado.

## Mensagem "Problema ao desmontar a MR" (módulo GAP)

|                           |   seções com log |   com eventos do 1º turno (04/10) |   mensagem da MR até 04/10 |   mensagem da MR em 25/10 |
|:--------------------------|-----------------:|----------------------------------:|---------------------------:|--------------------------:|
| todas (G0 + G1 + G2)      |             9026 |                              8994 |                          0 |                      9010 |
| só a amostra aleatória G0 |              579 |                               579 |                          0 |                       579 |

A mensagem aparece na inicialização, logo depois de a urna reconhecer a "mídia de resultado de 2º turno", e a urna segue para o aplicativo de votação. Distribuição por dia em `v13_msg_mr_por_dia.csv`. A causa não está documentada no material consultado; a hipótese de ser comportamento sistemático da preparação ou do software do 2º turno decorre só de ela aparecer em quase todas as urnas e só nesse turno.

## Limite

O log é escrito pelo próprio software da urna. Ele mostra consistência interna, não prova independente de qual software foi executado. Essa prova depende de procedimentos externos (cerimônia de assinatura e lacração, publicação de hashes, testes de autenticidade e integridade em urnas sorteadas), que este trabalho não verificou.
