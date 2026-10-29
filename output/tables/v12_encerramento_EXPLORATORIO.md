# Plano v1.2 — votos depositados após as 17h no 2º turno (EXPLORATÓRIO)

Plano carimbado antes da coleta: `docs/plano_v1_2_encerramento.md` (+ `.ots`). Nada aqui altera a classificação confirmatória. Fontes: TSE, BU na Web (D11) e logs de urna (D12); hashes em `data/raw/MANIFEST.csv`.

Margem entre os finalistas nas seções do Brasil (BU na Web, exterior excluído): **4.401.534 votos** (a margem oficial, com o exterior, é de 4.430.191).

## A3 — seções por faixa de encerramento (hora de Brasília)

| faixa           |   secoes |            aptos |   comparecimento |              v13 |              v22 |   pct_13 |   margem_13_menos_22 |
|:----------------|---------:|-----------------:|-----------------:|-----------------:|-----------------:|---------:|---------------------:|
| até 17h00       |   125624 |      3.8882e+07  |      3.16e+07    |      1.50012e+07 |      1.56083e+07 |    49.01 |    -607102           |
| 17h01 a 17h15   |   363428 |      1.158e+08   |      9.37182e+07 |      4.76927e+07 |      4.29628e+07 |    52.61 |          4.72989e+06 |
| 17h16 a 18h59   |     2493 | 838322           | 675182           | 372437           | 279413           |    57.14 |      93024           |
| 19h00 ou depois |     6352 |      2.30888e+06 |      1.86126e+06 | 989819           | 804095           |    55.18 |     185724           |

Deslocamento de fuso aplicado (regra 1): AC -2 h (2.270); AM -2 h (556); AM -1 h (7.601); MS -1 h (7.106); MT -1 h (8.287); PE +1 h (10); RO -1 h (4.698); RR -1 h (1.519). Demais UFs: 0.

## A1 — votos registrados no log após as 17h

|    |   secoes_no_grupo |   secoes_com_log |   secoes_validas |   comparecimento_validas |   votos_17h00 |   votos_17h15 |   votos_17h00_incluindo_invalidas |
|:---|------------------:|-----------------:|-----------------:|-------------------------:|--------------:|--------------:|----------------------------------:|
| G1 |              2493 |             2278 |             2277 |                   615228 |           957 |           442 |                               957 |
| G2 |              6352 |             6169 |             6169 |                  1811868 |          4363 |          3233 |                              4363 |
| G0 |            489052 |              579 |              579 |                   149563 |            41 |             0 |                                41 |

- Seções que fecharam depois das 17h15 (G1 + G2): **5.320 votos após as 17h00** nos logs válidos (5.320 incluindo os logs com divergência de contagem).
- Pior caso (todos esses votos para um só candidato): 0.12% da margem.
- 399 seções de G1 + G2 ficaram sem log válido (sem log na entrada "Totalizado" ou com contagem divergente). Somando **todo** o comparecimento delas (109.345) ao pior caso: 114.665 votos = 2.6% da margem.
- Horário do último voto (mediana; percentil 90): G1 16h53; 17h20. G2 16h59; 18h29. Nas seções encerradas depois das 19h, a urna ficou aberta, mas a maioria não recebeu nenhum voto depois das 17h.
- Seções que fecharam até 17h15 (G0), expansão da amostra de 579: 34.631 votos após as 17h00 (IC 95% 22.806 a 47.300). São votos de quem estava na fila, previstos na lei.
- Limite extremo (todos os votos após 17h00 do país, G0 estimado no limite superior): 52.620 votos = 1.2% da margem.
- Se os votos após 17h00 em G1 + G2 tivessem se dividido como o resto da própria seção, o saldo para o 13 seria de 773 votos.

## A2 — direção (estimativa ecológica)

Resíduo do modelo do T2 (sem `d_comparecimento` e `d_bn`) sobre a fração de votos após 17h, em 9013 seções com log válido; erro-padrão agrupado por município.

- Coeficiente: 4.44 pontos (IC 95% -8.90 a 17.79); p = 0.514.
- Efeito líquido estimado sobre a margem: 473 votos (IC 95% -947 a 1.893), isto é, 0.01% da margem.

Logs não registram em quem cada eleitor votou; A2 é inferência agregada por seção e não descreve o voto de nenhum eleitor. A pergunta sobre a isonomia do procedimento é institucional e não é respondida aqui.
