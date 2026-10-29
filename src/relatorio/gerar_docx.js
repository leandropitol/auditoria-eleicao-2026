// Relatório público (.docx) da auditoria. Todos os números vêm de output/relatorio/dados_relatorio.json,
// gerado por src/11_relatorio_publico.py a partir das saídas dos testes.
// Uso: node src/relatorio/gerar_docx.js

const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, Table, TableRow, TableCell, WidthType,
  ShadingType, BorderStyle, ImageRun, ExternalHyperlink, Footer, PageNumber, LevelFormat, PageBreak,
} = require("docx");

const RAIZ = path.resolve(__dirname, "..", "..");
const d = JSON.parse(fs.readFileSync(path.join(RAIZ, "output", "relatorio", "dados_relatorio.json"), "utf8"));
const REPO = d.repo;
const ARQ = (p) => `${REPO}/blob/main/${p}`;

const AZUL = "1F4E79", CINZA = "52514E", CLARO = "F2F4F7", BORDA = "D0D5DD", LARANJA_ESC = "B8481C";
const LARGURA = 9638; // A4 com margens de 2 cm, em DXA

const PARTICULAS = new Set(["da", "de", "do", "das", "dos", "e"]);
const titulo = (s) => s.toLowerCase().split(" ").map((w, i) => (i && PARTICULAS.has(w)) ? w : w[0].toUpperCase() + w.slice(1)).join(" ");
const N13 = titulo(d.nomes["13"]), N22 = titulo(d.nomes["22"]);

// --- construtores ------------------------------------------------------------------------------------
const t = (text, o = {}) => new TextRun({ text, ...o });
const b = (text, o = {}) => new TextRun({ text, bold: true, ...o });
const link = (text, url) => new ExternalHyperlink({ link: url, children: [new TextRun({ text, style: "Hyperlink" })] });
const P = (children, o = {}) => new Paragraph({ children: Array.isArray(children) ? children : [t(children)], spacing: { after: 140, line: 300 }, ...o });
const H1 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [t(text)], spacing: { before: 360, after: 160 } });
const H2 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [t(text)], spacing: { before: 240, after: 120 } });
const item = (children) => new Paragraph({ numbering: { reference: "marcadores", level: 0 }, children: Array.isArray(children) ? children : [t(children)], spacing: { after: 90, line: 290 } });
const legenda = (text) => new Paragraph({ children: [t(text, { italics: true, size: 18, color: CINZA })], spacing: { after: 220 } });

function figura(rel, largura, altura) {
  return new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { before: 120, after: 60 },
    children: [new ImageRun({ type: "png", data: fs.readFileSync(path.join(RAIZ, rel)), transformation: { width: largura, height: altura },
      altText: { title: "Gráfico", description: "Gráfico do relatório", name: path.basename(rel) } })],
  });
}

const borda = { style: BorderStyle.SINGLE, size: 4, color: BORDA };
const bordas = { top: borda, bottom: borda, left: borda, right: borda };
function tabela(cabecalho, linhas, larguras) {
  const cel = (conteudo, w, cab) => new TableCell({
    borders: bordas, width: { size: w, type: WidthType.DXA },
    shading: cab ? { fill: AZUL, type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: [new Paragraph({ children: (Array.isArray(conteudo) ? conteudo : [t(String(conteudo), { size: 18, bold: cab, color: cab ? "FFFFFF" : undefined })]) })],
  });
  return new Table({
    width: { size: LARGURA, type: WidthType.DXA }, columnWidths: larguras,
    rows: [new TableRow({ tableHeader: true, children: cabecalho.map((c, i) => cel(c, larguras[i], true)) }),
      ...linhas.map((l) => new TableRow({ children: l.map((c, i) => cel(c, larguras[i], false)) }))],
  });
}

function destaque(linhas) {
  // quadro de destaque: tabela de uma célula, fundo claro
  return new Table({
    width: { size: LARGURA, type: WidthType.DXA }, columnWidths: [LARGURA],
    rows: [new TableRow({ children: [new TableCell({
      width: { size: LARGURA, type: WidthType.DXA },
      borders: { top: { style: BorderStyle.SINGLE, size: 18, color: AZUL }, bottom: borda, left: borda, right: borda },
      shading: { fill: CLARO, type: ShadingType.CLEAR, color: "auto" },
      margins: { top: 140, bottom: 140, left: 200, right: 200 },
      children: linhas,
    })] })],
  });
}
const espaco = () => new Paragraph({ children: [], spacing: { after: 120 } });
const s = (x) => x; // marcador visual: valores vindos de `d`

// --- conteúdo ----------------------------------------------------------------------------------------
const c = [];

// capa
c.push(new Paragraph({ children: [t("AUDITORIA ESTATÍSTICA · DADOS PÚBLICOS", { bold: true, color: LARANJA_ESC, size: 20 })], spacing: { before: 600, after: 200 } }));
c.push(new Paragraph({ children: [t("O que os dados públicos dizem sobre o 2º turno presidencial de 2026", { bold: true, size: 52, color: AZUL, font: "Georgia" })], spacing: { after: 240, line: 360 } }));
c.push(new Paragraph({ children: [t("Boletins de urna, mapas, pesquisas e a virada entre turnos, examinados com plano, critérios e dados publicados", { size: 28, color: CINZA, font: "Georgia" })], spacing: { after: 360, line: 340 } }));
c.push(P([b("Leandro Marques Pitol"), t(` · versão 1.1, ${d.data_v11} (v1.0: ${d.data_relatorio})`)]));
c.push(P([t("Versão preliminar, revisada após a primeira revisão crítica e aberta a novas revisões", { italics: true, color: CINZA })]));
c.push(espaco());
c.push(destaque([
  P([b("Tudo o que está neste relatório pode ser verificado. ")]),
  P([t("Código, tabelas, plano pré-registrado, registro de desvios e a lista de cada arquivo baixado com sua impressão digital estão em: ")]),
  P([link(REPO, REPO)]),
  P([t("Os números deste documento são gerados por script a partir dessas tabelas, sem digitação manual.", { size: 18, color: CINZA })], { spacing: { after: 0 } }),
]));
c.push(new Paragraph({ children: [new PageBreak()] }));

// resumo
c.push(H1("Em resumo"));
c.push(P(`Após o 2º turno presidencial de 25 de outubro de 2026, em que ${N13} (número 13) venceu ${N22} (número 22) depois de terminar o 1º turno em segundo lugar, circularam alegações de que o resultado seria "milagroso" ou estatisticamente improvável. Este trabalho testou essas ideias com dados públicos do TSE e do IBGE, seguindo um plano escrito antes da coleta (o histórico do Git registra essa ordem, mas sem prova externa; veja a seção 2.1). Os principais resultados:`));
c.push(item([b("A contagem bateu na amostra. "), t(`Em ${s(d.t1.verificadas)} urnas sorteadas em todo o país, todas as assinaturas digitais dos boletins de urna foram validadas e a soma dos votos coincidiu com o resultado oficial: ${d.t1.divergencias} divergências em ${d.t1.votos} votos conferidos. Por ser amostra, isso limita (não elimina) a possibilidade de urnas com problema no país: no máximo ${d.v11.t1.ic_sup}%, com 95% de confiança.`)]));
c.push(item([b("O mapa não tem nada de novo. "), t(`O padrão geográfico do que os modelos não conseguem explicar em 2026 está dentro do observado em 2014, 2018 e 2022, e nenhum aglomerado de municípios aparece apenas em 2026. O resultado se mantém quando o modelo é refeito sem os dados do Censo.`)]));
c.push(item([b("Há seções atípicas, e nem todas estão explicadas, mas nenhuma conta chega perto da margem. "), t(`No modelo principal, ${d.t2.anomalas} seções fogem do previsto, concentradas em seções pequenas e aldeias indígenas; no pior caso, mexeriam em ${d.v11.pior_conf}% da margem. Uma especificação alternativa aponta ${d.v11.s2.s2b_n} seções em redutos do 13, ainda sem explicação demonstrada (pior caso: ${d.v11.especificacoes[2].pior}% da margem).`)]));
c.push(item([b("As pesquisas erraram todas para o mesmo lado. "), t(`As ${d.t5.n26} pesquisas finais superestimaram o candidato 22, em média por ${d.t5.erro_medio} pontos na margem entre os dois. Como os institutos compartilham métodos e vieses, isso não equivale a ${d.t5.n26} erros independentes.`)]));
c.push(item([b("A virada não é rara para uma vantagem tão pequena. "), t(`O candidato 22 liderou o 1º turno por ${d.votos_1t.margem_pp} ponto percentual. Em ${d.t6.casos} segundos turnos de seis países, viradas com vantagem desse tamanho acontecem em algo da ordem de metade dos casos, com grande incerteza (de ${d.t6.ic}%). O que foi excepcional foi a magnitude: o 13 ficou com ${d.virada.obtida}% dos votos novos entre os turnos, a maior parcela da série brasileira.`)]));
c.push(item([b("Veredito, pelas regras fixadas antes: "), t(`desfecho B do plano. Os achados são localizados e não têm tamanho para mudar o resultado nacional; são compatíveis com limitações do modelo, mas nem todos receberam explicação causal demonstrada.`)]));
c.push(item([b("O que este trabalho não demonstra. "), t(`Ele não prova ausência de fraude. Mostra que não houve divergência de contagem na amostra examinada e que os padrões estatísticos de 2026 são compatíveis com os de eleições anteriores.`)]));

// por que
c.push(H1("1. A pergunta e as regras do jogo"));
c.push(P(`A pergunta central foi escrita assim, antes de olhar os dados: o resultado do 2º turno de 2026 é consistente com o processo eleitoral tal como documentado nos registros públicos, ou existem anomalias localizadas que fatores demográficos, políticos e o erro amostral conhecido não explicam?`));
c.push(P(`O estudo não parte do pressuposto de que houve fraude, nem de que não houve. Para impedir que o resultado fosse moldado pelo que se desejava encontrar, o trabalho seguiu quatro regras:`));
c.push(item([b("Plano escrito antes dos dados. "), t("Hipóteses, testes, limiares e critérios de decisão foram registrados no Git antes do primeiro download, segundo as datas do histórico. A seção 2.1 explica o limite dessa prova e o carimbo externo adotado depois.")]));
c.push(item([b("Nada de inventar métrica depois de ver o resultado. "), t(`Qualquer ajuste posterior foi anotado, com data e justificativa, num registro público de desvios (${d.n_desvios} entradas). Resultados afetados são marcados como exploratórios e não entram no veredito.`)]));
c.push(item([b("Todos os testes são publicados, inclusive os que não acharam nada. "), t("Um estudo que só divulga o que confirma a suspeita inicial é advocacia, não investigação.")]));
c.push(item([b("\"Não consigo explicar\" não é \"foi fraudado\". "), t("Quando algo fica sem explicação, a hipótese padrão é erro do modelo estatístico. Uma alegação de fraude exigiria apontar urnas específicas, com achado reproduzível.")]));
c.push(P(`Os testes foram executados em ordem de poder de prova: primeiro a conferência dos boletins de urna (o único que trata diretamente da contagem), depois os padrões espaciais, as pesquisas, a série histórica e, por completude, os testes de dígitos.`));

// cadeia de custódia
c.push(H1("2. Cadeia de custódia: como saber que nada foi alterado"));
c.push(P(`Cadeia de custódia é o registro que permite a qualquer pessoa reconstituir o caminho dos dados, da fonte oficial até cada número publicado, e conferir que nada foi trocado no meio do caminho. Neste trabalho, ela tem cinco elos.`));
c.push(H2("2.1 O plano e a ordem dos eventos: o que está provado e o que não está"));
c.push(P([t("O documento de pré-registro foi copiado sem alterações e registrado no commit "), link(d.commit_preregistro.hash, d.commit_preregistro.url), t(` (${d.commit_preregistro.data}, horário do computador do autor), antes do primeiro download segundo o histórico do Git. A impressão digital (SHA-256) do arquivo `), link("PREREGISTRO.md", ARQ("PREREGISTRO.md")), t(" é:")]));
c.push(P([t(d.sha_preregistro, { font: "Consolas", size: 17 })]));
c.push(destaque([P([b("Limite da prova. "), t(`O horário de um commit é registrado pelo próprio computador de quem o faz e pode ser informado livremente. Os commits deste trabalho só chegaram ao GitHub em ${d.v11.repo_criado_utc}, de uma vez. Por isso não existe prova externa de que o plano foi escrito antes da coleta. A cadeia de hashes prova que nada foi alterado depois de publicado, mas não prova a ordem dos eventos anteriores. Essa limitação foi apontada na primeira revisão crítica e é aceita aqui.`)], { spacing: { after: 0 } })]));
c.push(espaco());
c.push(P(`O que foi feito a partir da revisão: os planos de toda análise nova passaram a receber carimbo temporal externo (OpenTimestamps, ancorado na rede Bitcoin) antes de serem executados. Qualquer pessoa pode conferir esses carimbos em opentimestamps.org. Foram carimbados:`));
for (const x of d.v11.carimbos) c.push(item([link(x.arquivo, ARQ(x.arquivo)), t(` (+ .ots), SHA-256 ${x.sha256.slice(0, 16)}…`, { size: 18 })]));
c.push(H2("2.2 Cada arquivo baixado tem impressão digital"));
c.push(P([t(`Os ${d.n_arquivos_manifesto} arquivos obtidos das fontes oficiais estão listados no `), link("manifesto", ARQ("data/raw/MANIFEST.csv")), t(", com endereço de origem, data e hora do acesso, tamanho e código SHA-256. Se um único byte de um arquivo mudar, o código muda completamente. Os dados brutos não ficam no repositório por causa do volume, mas podem ser baixados de novo e conferidos contra o manifesto.")]));
c.push(tabela(["Fonte", "Conteúdo", "Arquivos", "GB", "Acesso"],
  d.coleta.map((r) => [r.fonte, {
    D1: "Boletins de urna assinados (amostra) e especificação oficial do TSE",
    D2: "Resultados oficiais por seção e por município (TSE)",
    D3: "Perfil do eleitorado por seção e locais de votação (TSE)",
    D4: "Comparecimento, abstenção, brancos e nulos por seção (TSE)",
    D5: "Registro de pesquisas eleitorais (TSE)",
    D6: "Censo 2022: renda, alfabetização, idade, urbanização (IBGE)",
    D7: "Malhas municipal e de setores censitários (IBGE)",
    D8: "Resultados presidenciais 1989–2022 (TSE)",
    D9: "Resultados de pesquisas, compilação com revisão fixada (Wikipedia)",
    D10: "Segundos turnos de outros países, revisão fixada (Wikipedia)",
  }[r.fonte] || "", r.arquivos, r.gb, r.acesso]),
  [700, 5338, 1100, 1000, 1500]));
c.push(legenda("Fonte: data/raw/MANIFEST.csv. D9 e D10 são fontes secundárias, usadas apenas nos testes de menor poder de prova."));
c.push(H2("2.3 Os dados brutos nunca foram editados"));
c.push(P(`Os arquivos originais ficam numa pasta tratada como imutável. Toda transformação ocorre em scripts versionados, que leem os brutos e gravam resultados em outra pasta. Um verificador automático confere os ${d.n_arquivos_manifesto} arquivos contra o manifesto; na última execução, não houve nenhuma divergência. Na revisão 1.1, os brutos já apagados para liberar espaço precisaram ser baixados de novo das fontes oficiais: ${d.v11.rebaixados.filter((x) => x.confere).length} de ${d.v11.rebaixados.length} conferiram byte a byte com o SHA-256 registrado um dia antes, o que mostra na prática que a cadeia pode ser reconstruída.`));
c.push(H2("2.4 Cada mudança de rota foi anotada"));
c.push(P([t(`O `), link("registro de desvios", ARQ("DESVIOS.md")), t(` tem ${d.n_desvios} entradas. Entre elas estão os detalhes operacionais que o plano deixava em aberto (fixados antes de cada etapa), falhas de disponibilidade das fontes, correções de erros encontrados durante a análise e análises adicionais pedidas depois, todas marcadas como exploratórias.`)]));
c.push(H2("2.5 Linha do tempo pública"));
c.push(P("Cada etapa corresponde a um commit público, com data e hora. A ordem dos eventos pode ser conferida diretamente no GitHub:"));
c.push(tabela(["Commit", "Data (UTC−3)", "O que foi registrado"],
  d.commits.map((x) => [[link(x.hash, x.url)], x.data, x.mensagem]), [1100, 1900, 6638]));
c.push(legenda("Clique no identificador para abrir o commit. A data é a do registro no Git; o histórico não foi reescrito."));

// T1
c.push(H1("3. Os votos foram contados corretamente?"));
c.push(P(`Ao fim da votação, cada urna imprime e grava o boletim de urna (BU), com o total de votos de cada candidato naquela seção. O arquivo é assinado digitalmente pela própria urna, e o TSE o publica. Se alguém alterasse os votos depois que saíram da urna, ou se a totalização somasse errado, apareceria uma de duas coisas: uma assinatura inválida ou uma diferença entre o boletim e o resultado oficial daquela seção.`));
c.push(P(`O universo tem ${d.t1.universo} seções. Como o pacote completo de boletins assinados soma dezenas de gigabytes (só o de São Paulo tem cerca de 26 GB), o plano previa uma amostra aleatória de pelo menos 5 mil urnas, estratificada por estado e porte de município. Foram sorteadas ${d.t1.sorteadas} seções, com semente aleatória registrada antes do sorteio. Delas, ${d.t1.agregadas} eram seções agregadas (votam na urna de outra seção) e ${d.t1.sem_bu} não tinham boletim marcado como totalizado no dia da coleta (${d.v11.t1.recebidos} com boletim em estado "Recebido", verificados à parte, e ${d.v11.t1.nao_instalada} urna não instalada). Em nenhuma das ${d.t1.agregadas} agregadas a seção principal foi sorteada (${d.v11.t1.agregadas_principal}), então os votos delas estão em boletins que não foram verificados.`));
c.push(tabela(["O que foi verificado", "Resultado"], [
  ["Urnas com boletim verificado", d.t1.verificadas],
  ["Assinaturas digitais inválidas", String(d.t1.falhas)],
  ["Urnas com diferença entre boletim e resultado oficial", String(d.t1.divergencias)],
  ["Votos conferidos um a um", d.t1.votos],
  ["Complemento exploratório (boletins em estado \"Recebido\")", `${d.t1.recebidos} verificados, nenhuma falha, nenhuma diferença`],
], [6138, 3500]));
c.push(espaco());
c.push(P(`A verificação usou a especificação e os scripts oficiais publicados pelo TSE, incluindo os certificados raiz das urnas. Para garantir que o verificador não aprovava tudo automaticamente, testes adulteraram de propósito um boletim, uma assinatura e um certificado: os três foram rejeitados.`));
c.push(destaque([P([b("O que isso significa. "), t(`Pelo critério fixado antes, a hipótese de fraude na contagem fica rejeitada no escopo amostrado. Como é uma amostra, o resultado é compatível com, no máximo, ${d.v11.t1.ic_sup}% de urnas divergentes no país inteiro. A conta: com zero divergências em n = ${d.t1.verificadas} urnas, o limite superior do intervalo exato de Clopper-Pearson de 95% é 1 − 0,025^(1/n); levando em conta os pesos da amostra estratificada (tamanho efetivo de ${d.v11.t1.n_eff}), fica em ${d.v11.t1.ic_pond}%. O teste não autoriza afirmar nada sobre uma urna específica que não foi sorteada. E há um limite de escopo: a reconciliação mostra que o boletim e a totalização coincidem, não que a urna registrou exatamente a intenção de cada eleitor; essa é outra questão, que este teste não cobre.`)], { spacing: { after: 0 } })]));

// T3 e T2
c.push(H1("4. Há algum padrão geográfico fora do comum?"));
c.push(P(`Uma fraude que favorecesse um candidato em certas regiões deixaria marcas no mapa: municípios vizinhos com votação acima ou abaixo do esperado, formando aglomerados que não existiam em eleições anteriores. Para procurar essas marcas, um modelo estatístico previu a votação de cada município no 2º turno a partir do 1º turno, da renda, da alfabetização, da urbanização e da idade da população. Depois, examinou-se onde o modelo erra.`));
c.push(H2("4.1 Municípios (2014 a 2026)"));
c.push(P(`O mesmo modelo foi aplicado a 2014, 2018, 2022 e 2026, para que as eleições anteriores servissem de comparação. Erros do modelo sempre se agrupam um pouco no mapa, porque vizinhos votam parecido. A medida desse agrupamento (I de Moran) foi de ${d.t3.I["2014"]} em 2014, ${d.t3.I["2018"]} em 2018, ${d.t3.I["2022"]} em 2022 e ${d.t3.I["2026"]} em 2026: dentro da faixa histórica.`));
c.push(P(`A busca por aglomerados locais, com correção para as milhares de comparações simultâneas, não encontrou nenhum município em aglomerado em 2026. Numa versão mais sensível do teste (9.999 sorteios em vez de 999), as eleições de 2014 e 2022 mostraram ${d.t3.clusters_9999["2014"]} e ${d.t3.clusters_9999["2022"]} municípios em aglomerado, e 2026 continuou com ${d.t3.clusters_9999["2026"]}. Pelo critério do plano: nada anômalo.`));
c.push(P(`O modelo usa dados do Censo 2022 também para 2014 e 2018, o que poderia distorcer a comparação. Para testar isso (análise exploratória da revisão 1.1), o modelo foi refeito só com os resultados do 1º turno, sem nenhum dado do Censo. O I de Moran ficou em ${d.v11.t3_sem_censo["2014"].I} (2014), ${d.v11.t3_sem_censo["2018"].I} (2018), ${d.v11.t3_sem_censo["2022"].I} (2022) e ${d.v11.t3_sem_censo["2026"].I} (2026), de novo dentro da faixa; 2026 teve ${d.v11.t3_sem_censo["2026"].cl9999} municípios em aglomerado, contra ${d.v11.t3_sem_censo["2014"].cl9999} em 2014 e ${d.v11.t3_sem_censo["2022"].cl9999} em 2022. A conclusão não depende do Censo.`));
c.push(H2("4.2 Seções eleitorais (2026)"));
c.push(P(`O mesmo raciocínio foi aplicado às ${d.t2.secoes} seções do país, comparando cada uma com as do mesmo município e levando em conta o perfil de quem vota nela (idade, sexo, escolaridade). ${d.t2.anomalas} seções (menos de 0,1%) tiveram resultado fora do esperado; ${d.t2.pos} acima do previsto para o 13 e ${d.t2.neg} abaixo. Elas são vizinhas umas das outras com mais frequência do que o acaso explicaria. Pelos critérios fixados, isso conta como "achado a localizar". A investigação, porém, aponta para uma limitação do modelo:`));
c.push(item(`${d.t2.pequenas} das ${d.t2.anomalas} estão entre as seções com menos eleitores, onde a proporção de votos oscila muito mais e o modelo, sem ponderar pelo tamanho, as trata como se fossem iguais às grandes;`));
c.push(item(`${d.t2.indigenas} ficam em aldeias ou escolas indígenas, contextos de voto mais coeso: são ${d.indigena.pct_anomalas}% das seções atípicas, contra ${d.indigena.pct_todas}% do total de seções (cerca de ${d.indigena.razao} vezes mais);`));
c.push(item(`quando o modelo pondera pelo tamanho da seção (análise exploratória), sobram ${d.t2.pond_anomalas} seções, e o único agrupamento é um mesmo local de votação em São Paulo.`));
c.push(P("Quanto menor a seção, maior a chance de ela aparecer como atípica:"));
c.push(tabela(["Votos na seção (2º turno)", "Seções no país", "Seções atípicas", "% atípicas na faixa"],
  d.v11.por_tamanho.map((r) => [r.faixa, r.secoes, r.anomalas, r.pct]), [2900, 2300, 2200, 2238]));
c.push(legenda("Fonte: output/tables/v11_t2_anomalas_por_tamanho.csv. A lista completa das seções, com o desvio e os p-valores antes e depois da correção, está em output/tables/t2_secoes_anomalas.csv."));
c.push(destaque([P([b("O tamanho importa. "), t(`As ${d.t2.anomalas} seções somam ${d.t2.votos} votos. No pior caso imaginável, em que todos os votos de um candidato nelas fossem na verdade do outro, a margem nacional mudaria ${d.v11.pior_conf}%, e ${d.v11.pior_pond}% na versão ponderada. A margem oficial é de ${d.votos_2t.margem} votos; nenhum desses cenários chega perto de alterar o resultado. O plano exige que achados assim sejam reportados como estatisticamente detectáveis, mas numericamente irrelevantes.`)], { spacing: { after: 0 } })]));
c.push(H2("4.3 Outras formas de montar o modelo (revisão 1.1, exploratório)"));
c.push(P("Para testar se a conclusão depende das escolhas do modelo, a análise das seções foi refeita de quatro outras maneiras, definidas e carimbadas antes de rodar:"));
c.push(tabela(["Especificação", "Seções atípicas", "Acima / abaixo do previsto para o 13", "Agrupadas?", "Direcionais?", "Pior caso (% da margem)"],
  d.v11.especificacoes.map((r) => [r.nome, r.anomalas, r.direcao, r.agrupada, r.direcional, r.pior]), [2700, 1300, 1700, 1200, 1200, 1538]));
c.push(espaco());
c.push(P(`Sem o perfil do eleitorado, o quadro é parecido com o principal. Excluindo os locais indígenas, sobram poucas seções, e elas deixam de apontar numa direção predominante, o que apoia a explicação das aldeias. As duas versões em escala logit, porém, apontam muito mais seções. A versão planejada tinha um erro de especificação reconhecido, e foi corrigida por um adendo carimbado antes da nova rodada. Mesmo corrigida, ela indica ${d.v11.s2.s2b_n} seções, ${d.v11.s2.acima90_pct_anomalas_s2b}% delas em redutos onde o 13 teve mais de 90% dos votos (faixa que reúne só ${d.v11.s2.acima90_pct_secoes}% das seções do país).`));
c.push(P(`O que se sabe dessas seções: o 13 já tinha, na mediana, ${d.v11.s2.s2b_t1}% dos votos nelas no 1º turno e passou a ${d.v11.s2.s2b_y}% no 2º; ficam sobretudo em ${d.v11.s2.s2b_ufs}; ${d.v11.s2.s2b_indigena}% estão em locais indígenas. O ganho entre turnos nelas (+${d.v11.s2.s2b_ganho} pontos na mediana) é o mesmo observado no conjunto das ${d.v11.s2.acima90_n} seções em que o 13 passou de 90% (+${d.v11.s2.acima90_ganho}). Isso é compatível com um efeito da escala logit, que amplia diferenças perto de 100%. A hipótese, porém, não foi testada formalmente, e o resultado fica registrado como não explicado. Mesmo no pior caso (${d.v11.especificacoes[2].pior}% da margem), ele não alcança a diferença entre os candidatos.`));

// T4
c.push(H1("5. E a \"lei de Benford\"?"));
c.push(P(`Testes que olham a frequência dos dígitos nas contagens (lei de Benford, último dígito, múltiplos de 5 e de 10) são populares em discussões sobre eleições, e por isso foram incluídos. Mas o plano registrou de antemão que eles não valem como prova: o número de votos por urna tem faixa estreita e teto fixo (o número de eleitores da seção), condição em que a lei de Benford não se aplica e acusa "desvio" mesmo em eleições sem problema algum.`));
c.push(P(`Foi exatamente o que aconteceu: o teste acusou desvio em todos os anos, inclusive 2014, 2018 e 2022. O tamanho do desvio em 2026 (${d.t4.mad26}, na medida usada) ficou dentro da faixa das eleições anteriores (${d.t4.madctrl}). Os últimos dígitos de 2026 estão até mais próximos do esperado do que nos anos anteriores. Este teste não é usado como evidência em nenhum sentido.`));

// T5
c.push(H1("6. As pesquisas erraram?"));
c.push(P(`Sim, e todas para o mesmo lado. As ${d.t5.n26} pesquisas finais do 2º turno de 2026 mostravam o candidato 22 à frente em ${d.pesquisas_22_frente} casos e o 13 ligeiramente à frente em ${d.pesquisas_13_frente}. No resultado oficial, a vantagem do 13 foi maior do que qualquer pesquisa indicava. Medido na margem entre os dois candidatos (a forma correta, já que o erro da diferença é cerca do dobro do erro de cada percentual), o erro foi de ${d.t5.erro_min} a ${d.t5.erro_max} pontos, com média de ${d.t5.erro_medio}.`));
c.push(figura(d.figuras.t5, 620, 258));
c.push(legenda(`Erro de cada pesquisa final na margem entre os dois candidatos, por eleição (cada ponto é um instituto; o traço preto é a média). Médias: 2010 ${d.t5.media_por_ano["2010"]}; 2014 ${d.t5.media_por_ano["2014"]}; 2018 ${d.t5.media_por_ano["2018"]}; 2022 ${d.t5.media_por_ano["2022"]}; 2026 ${d.t5.media_por_ano["2026"]} pontos. Fonte: resultados das pesquisas compilados na Wikipedia (revisões fixadas), cruzados com o registro do TSE; resultados oficiais do TSE.`));
c.push(P(`O plano previa um critério objetivo: se o erro de 2026 de cada instituto ficasse dentro do que o próprio instituto já havia errado antes, a tese de "improbabilidade estatística" estaria refutada. Isso só ocorreu com ${d.t5.dentro} dos ${d.t5.com_hist} institutos que têm histórico. Por esse critério, o T5 não refuta a alegação. Há, porém, três ressalvas importantes:`));
c.push(item("a maioria dos institutos tem apenas uma a quatro eleições de histórico, base curta para definir o que é \"normal\";"));
c.push(item(`na comparação com todos os erros de 2010 a 2022 juntos, os de 2026 ficam dentro da faixa já observada, e a média de 2026 é da mesma ordem da de 2018 (${d.t5.media_por_ano["2018"]} pontos);`));
c.push(item("erros que vão todos para o mesmo lado indicam viés comum de método (quem responde, como se pondera, quem decide votar), algo documentado em várias eleições. A margem de erro divulgada cobre apenas o acaso da amostra, não esses vieses."));
c.push(P("Em resumo, as pesquisas erraram mais do que costumam errar, e na mesma direção. Dezenove pesquisas, porém, não são dezenove observações independentes: institutos compartilham métodos, cadastros, formas de ponderação e dificuldades de amostragem. Entender o mecanismo (não resposta, ponderação, decisão tardia, diferença entre comparecimento projetado e real) exigiria os microdados dos institutos, que não são públicos, e fica como estudo à parte. Esse é um problema de medição das pesquisas e não diz nada, por si só, sobre a apuração dos votos."));

// T6 e virada
c.push(H1("7. A virada foi \"milagrosa\"?"));
c.push(P(`Antes de responder, um cuidado de método. Calcular a probabilidade de um resultado específico depois de vê-lo é o chamado "erro do atirador texano": quem dispara contra um celeiro e desenha o alvo ao redor dos tiros sempre parece um atirador perfeito. Qualquer desfecho exato é improvável visto de antes. A pergunta que faz sentido é outra: com uma vantagem desse tamanho no 1º turno, viradas são raras ou comuns?`));
c.push(H2("7.1 Viradas são comuns quando a vantagem é pequena"));
c.push(P(`O Brasil teve sete 2ºs turnos presidenciais antes de 2026, sem nenhuma virada. Isso parece impressionante, mas a vantagem do líder nesses casos variou de ${d.t6.br_min} a ${d.t6.br_max} pontos. Em 2026, foi de ${d.votos_1t.margem_pp} ponto (${d.votos_1t.pct22}% contra ${d.votos_1t.pct13}% dos votos válidos), a menor da série. Para ter uma base comparável, o estudo reuniu ${d.t6.casos} segundos turnos presidenciais do Brasil, França, Chile, Colômbia, Peru e Argentina.`));
c.push(figura(d.figuras.t6, 620, 250));
c.push(legenda(`Cada ponto é um 2º turno presidencial (Brasil 1989–2022 e cinco outros países), posicionado pela vantagem do 1º colocado no 1º turno. Fonte: TSE; Wikipedia com revisões fixadas para os outros países.`));
c.push(P(`Na base, houve ${d.t6.reversoes} viradas em ${d.t6.casos} casos, concentradas nas vantagens pequenas. Um modelo estatístico estima que, com vantagem de ${d.votos_1t.margem_pp} ponto, a chance de virada é da ordem de metade (estimativa central de ${d.t6.p}%), mas com grande incerteza: o intervalo de 95% vai de ${d.t6.ic}%. Entre os dez casos de vantagem mais parecida, houve ${d.t6.viz.split(" / ")[0]} viradas. Duas ressalvas: eleições de países diferentes não são observações equivalentes (sistemas partidários, regras e eleitorados diferem), e ${d.t6.casos} casos são uma base pequena. O número não deve ser lido como probabilidade precisa; o que ele indica é que viradas com vantagens desse tamanho não são raras.`));
c.push(H2("7.2 O que foi fora do padrão: o tamanho do ganho (análise exploratória)"));
c.push(P(`Esta parte foi pedida depois de vistos os resultados anteriores e está marcada como exploratória: descreve a virada, mas não entra no veredito. Entre os dois turnos, os dois finalistas somaram ${d.virada.novos_mi} milhões de votos a mais. As contas oficiais mostram de onde veio esse total: ${d.virada.demais_mi} milhões tinham ido no 1º turno para os candidatos eliminados, ${d.virada.comp_mi} milhões vieram do aumento do comparecimento e ${d.virada.bn_mi} milhão veio da redução de brancos e nulos. Desse total, ${d.virada.ganho13_mi} milhões foram para o 13 e ${d.virada.ganho22_mi} milhões para o 22.`));
c.push(figura(d.figuras.virada, 620, 284));
c.push(legenda(`Parcela dos votos novos dos dois finalistas que o 2º colocado do 1º turno precisava obter para virar (azul) e a que efetivamente obteve (laranja), em cada 2º turno brasileiro. 2006 fica fora da escala porque o 2º colocado perdeu votos entre os turnos. Fonte: TSE.`));
c.push(P(`Para virar em 2026, o 13 precisava ficar com ${d.virada.necessaria}% desses votos novos, a menor exigência da história (nas eleições anteriores, entre ${d.virada.nec_min_hist}% e ${d.virada.nec_max_hist}%). Ele obteve ${d.virada.obtida}%, a maior parcela da série (em 2022 o 2º colocado obtivera ${d.virada.obtida_2022}%, e em 2018, ${d.virada.obtida_2018}%). Medida de outra forma, a perda de vantagem do líder entre os turnos (${d.virada.desloc} pontos) foi menor do que em ${d.virada.desloc_maiores} dos ${d.virada.desloc_total} segundos turnos da base.`));
c.push(destaque([P([b("Em uma frase. "), t(`A virada era a mais fácil da série, porque a vantagem inicial era a menor já registrada; o desempenho do 2º colocado entre os votos novos foi o melhor da série, cerca de quatro pontos acima de 2022; e as pesquisas não captaram esse movimento. É um resultado fora do comum na magnitude, não um evento implausível. Os números agregados não permitem dizer de quem, individualmente, vieram os votos.`)], { spacing: { after: 0 } })]));

// veredito
c.push(H1("8. O veredito, pelas regras fixadas antes"));
c.push(P("O plano definiu três desfechos possíveis, com critérios escritos antes da análise:"));
c.push(tabela(["Desfecho", "Condição (pré-registrada)", "Situação"], [
  ["A — nada anômalo", "Contagem reconcilia; mapa dentro da faixa histórica; erro das pesquisas dentro do padrão de cada instituto", "Não atendido: pesquisas fora do padrão por instituto e achado formal nas seções"],
  [[b("B — anomalia com causa mundana", { size: 18 })], "Achado localizado, explicável por erro operacional, particularidade regional ou limitação do modelo, sem tamanho para mudar o resultado", [b("Atendido pelos critérios fixados (ver ressalva abaixo)", { size: 18 })]],
  ["C — anomalia inexplicada", "Achado material (capaz de alterar o resultado), localizável, direcional, reprodutível e que sobreviva à correção para múltiplos testes", `Não atendido: no pior caso, o achado principal mexeria em ${d.v11.pior_conf}% da margem (${d.v11.especificacoes[2].pior}% na especificação alternativa mais desfavorável)`],
], [2300, 4200, 3138]));
c.push(espaco());
c.push(P(`Desfecho B, com uma ressalva de leitura: o nome do desfecho, "anomalia com causa mundana", vem do plano, mas não deve ser lido como se todas as anomalias tivessem explicação causal definitiva. Os achados são localizados, numericamente irrelevantes para o resultado e compatíveis com limitações do modelo; parte deles (a especificação logit da seção 4.3) segue sem explicação demonstrada. O plano também determina que nenhum desfecho autoriza conclusão nacional baseada só em raciocínio agregado: uma alegação formal precisaria apontar urnas específicas, e nenhuma urna com divergência de contagem foi encontrada.`));
c.push(destaque([P([b("O alcance das conclusões. "), t("Há três afirmações diferentes. (1) Não houve divergência de contagem na amostra: demonstrado. (2) Os padrões estatísticos de 2026 são compatíveis com os de eleições anteriores: sustentado, com as ressalvas acima. (3) Não houve fraude: este trabalho não tem capacidade para demonstrar isso, e não afirma.")], { spacing: { after: 0 } })]));

// limites
c.push(H1("9. O que este trabalho não mostra"));
c.push(item(`Não há prova externa de que o pré-registro original antecede a coleta (seção 2.1). Desde a revisão 1.1, os planos novos são carimbados externamente antes de executados.`));
c.push(item(`A conferência de boletins é amostral (${d.t1.verificadas} urnas). Ela limita a proporção possível de urnas com problema, mas não examina cada urna do país; os votos das ${d.t1.agregadas} seções agregadas sorteadas não foram verificados; e ela não cobre a correspondência entre a intenção do eleitor e o registro na urna.`));
c.push(item(`Uma especificação alternativa do modelo de seções (seção 4.3) aponta ${d.v11.s2.s2b_n} seções em redutos do 13 que seguem sem explicação demonstrada.`));
c.push(item("Os percentuais das pesquisas e os resultados de outros países vêm de compilações da Wikipedia, com versões fixadas e cruzadas com o registro do TSE quando possível. Valores extremos devem ser conferidos nas fontes primárias."));
c.push(item("O modelo espacial foi aplicado por município, e não por seção como previa o plano, porque não há dados por seção para os anos de comparação. A mudança está registrada."));
c.push(item("Relatos de coação de eleitores (por exemplo, idosos acompanhados na cabine) não entram como métrica. Vídeos compartilhados não formam amostra; cada caso deve ser denunciado individualmente ao Ministério Público Eleitoral."));
c.push(item("Dados agregados não revelam o voto de ninguém. Os fluxos entre turnos descritos aqui são compatíveis com os totais, não comprovam transferência individual de votos."));
c.push(item("Esta é uma versão preliminar. A primeira revisão crítica foi incorporada (seção 11); novas revisões continuam bem-vindas, e toda correção é registrada publicamente."));

// verificar
c.push(H1("10. Verifique você mesmo"));
c.push(P("Tudo está disponível para conferência e reprodução:"));
c.push(item([t("Repositório completo: "), link(REPO, REPO)]));
c.push(item([t("Plano pré-registrado: "), link("PREREGISTRO.md", ARQ("PREREGISTRO.md"))]));
c.push(item([t("Registro de desvios: "), link("DESVIOS.md", ARQ("DESVIOS.md"))]));
c.push(item([t("Manifesto com o SHA-256 de cada arquivo: "), link("data/raw/MANIFEST.csv", ARQ("data/raw/MANIFEST.csv"))]));
c.push(item([t("Relatório técnico consolidado: "), link("output/report.md", ARQ("output/report.md"))]));
c.push(item([t("Instruções de reprodução, passo a passo: "), link("README.md", ARQ("README.md"))]));
c.push(P(`Para conferir um arquivo baixado, calcule o SHA-256 (por exemplo, "certutil -hashfile arquivo SHA256" no Windows ou "sha256sum arquivo" no Linux) e compare com o manifesto. Críticas, erros encontrados e reproduções independentes podem ser enviados pelas issues do repositório.`));

// revisão
c.push(H1("11. A primeira revisão crítica e o que mudou"));
c.push(P([t("Depois da publicação da versão 1.0, uma revisão independente avaliou a estrutura metodológica como acima da média para uma auditoria independente, mas apontou fragilidades. Todas foram analisadas; o registro completo, ponto a ponto, está em "), link("docs/revisao_etapa8.md", ARQ("docs/revisao_etapa8.md")), t(". Em resumo:")]));
c.push(tabela(["Ponto levantado", "Resposta na versão 1.1"], [
  ["O horário de um commit não prova a anterioridade do pré-registro", "Aceito. Limitação declarada (seção 2.1); planos novos passam a ter carimbo temporal externo antes de executados"],
  ["A amostra não elimina irregularidades; faltava detalhar exclusões e o cálculo do intervalo; boletim igual à totalização não prova a intenção do eleitor", "Aceito. Memória de cálculo, seções excluídas e limite de escopo na seção 3"],
  ["O modelo geográfico precisava de mais transparência e de testes de robustez; o uso do Censo 2022 nos anos anteriores", "Aceito. Distribuição das seções atípicas, quatro especificações alternativas e modelo municipal sem o Censo (seções 4.1 a 4.3); uma delas deixou resultado sem explicação demonstrada, reportado"],
  ["A comparação internacional é limitada; os 49% não são uma probabilidade precisa", "Aceito. Texto revisto (seção 7.1)"],
  ["O erro das pesquisas merece estudo próprio; as pesquisas não são independentes", "Aceito. Ressalva incluída (seção 6); mecanismos ficam para estudo à parte"],
  ["O veredito podia ser lido como explicação causal definitiva e como prova de ausência de fraude", "Aceito. Veredito reescrito e alcance das conclusões explicitado (seção 8)"],
], [4600, 5038]));
c.push(espaco());
c.push(P("A recomendação final do revisor foi não apresentar o trabalho como auditoria conclusiva, mas mantê-lo aberto e reproduzível, capaz de sobreviver a revisões hostis, inclusive de quem discorde das conclusões. Esta versão segue essa recomendação."));

// glossário
c.push(H1("Glossário"));
const gl = [
  ["Boletim de urna (BU)", "Arquivo e extrato impresso que cada urna gera ao fim da votação, com o total de votos por candidato na seção."],
  ["Assinatura digital", "Código criptográfico que prova que um arquivo foi gerado por quem diz tê-lo gerado e não foi alterado desde então."],
  ["SHA-256", "Impressão digital de um arquivo: um código de 64 caracteres que muda completamente se qualquer byte do arquivo mudar."],
  ["Commit", "Registro datado de uma alteração no repositório Git. Cada commit depende do anterior, o que torna o histórico difícil de adulterar sem deixar rastro."],
  ["Pré-registro", "Publicação do plano de análise antes de ver os dados, para impedir que os resultados guiem a escolha dos testes."],
  ["Intervalo de confiança de 95%", "Faixa de valores compatível com os dados da amostra; 95% dos intervalos calculados assim contêm o valor real."],
  ["Correção para múltiplos testes", "Ajuste que evita \"achados\" por puro acaso quando se fazem centenas de comparações ao mesmo tempo (aqui, o método de Benjamini-Hochberg)."],
  ["I de Moran", "Medida de quanto valores parecidos se agrupam no mapa; vai de valores negativos a 1."],
  ["Margem", "Diferença entre os percentuais dos dois candidatos."],
  ["Falácia ecológica", "Erro de deduzir o comportamento de indivíduos a partir de totais agregados."],
  ["Atirador texano", "Erro de calcular a improbabilidade de um resultado depois de conhecê-lo, desenhando o alvo em volta dos tiros."],
];
c.push(tabela(["Termo", "Significado"], gl.map(([a, x]) => [[b(a, { size: 18 })], x]), [2600, 7038]));
c.push(espaco());
c.push(P([t("Fontes de dados: Tribunal Superior Eleitoral (Portal de Dados Abertos, resultados.tse.jus.br e documentação técnica), Instituto Brasileiro de Geografia e Estatística (Censo 2022 e malhas territoriais) e Wikipedia (revisões fixadas, somente para pesquisas e eleições de outros países). Texto e tabelas sob licença CC BY 4.0; código sob licença MIT.", { size: 18, color: CINZA })]));

// --- documento ---------------------------------------------------------------------------------------
const doc = new Document({
  creator: "Leandro Marques Pitol",
  title: "O que os dados públicos dizem sobre o 2º turno presidencial de 2026",
  description: "Auditoria estatística pré-registrada — versão preliminar",
  styles: {
    default: { document: { run: { font: "Calibri", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: "Georgia", size: 32, bold: true, color: AZUL }, paragraph: { spacing: { before: 360, after: 160 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: "Georgia", size: 25, bold: true, color: "2E3A46" }, paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 } },
    ],
  },
  numbering: { config: [{ reference: "marcadores", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
    style: { paragraph: { indent: { left: 540, hanging: 300 } } } }] }] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, right: 1134, bottom: 1134, left: 1134 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [
      t("Versão 1.1 (preliminar) · github.com/leandropitol/auditoria-eleicao-2026 · página ", { size: 16, color: CINZA }),
      new TextRun({ children: [PageNumber.CURRENT], size: 16, color: CINZA })] })] }) },
    children: c,
  }],
});

const saida = path.join(RAIZ, "output", "relatorio", "relatorio_publico_eleicao_2026.docx");
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(saida, buf); console.log("ok", saida, buf.length); });
