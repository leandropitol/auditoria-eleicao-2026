# Log de desvios

Seção 9 de `PREREGISTRO.md`. Toda alteração ao plano após o congelamento deve ser registrada aqui, com data, descrição e justificativa. Resultados afetados por desvio são **exploratórios**, não confirmatórios.

| Data | Desvio | Justificativa | Impacto na classificação |
|------|--------|---------------|--------------------------|
| 2026-10-28 | Detalhamento do desenho amostral do T1 (estratos de porte por nº de seções do município, n = 6.000, alocação proporcional com mínimo 5, semente 20261025) e das regras operacionais de verificação e classificação, em `docs/desenho_amostral_T1.md` | O plano fixa "amostra estratificada por UF e porte de município, n ≥ 5.000" sem definir porte, alocação nem regras de operação; detalhes fixados antes do sorteio e antes de abrir qualquer BU ou arquivo de totalização | Nenhum: especificação de detalhe registrada antes da coleta; T1 permanece confirmatório |
| 2026-10-28 | D1 restrito ao 2º turno (BUs do 1º turno não coletados) | O objeto do T1 é o 2º turno presidencial; T2 usa a totalização por seção do 1º turno (D2), que está em `votacao_secao_2026_BR.zip` | Nenhum sobre T1; T2 não usa BU |
| 2026-10-28 | D5 sem o ano de 2010 (arquivo `pesquisa_eleitoral_2010.zip` inexistente no portal do TSE, HTTP 404) e sem resultados das pesquisas (o registro do TSE contém instituto, metodologia e amostra, não os percentuais) | Disponibilidade da fonte | T5 precisará de fonte complementar para resultados e para 2010; a definir antes de rodar T5, com novo registro aqui |
| 2026-10-28 | D8: 1989 disponível só por UF (sem recorte município/zona no portal) | Disponibilidade da fonte | Nenhum sobre T6 (usa margens nacionais); 1989 não entra em controles municipais |
