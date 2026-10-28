# Auditoria estatística — 2º turno presidencial 2026

Execução do plano pré-registrado em [`PREREGISTRO.md`](PREREGISTRO.md) (v1.0, redigido em 2026-10-26, cópia byte a byte, SHA-256 `5a8dced7…3e42fd`). O pré-registro foi congelado no commit `abdc482`, antes de qualquer download. Alterações e detalhamentos posteriores estão em [`DESVIOS.md`](DESVIOS.md); resultados afetados por desvio são exploratórios.

## Status por etapa (Seção 8 do pré-registro)

| Etapa | Conteúdo | Status |
|-------|----------|--------|
| 1 | Congelar pré-registro em commit; `DESVIOS.md` vazio | concluída (2026-10-28) |
| 2 | Coleta D1–D8 com manifesto de hashes | concluída (2026-10-28) |
| 3 | T1 — verificação de BUs | concluída na amostra (2026-10-28): linha 1 |
| 4 | T5 e T6 — pesquisas e série histórica | pendente (T5 depende de fonte de resultados das pesquisas, ver `DESVIOS.md`) |
| 5 | T2 e T3 — pareamento e modelo espacial | pendente |
| 6 | T4 — dígitos (completude) | pendente |
| 7 | Consolidação e classificação A/B/C | pendente |
| 8 | Revisão adversarial externa | pendente |
| 9 | Publicação, incluindo testes negativos | pendente |

## Etapa 2 — coleta

Todos os arquivos estão registrados em [`data/raw/MANIFEST.csv`](data/raw/MANIFEST.csv) (URL, data/hora UTC, bytes, SHA-256). `src/00_manifesto.py` confere `data/raw` contra o manifesto; na última execução: 17.560 arquivos, 0 divergências. Resumo por fonte em [`output/tables/coleta_resumo_por_fonte.csv`](output/tables/coleta_resumo_por_fonte.csv).

| Fonte | Conteúdo coletado | Origem |
|---|---|---|
| D1 | Configuração de seções do 2º turno (quadro amostral) e `bu.dat` + `vota.vsc` de 6.025 seções sorteadas; especificação oficial do BU/assinatura | resultados.tse.jus.br, tse.jus.br |
| D2 | Votação por seção 2026 (Presidente) e por município/zona | cdn.tse.jus.br |
| D3 | Perfil do eleitorado por seção (27 UFs), por município/zona e por local de votação | cdn.tse.jus.br |
| D4 | Detalhe da apuração por seção 2026; perfil de comparecimento e abstenção | cdn.tse.jus.br |
| D5 | Registro de pesquisas 2014, 2018, 2022, 2026 | cdn.tse.jus.br |
| D6 | Censo 2022: agregados por município e setor (básico, alfabetização, demografia, renda do responsável) | ftp.ibge.gov.br |
| D7 | Malha municipal 2022 e malha de setores censitários 2022 | geoftp.ibge.gov.br |
| D8 | 1989 por UF; 1994–2022 por município/zona; 2014, 2018, 2022 por seção (controles do T3) | cdn.tse.jus.br |

Lacunas de disponibilidade (detalhes em `DESVIOS.md`): o portal não tem registro de pesquisas de 2010, e o registro do TSE não traz os resultados das pesquisas; 1989 só existe por UF.

## Etapa 3 — T1 (verificação criptográfica e reconciliação)

Desenho fixado antes do sorteio em [`docs/desenho_amostral_T1.md`](docs/desenho_amostral_T1.md). Amostra estratificada por UF × porte do município: universo de 517.179 seções, 81 estratos, n = 6.025 (semente 20261025). Resumo completo em [`output/tables/t1_resumo.md`](output/tables/t1_resumo.md); resultados por urna em `output/tables/t1_validacao_por_urna.csv` e `output/tables/t1_reconciliacao_por_urna.csv`.

| Métrica | Resultado |
|---|---|
| Seções sorteadas | 6.025 |
| Urnas com BU "Totalizado" verificadas | 5.692 |
| Seções agregadas (votam na urna da seção principal, sem BU próprio) | 205 |
| Seções sem BU "Totalizado" | 128 (127 com índice em estado "Recebido" em 28/10; 1 urna não instalada) |
| Falhas de assinatura | 0 de 5.692 (IC 95% Clopper-Pearson: 0 a 0,065%) |
| Urnas com divergência BU × totalização | 0 de 5.692 (IC 95%: 0 a 0,065%) |
| Votos conferidos | 1.459.681; soma das diferenças absolutas: 0 |
| Certificados das urnas | emitidos por AC UE2020 (2.371), AC UE2022 (2.196) e AC URNA (1.125), todos validados contra as AC raiz publicadas pelo TSE |

**Classificação (critério fixado no T1):** linha 1. Todas as assinaturas válidas e nenhuma divergência; H1 (divergência na contagem) rejeitada **no escopo amostrado**. Com n = 5.692 urnas, o resultado é compatível com uma proporção de urnas divergentes no universo de até 0,065% (limite superior do IC 95%). Não autoriza conclusão sobre urnas específicas não amostradas.

Complemento **exploratório** (fora da classificação, ver `DESVIOS.md`): as 127 seções em estado "Recebido" também foram verificadas. Nenhuma falha de assinatura e nenhuma divergência.

Testes de invariantes em `tests/`: o verificador rejeita BU, assinatura e certificado adulterados, e a reconciliação acusa divergências e ausências injetadas.

Fonte: TSE, arquivos de urna do 2º turno 2026 (pleito 3221) e votação por seção 2026 (`votacao_secao_2026_BR.zip`); IDs e hashes em `data/raw/MANIFEST.csv`. Estimativa amostral.

## Reprodução

```bash
python -m venv .venv && .venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python src/01_download.py lote
.venv/Scripts/python src/01_download.py bu-quadro
.venv/Scripts/python src/02_validate_bu.py sorteia
.venv/Scripts/python src/01_download.py bu-amostra
.venv/Scripts/python src/01_download.py bu-recebidos
.venv/Scripts/python src/00_manifesto.py
.venv/Scripts/python src/02_validate_bu.py valida
.venv/Scripts/python src/02_validate_bu.py valida-recebidos
.venv/Scripts/python src/02_validate_bu.py reconcilia
.venv/Scripts/python -m pytest tests
```

A especificação oficial (`data/raw/tse_doc/formato-arquivos-de-bu-rdv-e-assinatura-digital.zip`) precisa ser baixada por navegador, porque tse.jus.br responde 403 a clientes de linha de comando. Depois disso, ela é extraída em `data/processed/tse_spec/`.

## Espaço em disco

`data/raw` ocupa cerca de 8,8 GB. Os brutos não ficam no git: o manifesto permite baixá-los de novo e conferir os hashes. Quando o trabalho terminar, os brutos podem ser apagados.
