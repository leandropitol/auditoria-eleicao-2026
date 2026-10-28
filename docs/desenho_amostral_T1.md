# T1 — desenho amostral e regras operacionais

**Status:** fixado em 2026-10-28, **antes** do sorteio e do download de qualquer boletim de urna (BU). Detalha o que a Seção 3/T1 do `PREREGISTRO.md` deixa em aberto; não altera métricas nem critérios. O registro correspondente está em `DESVIOS.md`.

Já baixados neste momento: o pacote oficial de especificação do BU/assinatura (TSE) e a configuração de seções do pleito do 2º turno (quadro amostral). Nenhum arquivo de urna ou de totalização foi aberto.

## 1. Escopo

- Eleição: Eleição Ordinária Federal 2026, 2º turno (pleito TSE `3221`, eleição `6258`), cargo Presidente.
- Universo: todas as seções listadas nos arquivos `data/raw/D1/config/<uf>-p003221-cs.json` (27 UFs e exterior `ZZ`).
- O universo completo de BUs assinados do 2º turno (arquivos "transmitidos para totalização") passa de 100 GB (só SP: 25,8 GB). Por isso o T1 usa a amostra estratificada prevista no plano (meta n ≥ 5.000).

## 2. Estratos e alocação

- Estrato = UF (28, incluindo `ZZ`) × porte do município.
- Porte do município = número de seções do município no quadro amostral:
  - pequeno: até 30 seções;
  - médio: 31 a 300 seções;
  - grande: mais de 300 seções.
- Tamanho total planejado: n = 6.000 (margem sobre a meta de 5.000 para seções sem BU disponível).
- Alocação proporcional ao número de seções do estrato, com mínimo de 5 por estrato (ou o estrato inteiro, se tiver menos de 5): `n_h = max(min(N_h, 5), round(6000 · N_h / N))`. O n final realizado é reportado.
- Seleção: amostragem aleatória simples sem reposição dentro de cada estrato, com `numpy.random.default_rng(20261025)`, sobre o quadro ordenado por (uf, município, zona, seção) e estratos processados em ordem lexicográfica.
- Peso de cada seção: `w = N_h / n_h`.

## 3. Arquivos por seção

- Para cada seção sorteada: `aux.json` (índice de arquivos de urna) e, para cada entrada com estado `Totalizado`, os arquivos `bu.dat` e `vota.vsc` (arquivo de assinaturas).
- `rdv.dat` e `log.jez` não são baixados: o T1 trata da assinatura do BU, não do RDV nem do log.
- Seção sem entrada `Totalizado` (urna não instalada, apuração manual, BU não recebido etc.): classificada como "sem BU eletrônico totalizado", contada e reportada com o estado informado pelo TSE. Não entra no denominador da taxa de falha de assinatura.
- Seção com mais de uma entrada `Totalizado`: todas são verificadas e reportadas.

## 4. Verificação da assinatura (por BU)

Segue a lógica do script oficial `python/assinatura_hash.py` do pacote do TSE, restrita ao arquivo `bu.dat`. O BU é "assinatura válida" se e somente se todas as condições abaixo forem verdadeiras:

1. Para os envelopes `assinaturaSW` e `assinaturaHW` do `vota.vsc`: SHA-512 de `conteudoAutoAssinado` igual ao hash em `autoAssinado`.
2. SHA-512 do `bu.dat` igual ao hash listado para esse arquivo nos dois envelopes (SW e HW).
3. Certificado de hardware da urna (`assinaturaHW.informacaoChave`) com assinatura válida contra a chave da AC raiz indicada como emissora, entre as AC raiz publicadas pelo TSE no pacote oficial (`lib/mr_util.py`, `_AC_RAIZ_UE_PEMS`).
4. Assinatura do hash do `bu.dat` válida com a chave pública do certificado de hardware (ECDSA secp521r1 ou EdDSA Ed521, conforme o certificado).

Se um BU falhar, o arquivo é baixado uma segunda vez, em pasta separada, e os SHA-256 das duas cópias são comparados, para separar falha de transferência de falha no arquivo publicado. Toda falha é listada por seção.

## 5. Extração e reconciliação

- BU: `EntidadeEnvelopeGenerico.conteudo` → `EntidadeBoletimUrna`; resultado com `idEleicao = 6258`; cargo `cargoConstitucional = presidente`; votos por tipo (`nominal` por número do candidato, `branco`, `nulo`).
- Totalização (D2): `votacao_secao_2026_BR.zip`, linhas do 2º turno, cargo Presidente, mesma chave (UF, município, zona, seção); `NR_VOTAVEL` 95 = branco, 96 = nulo.
- Divergência na urna: qualquer diferença em qualquer votável (candidatos, branco, nulo), ou seção presente no BU e ausente na totalização (ou o inverso).
- Magnitude: soma de |BU − totalização| em votos, e a mesma soma dividida pelo total de votos do BU na urna (%).
- Direção: para cada urna divergente, diferença líquida (BU − totalização) da margem entre os dois candidatos.

## 6. Métricas e classificação (Seção 3/T1 do pré-registro)

- Taxa de falha de assinatura: amostral (com IC 95% de Clopper-Pearson) e estimada para o universo (ponderada por `w`).
- Nº de urnas com divergência e magnitude (lista completa).
- Classificação, aplicada nesta ordem:
  1. **Linha 1** — 100% das assinaturas válidas e zero divergência: "H1 rejeitada no escopo amostrado".
  2. **Linha 3** — divergências com direção consistente (teste binomial bilateral do sinal da diferença líquida da margem, α = 0,05, quando houver ≥ 1 urna divergente com diferença de margem ≠ 0) ou concentração espacial (teste exato de Fisher da distribuição por UF das urnas divergentes contra a distribuição da amostra, α = 0,05): "achado material".
  3. **Linha 2** — demais casos com divergências: compatível com erro operacional se o limite superior do IC 95% da proporção estimada de urnas divergentes no universo for < 0,01%; caso contrário, reportar que a amostra não permite enquadrar na linha 2 e listar as urnas.
- Falha de assinatura com divergência zero não se enquadra na linha 1: é reportada urna a urna, com o resultado da segunda cópia (Seção 4).
- Limite de resolução: com n ≈ 6.000, uma única urna divergente corresponde a ≈ 0,017% da amostra. Zero divergência na amostra dá limite superior do IC 95% de ≈ 0,05% para a proporção no universo (regra de três: 3/n). O resultado é válido para o escopo amostrado e não autoriza conclusão sobre urnas não amostradas além desse intervalo.
