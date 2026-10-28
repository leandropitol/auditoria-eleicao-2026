# T4 — dígitos (completude; não é evidência)

**Advertência do pré-registro:** contagens por urna têm faixa estreita e teto rígido; Benford não vale nessas condições e produz falsos positivos com regularidade. Desvio em T4, sozinho, não constitui achado e não deve ser reportado como evidência sob nenhuma circunstância.

## 2026 contra os anos de controle (tamanho do desvio)

| métrica      |   2014–2022 (mín.) |   2014–2022 (máx.) | 2026 (candidatos)      | 2026 dentro da faixa   |
|:-------------|-------------------:|-------------------:|:-----------------------|:-----------------------|
| benford2_MAD |             0.003  |             0.0103 | 13: 0.0102, 22: 0.0091 | True                   |
| ultimo_MAD   |             0.0003 |             0.0007 | 13: 0.0002, 22: 0.0003 | False                  |
| prop_mult5   |             0.1996 |             0.2016 | 13: 0.2001, 22: 0.2003 | True                   |
| prop_mult10  |             0.1    |             0.1011 | 13: 0.1003, 22: 0.1002 | True                   |

## Todos os testes

|   ano |   candidato |   n_contagens_ge_10 |   benford2_media_2o_digito |   benford2_MAD |   benford2_chi2 |   benford2_p |   ultimo_MAD |   ultimo_chi2 |   ultimo_p |   prop_mult5 |   mult5_p |   prop_mult10 |   mult10_p |
|------:|------------:|--------------------:|---------------------------:|---------------:|----------------:|-------------:|-------------:|--------------:|-----------:|-------------:|----------:|--------------:|-----------:|
|  2014 |          13 |              428483 |                     3.9709 |         0.0069 |        2824.88  |            0 |       0.0003 |        7.102  |     0.6265 |       0.1996 |    0.5063 |        0.1001 |     0.76   |
|  2014 |          45 |              423360 |                     4.0342 |         0.0052 |        1420.43  |            0 |       0.0007 |       31.8728 |     0.0002 |       0.2014 |    0.0228 |        0.101  |     0.0274 |
|  2018 |          13 |              453894 |                     4.0412 |         0.0044 |        1292.89  |            0 |       0.0004 |       12.328  |     0.1954 |       0.2003 |    0.6295 |        0.1    |     0.9389 |
|  2018 |          17 |              447829 |                     4.185  |         0.003  |         557.337 |            0 |       0.0005 |       14.3249 |     0.1112 |       0.2005 |    0.3719 |        0.1003 |     0.4825 |
|  2022 |          13 |              471903 |                     3.8526 |         0.0103 |        6613.13  |            0 |       0.0003 |       11.4204 |     0.248  |       0.2001 |    0.9261 |        0.1001 |     0.8272 |
|  2022 |          22 |              468468 |                     4.0744 |         0.0065 |        3039.98  |            0 |       0.0005 |       17.2906 |     0.0444 |       0.2016 |    0.0056 |        0.1011 |     0.0121 |
|  2026 |          13 |              499016 |                     3.8585 |         0.0102 |        6731.22  |            0 |       0.0002 |        4.9762 |     0.8364 |       0.2001 |    0.7961 |        0.1003 |     0.4953 |
|  2026 |          22 |              496587 |                     3.9706 |         0.0091 |        6461.01  |            0 |       0.0003 |       12.3637 |     0.1936 |       0.2003 |    0.55   |        0.1002 |     0.6964 |

Contagens ≥ 10 votos por seção e finalista. MAD = desvio absoluto médio entre as proporções observada e esperada. Com centenas de milhares de seções, p-valores baixos são esperados mesmo para desvios mínimos. Fontes: TSE (D2, D8); hashes em `data/raw/MANIFEST.csv`. Regras em `docs/desenho_T4_consolidacao.md`.
