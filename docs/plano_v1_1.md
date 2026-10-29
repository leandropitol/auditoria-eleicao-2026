# Plano da revisão v1.1 (resposta à revisão adversarial nº 1)

**Status:** redigido em 2026-10-29, **antes** de rodar qualquer análise nova. Ao ser commitado, este arquivo recebe carimbo temporal externo (OpenTimestamps, `docs/carimbos/`). Tudo o que segue é **exploratório**: não altera nenhuma classificação confirmatória (T1–T6) nem o desfecho da Etapa 7. O registro está em `DESVIOS.md`.

## Origem

Revisão crítica recebida em 2026-10-28/29 (resumo em `docs/revisao_etapa8.md`). Pontos acatados:
- (A) anterioridade do pré-registro sem prova externa;
- (B) detalhamento da amostra do T1;
- (C) transparência e robustez do modelo geográfico, incluindo o uso do Censo 2022 nos anos de controle;
- (D) cautela com a comparação internacional;
- (E) não independência das pesquisas;
- (3) alcance do veredito.

## 1. Anterioridade e carimbo temporal

- Fato a registrar no relatório: os commits foram enviados ao GitHub pela primeira vez em 2026-10-28T20:42:54Z (criação do repositório). Antes disso, as datas dos commits são locais e não constituem prova externa de anterioridade. A cadeia de hashes prova integridade a partir da publicação, não a ordem anterior dos eventos.
- Carimbo OpenTimestamps de: (i) este plano; (ii) um arquivo `docs/carimbos/estado_v1_0.txt` com o hash do commit publicado (`HEAD` atual), o SHA-256 do `PREREGISTRO.md` e o SHA-256 do `MANIFEST.csv`. O carimbo prova existência a partir de agora; não prova nada retroativamente.
- Regra daqui em diante: todo plano de análise nova é commitado e carimbado antes de ser executado.

## 2. Sensibilidades (exploratórias)

**T3 sem o Censo 2022.** Mesmo modelo misto, mesmos anos, só com os preditores de 1º turno e o intercepto aleatório de UF. Moran global e LISA com FDR (999 e 9.999 permutações, semente 20261025). Leitura: a conclusão "I de 2026 dentro da faixa de 2014–2022 e nenhum cluster exclusivo de 2026" se mantém ou não.

**T2 com especificações alternativas.** Mesmos critérios (a), (b), (c), FDR q = 0,05, 5 vizinhos e 999 permutações:
- S1: sem o perfil do eleitorado (D3), só 1º turno, abstenção, brancos e nulos e variações entre turnos, com efeito fixo de município, sem ponderação;
- S2: resposta em logit, `log(v13 / v22)`, ponderada pelos votos dos dois finalistas;
- S3: especificação ponderada da sensibilidade B, excluindo seções em locais cujo nome indica aldeia ou escola indígena (padrão `ALDEIA|INDÍGENA|TUXAUA`).

Para cada uma: número de seções anômalas, direção, agrupamento, votos envolvidos e **pior caso**.

**Pior caso (todas as versões).** `2 × soma dos votos válidos dos finalistas nas seções anômalas`, em % da margem oficial (4.430.191 votos). É a mudança máxima de margem se todos os votos de um candidato nessas seções fossem do outro.

**Distribuição das 461 seções (confirmatório).** Tabela por faixa de tamanho da seção, por faixa de |z| e por UF, mais a contagem com p antes e depois da correção.

## 3. Detalhamento do T1

- Memória de cálculo do intervalo: Clopper-Pearson exato, k = 0, n = 5.692, limite superior `1 − 0,025^(1/n)`. Também a versão ponderada pelos pesos amostrais, com o tamanho efetivo de Kish.
- Seções excluídas: as 205 agregadas (seção principal de cada uma e se essa principal está na amostra) e as 128 sem BU "Totalizado" (127 verificadas no complemento exploratório, 1 não instalada).
- Nota de escopo: a reconciliação BU × totalização não verifica se a urna registrou a intenção do eleitor.

## 4. Textos

- **Veredito:** "Desfecho B do plano. Os achados são localizados, numericamente irrelevantes e compatíveis com limitações do modelo; nenhum recebeu explicação causal definitiva." Mais a frase explícita: "Este trabalho não demonstra ausência de fraude; mostra ausência de divergência na amostra e padrões compatíveis com eleições anteriores."
- **T6:** substituir "cerca de 49%" por "da ordem de metade, com grande incerteza (IC 95%: 27% a 71%)", com a ressalva sobre não equivalência entre países e o n pequeno.
- **T5:** as 19 pesquisas não são observações independentes; os mecanismos do erro são um estudo à parte.
- Atualizar o relatório (.docx e `report.md`), o README, a imagem e o texto de divulgação.
