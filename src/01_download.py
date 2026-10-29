"""Etapa 2 — coleta D1–D8 com registro de SHA-256, data/hora UTC e URL em data/raw/MANIFEST.csv.

Uso:
    python src/01_download.py lote        # D2–D8 (arquivos agregados do TSE e do IBGE)
    python src/01_download.py bu-quadro   # D1: quadro amostral (configuração de seções do 2º turno)
    python src/01_download.py bu-amostra  # D1: BUs assinados das seções sorteadas

A amostra de D1 segue docs/desenho_amostral_T1.md (fixado antes da coleta dos BUs).
"""

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from common import RAW, USER_AGENT, arquivos_no_manifesto, baixa_e_registra

TSE = "TSE"
IBGE = "IBGE"
LIC_TSE = "CC-BY (Portal de Dados Abertos do TSE)"
LIC_IBGE = "Dados abertos IBGE (Lei 12.527/2011)"
ODS = "https://cdn.tse.jus.br/estatistica/sead/odsele"
IBGE_AGR = "https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios"
IBGE_REND = "https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios_Rendimento_do_Responsavel"
GEOFTP = "https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais"
UFS = ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA",
       "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO"]
ANOS_MUNZONA = [1994, 1998, 2002, 2006, 2010, 2014, 2018, 2022]
ANOS_CONTROLE = [2014, 2018, 2022]
ANOS_PESQUISA = [2014, 2018, 2022, 2026]

RESULTADOS_2026 = "https://resultados.tse.jus.br/oficial/ele2026"
PLEITO_2T = "3221"


def lote() -> list[tuple]:
    """(id_fonte, url, subpasta, orgao, descricao, licenca, observacoes)"""
    itens = [
        ("D2", f"{ODS}/votacao_secao/votacao_secao_2026_BR.zip", "D2", TSE,
         "Votação por seção eleitoral 2026 - Presidente (totalização oficial)", LIC_TSE, ""),
        ("D2", f"{ODS}/votacao_candidato_munzona/votacao_candidato_munzona_2026.zip", "D2", TSE,
         "Votação nominal por município e zona 2026", LIC_TSE, ""),
        ("D4", f"{ODS}/detalhe_votacao_secao/detalhe_votacao_secao_2026.zip", "D4", TSE,
         "Detalhe da apuração por seção 2026 (aptos, comparecimento, abstenção, brancos, nulos)", LIC_TSE, ""),
        ("D4", f"{ODS}/perfil_comparecimento_abstencao/perfil_comparecimento_abstencao_2026.zip", "D4", TSE,
         "Perfil de comparecimento e abstenção 2026", LIC_TSE, ""),
        ("D3", f"{ODS}/perfil_eleitorado/perfil_eleitorado_2026.zip", "D3", TSE,
         "Perfil do eleitorado 2026 (município/zona)", LIC_TSE, ""),
        ("D3", f"{ODS}/eleitorado_locais_votacao/eleitorado_local_votacao_2026.zip", "D3", TSE,
         "Eleitorado por local de votação 2026 (inclui coordenadas dos locais)", LIC_TSE, ""),
    ]
    itens += [("D3", f"{ODS}/perfil_eleitor_secao/perfil_eleitor_secao_2026_{uf}.zip", "D3", TSE,
               f"Perfil do eleitorado por seção 2026 - {uf}", LIC_TSE, "") for uf in UFS]
    itens += [("D5", f"{ODS}/pesquisa_eleitoral/pesquisa_eleitoral_{a}.zip", "D5", TSE,
               f"Registro de pesquisas eleitorais {a}", LIC_TSE,
               "Registro (instituto, metodologia, amostra); não contém resultados das pesquisas")
              for a in ANOS_PESQUISA]
    for nivel in ("municipios", "setores"):
        for tema, arq in (("basico", f"Agregados_por_{nivel}_basico_BR_20260520.zip"),
                          ("alfabetizacao", f"Agregados_por_{nivel}_alfabetizacao_BR.zip"),
                          ("demografia", f"Agregados_por_{nivel}_demografia_BR.zip")):
            pasta = "Agregados_por_Municipio_csv" if nivel == "municipios" else "Agregados_por_Setor_csv"
            itens.append(("D6", f"{IBGE_AGR}/{pasta}/{arq}", "D6", IBGE,
                          f"Censo 2022 - agregados por {nivel} - {tema}", LIC_IBGE, ""))
        itens.append(("D6", f"{IBGE_REND}/Agregados_por_{nivel}_renda_responsavel_BR_20260508_csv.zip", "D6", IBGE,
                      f"Censo 2022 - agregados por {nivel} - rendimento do responsável", LIC_IBGE, ""))
    itens += [
        ("D6", f"{IBGE_AGR}/dicionario_de_dados_agregados_por_setores_censitarios_20260520.xlsx", "D6", IBGE,
         "Dicionário dos agregados por setores censitários - Censo 2022", LIC_IBGE, ""),
        ("D6", f"{IBGE_REND}/dicionario_de_dados_renda_responsavel_20260508.xlsx", "D6", IBGE,
         "Dicionário dos agregados de rendimento do responsável - Censo 2022", LIC_IBGE, ""),
        ("D7", f"{GEOFTP}/malhas_municipais/municipio_2022/Brasil/BR/BR_Municipios_2022.zip", "D7", IBGE,
         "Malha municipal 2022", LIC_IBGE, ""),
        ("D7", f"{GEOFTP}/malhas_de_setores_censitarios__divisoes_intramunicipais/censo_2022/setores/shp/BR/BR_setores_CD2022.zip",
         "D7", IBGE, "Malha de setores censitários - Censo 2022", LIC_IBGE, ""),
        ("D8", f"{ODS}/votacao_candidato_uf/votacao_candidato_uf_1989.zip", "D8", TSE,
         "Votação nominal por UF 1989", LIC_TSE, "1989 não tem recorte município/zona no portal"),
        ("D8", f"{ODS}/detalhe_votacao_uf/detalhe_votacao_uf_1989.zip", "D8", TSE,
         "Detalhe da apuração por UF 1989", LIC_TSE, ""),
    ]
    for a in ANOS_MUNZONA:
        itens.append(("D8", f"{ODS}/votacao_candidato_munzona/votacao_candidato_munzona_{a}.zip", "D8", TSE,
                      f"Votação nominal por município e zona {a}", LIC_TSE, ""))
        itens.append(("D8", f"{ODS}/detalhe_votacao_munzona/detalhe_votacao_munzona_{a}.zip", "D8", TSE,
                      f"Detalhe da apuração por município e zona {a}", LIC_TSE, ""))
    for a in ANOS_CONTROLE:
        itens.append(("D8", f"{ODS}/votacao_secao/votacao_secao_{a}_BR.zip", "D8", TSE,
                      f"Votação por seção {a} - Presidente (controle T3)", LIC_TSE, ""))
        itens.append(("D8", f"{ODS}/detalhe_votacao_secao/detalhe_votacao_secao_{a}.zip", "D8", TSE,
                      f"Detalhe da apuração por seção {a} (controle T3)", LIC_TSE, ""))
    return itens


def roda_lote(workers: int = 3) -> None:
    feitos = arquivos_no_manifesto()
    pendentes = []
    for id_fonte, url, sub, orgao, desc, lic, obs in lote():
        destino = RAW / sub / url.rsplit("/", 1)[1]
        if destino.relative_to(RAW).as_posix() in feitos:
            continue
        pendentes.append((id_fonte, url, destino, orgao, desc, lic, obs))
    print(f"{len(pendentes)} arquivos pendentes", flush=True)
    with ThreadPoolExecutor(workers) as ex:
        futs = {ex.submit(baixa_e_registra, i, u, d, o, de, l, ob): u
                for i, u, d, o, de, l, ob in pendentes}
        erros = 0
        for fut in as_completed(futs):
            try:
                row = fut.result()
                print(f"ok {row['arquivo']} {row['bytes']} {row['sha256'][:12]}", flush=True)
            except Exception as e:  # noqa: BLE001 - registra e segue; o resumo final acusa a falha
                erros += 1
                print(f"ERRO {futs[fut]}: {e}", flush=True)
    print(f"fim do lote; erros={erros}", flush=True)
    if erros:
        sys.exit(1)


def roda_quadro() -> None:
    """Baixa a configuração de seções (quadro amostral) do pleito do 2º turno, por UF e exterior."""
    sessao = requests.Session()
    feitos = arquivos_no_manifesto()
    for uf in [u.lower() for u in UFS] + ["zz"]:
        url = f"{RESULTADOS_2026}/arquivo-urna/{PLEITO_2T}/config/{uf}/{uf}-p00{PLEITO_2T}-cs.json"
        destino = RAW / "D1" / "config" / url.rsplit("/", 1)[1]
        if destino.relative_to(RAW).as_posix() in feitos:
            continue
        row = baixa_e_registra("D1", url, destino, TSE,
                               f"Configuração de seções do pleito {PLEITO_2T} (2º turno 2026) - {uf.upper()}",
                               LIC_TSE, "Quadro amostral de T1", sessao)
        print(f"ok {row['arquivo']} {row['bytes']}", flush=True)


def _baixa_secao(sessao, uf, mun, zona, secao):
    """Baixa o aux.json da seção e, para o hash com estado Totalizado, o bu.dat e o vota.vsc."""
    base = f"{RESULTADOS_2026}/arquivo-urna/{PLEITO_2T}/dados/{uf}/{mun}/{zona}/{secao}"
    pasta = RAW / "D1" / "bu" / uf / f"{mun}-{zona}-{secao}"
    aux_nome = f"p00{PLEITO_2T}-{uf}-m{mun}-z{zona}-s{secao}-aux.json"
    linhas = [baixa_e_registra("D1", f"{base}/{aux_nome}", pasta / aux_nome, TSE,
                               "Índice de arquivos de urna da seção (2º turno 2026)", LIC_TSE, "", sessao)]
    aux = json.loads((pasta / aux_nome).read_text(encoding="utf-8"))
    for h in aux.get("hashes", []):
        if h.get("st") != "Totalizado":
            continue
        for arq in h["arq"]:
            if arq["tp"] in ("bu", "vota"):
                linhas.append(baixa_e_registra(
                    "D1", f"{base}/{h['hash']}/{arq['nm']}", pasta / h["hash"][:16] / arq["nm"], TSE,
                    f"Arquivo de urna ({arq['tp']}) - 2º turno 2026", LIC_TSE,
                    f"hash TSE {h['hash']}", sessao))
    return linhas


def roda_amostra(workers: int = 8) -> None:
    import pandas as pd

    from common import PROCESSED

    amostra = pd.read_csv(PROCESSED / "t1_amostra.csv", dtype=str)
    feitos = arquivos_no_manifesto()
    pendentes = []
    for r in amostra.itertuples():
        uf = r.uf.lower()
        aux = f"D1/bu/{uf}/{r.mun}-{r.zona}-{r.secao}/p00{PLEITO_2T}-{uf}-m{r.mun}-z{r.zona}-s{r.secao}-aux.json"
        if aux not in feitos:
            pendentes.append((uf, r.mun, r.zona, r.secao))
    print(f"{len(pendentes)} seções pendentes de {len(amostra)}", flush=True)
    sessao = requests.Session()
    sessao.mount("https://", requests.adapters.HTTPAdapter(pool_maxsize=workers))
    erros = 0
    with ThreadPoolExecutor(workers) as ex:
        futs = {ex.submit(_baixa_secao, sessao, *p): p for p in pendentes}
        for n, fut in enumerate(as_completed(futs), 1):
            try:
                fut.result()
            except Exception as e:  # noqa: BLE001
                erros += 1
                print(f"ERRO {futs[fut]}: {e}", flush=True)
            if n % 250 == 0:
                print(f"{n}/{len(pendentes)}", flush=True)
    print(f"fim da amostra; erros={erros}", flush=True)
    if erros:
        sys.exit(1)


def roda_recebidos() -> None:
    """Complemento exploratório (DESVIOS.md): BUs de seções sem entrada "Totalizado" mas com entrada "Recebido"."""
    sessao = requests.Session()
    feitos = arquivos_no_manifesto()
    for aux_path in sorted((RAW / "D1" / "bu").rglob("*-aux.json")):
        aux = json.loads(aux_path.read_text(encoding="utf-8"))
        estados = {h.get("st") for h in aux.get("hashes", [])}
        if "Totalizado" in estados or "Recebido" not in estados:
            continue
        pasta = aux_path.parent
        uf = pasta.parent.name
        mun, zona, secao = pasta.name.split("-")
        base = f"{RESULTADOS_2026}/arquivo-urna/{PLEITO_2T}/dados/{uf}/{mun}/{zona}/{secao}"
        for h in aux["hashes"]:
            if h.get("st") != "Recebido":
                continue
            for arq in h["arq"]:
                destino = pasta / h["hash"][:16] / arq["nm"]
                if arq["tp"] in ("bu", "vota") and destino.relative_to(RAW).as_posix() not in feitos:
                    baixa_e_registra("D1", f"{base}/{h['hash']}/{arq['nm']}", destino, TSE,
                                     f"Arquivo de urna ({arq['tp']}) - 2º turno 2026 - estado Recebido",
                                     LIC_TSE, f"complemento exploratório; hash TSE {h['hash']}", sessao)
        print(f"ok {pasta.relative_to(RAW).as_posix()}", flush=True)

CKAN_TSE = "https://dadosabertos.tse.jus.br/api/3/action/package_show"


def roda_bweb() -> None:
    """D11 (plano v1.2, exploratório): BU na Web do 2º turno, último arquivo de cada UF no catálogo do TSE."""
    import re

    sessao = requests.Session()
    feitos = arquivos_no_manifesto()
    r = sessao.get(CKAN_TSE, params={"id": "resultados-2026-boletim-de-urna"},
                   headers={"User-Agent": USER_AGENT}, timeout=60)
    r.raise_for_status()
    ultimos = {}
    for rec in r.json()["result"]["resources"]:
        # o catálogo lista RR só pelo .sha512; o .zip existe com o mesmo nome
        m = re.search(r"/bweb_2t_([A-Z]{2})_(\d+)\.zip(\.sha512)?$", rec["url"])
        if m and m.group(1) in UFS:
            uf, carimbo, _ = m.groups()
            data = carimbo[4:8] + carimbo[2:4] + carimbo[:2] + carimbo[8:]  # ddmmaaaahhmm -> aaaammddhhmm
            if uf not in ultimos or data > ultimos[uf][0]:
                ultimos[uf] = (data, rec["url"].removesuffix(".sha512"))
    for uf in UFS:
        url = ultimos[uf][1]
        destino = RAW / "D11" / url.rsplit("/", 1)[1]
        if destino.relative_to(RAW).as_posix() in feitos:
            continue
        row = baixa_e_registra("D11", url, destino, TSE, f"BU na Web - 2º turno 2026 - {uf}", LIC_TSE,
                               "Plano v1.2 (exploratório): horário de abertura e encerramento por seção", sessao)
        print(f"ok {row['arquivo']} {row['bytes']}", flush=True)


def _baixa_log(sessao, uf, mun, zona, secao):
    """D12 (plano v1.2): aux.json da seção e o log de urna da entrada "Totalizado"."""
    base = f"{RESULTADOS_2026}/arquivo-urna/{PLEITO_2T}/dados/{uf}/{mun}/{zona}/{secao}"
    pasta = RAW / "D12" / uf / f"{mun}-{zona}-{secao}"
    aux_nome = f"p00{PLEITO_2T}-{uf}-m{mun}-z{zona}-s{secao}-aux.json"
    baixa_e_registra("D12", f"{base}/{aux_nome}", pasta / aux_nome, TSE,
                     "Índice de arquivos de urna da seção (2º turno 2026)", LIC_TSE, "Plano v1.2", sessao)
    aux = json.loads((pasta / aux_nome).read_text(encoding="utf-8"))
    for h in aux.get("hashes", []):
        if h.get("st") != "Totalizado":
            continue
        for arq in h["arq"]:
            if arq["tp"] == "log":
                baixa_e_registra("D12", f"{base}/{h['hash']}/{arq['nm']}", pasta / h["hash"][:16] / arq["nm"], TSE,
                                 "Log de urna - 2º turno 2026", LIC_TSE, f"Plano v1.2; hash TSE {h['hash']}", sessao)


def roda_logs(workers: int = 8) -> None:
    """D12: logs das seções listadas em data/processed/v12_selecao_logs.csv (gerado por src/15_encerramento_v12.py)."""
    import pandas as pd

    from common import PROCESSED

    sel = pd.read_csv(PROCESSED / "v12_selecao_logs.csv", dtype=str)
    feitos = arquivos_no_manifesto()
    pendentes = []
    for r in sel.itertuples():
        uf = r.uf.lower()
        aux = f"D12/{uf}/{r.mun}-{r.zona}-{r.secao}/p00{PLEITO_2T}-{uf}-m{r.mun}-z{r.zona}-s{r.secao}-aux.json"
        if aux not in feitos:
            pendentes.append((uf, r.mun, r.zona, r.secao))
    print(f"{len(pendentes)} seções pendentes de {len(sel)}", flush=True)
    sessao = requests.Session()
    sessao.mount("https://", requests.adapters.HTTPAdapter(pool_maxsize=workers))
    erros = 0
    with ThreadPoolExecutor(workers) as ex:
        futs = {ex.submit(_baixa_log, sessao, *p): p for p in pendentes}
        for n, fut in enumerate(as_completed(futs), 1):
            try:
                fut.result()
            except Exception as e:  # noqa: BLE001
                erros += 1
                print(f"ERRO {futs[fut]}: {e}", flush=True)
            if n % 500 == 0:
                print(f"{n}/{len(pendentes)}", flush=True)
    print(f"fim dos logs; erros={erros}", flush=True)
    if erros:
        sys.exit(1)


WIKI_API = "https://en.wikipedia.org/w/api.php"
WIKI_LIC = "CC BY-SA 4.0 (Wikipedia)"
PESQUISAS_WIKI = {a: f"Opinion polling for the {a} Brazilian presidential election"
                  for a in (2010, 2014, 2018, 2022, 2026)}
# não há página dedicada às pesquisas de 2014 (en nem pt); a página da eleição traz a seção de pesquisas
PESQUISAS_WIKI[2014] = "2014 Brazilian general election"
ELEICOES_EXTERIOR = {
    "France": [1965, 1969, 1974, 1981, 1988, 1995, 2002, 2007, 2012, 2017, 2022],
    "Chile": [1989, 1993, 1999, 2005, 2009, 2013, 2017, 2021, 2025],
    "Colombia": [1994, 1998, 2002, 2006, 2010, 2014, 2018, 2022, 2026],
    "Argentina": [1995, 1999, 2003, 2007, 2011, 2015, 2019, 2023],
    "Peru": [1990, 1995, 2000, 2001, 2006, 2011, 2016, 2021, 2026],
}
GENTILICO = {"France": "French", "Chile": "Chilean", "Colombia": "Colombian",
             "Argentina": "Argentine", "Peru": "Peruvian"}


def _revisao_atual(sessao, titulo: str) -> tuple[str, int, str]:
    """Resolve redirecionamentos e devolve (título final, ID da revisão vigente, timestamp)."""
    for tentativa in range(6):
        r = sessao.get(WIKI_API, params={"action": "query", "prop": "revisions", "titles": titulo,
                                         "redirects": 1, "rvprop": "ids|timestamp", "format": "json"},
                       headers={"User-Agent": USER_AGENT}, timeout=60)
        if r.status_code != 429:
            break
        time.sleep(int(r.headers.get("Retry-After", 0)) or 10 * 2 ** tentativa)
    r.raise_for_status()
    pagina = next(iter(r.json()["query"]["pages"].values()))
    if "revisions" not in pagina:
        raise LookupError(f"página inexistente: {titulo}")
    rev = pagina["revisions"][0]
    return pagina["title"], rev["revid"], rev["timestamp"]


def roda_wiki() -> None:
    """D9 (pesquisas, T5) e D10 (2ºs turnos no exterior, T6): HTML de revisões fixadas da Wikipedia."""
    sessao = requests.Session()
    feitos = arquivos_no_manifesto()
    alvos = [("D9", [t], f"pesquisas_{a}") for a, t in PESQUISAS_WIKI.items()]
    for p, anos in ELEICOES_EXTERIOR.items():
        for a in anos:
            g = GENTILICO[p]
            titulos = [f"{a} {g} presidential election", f"{a} {g} general election",
                       f"{a}–{str(a + 1)[2:]} {g} presidential election",
                       f"{a}–{a + 1} {g} presidential election"]
            alvos.append(("D10", titulos, f"{p.lower()}_{a}"))
    for id_fonte, titulos, slug in alvos:
        if any(f.startswith(f"{id_fonte}/{slug}_rev") for f in feitos):
            continue
        for titulo in titulos:
            try:
                final, revid, ts = _revisao_atual(sessao, titulo)
                break
            except LookupError:
                time.sleep(2)
        else:
            print(f"AUSENTE {slug}: {titulos}", flush=True)
            continue
        url = f"https://en.wikipedia.org/w/index.php?oldid={revid}&action=render"
        destino = RAW / id_fonte / f"{slug}_rev{revid}.html"
        baixa_e_registra(id_fonte, url, destino, "Wikipedia", f"{final} (revisão {revid}, {ts})", WIKI_LIC,
                         "Fonte secundária; revisão fixada (docs/desenho_T5_T6.md)", sessao)
        print(f"ok {destino.name} <- {final}", flush=True)
        time.sleep(5)


def roda_rebaixa(arquivos: list[str]) -> None:
    """Baixa de novo arquivos já registrados no manifesto e compara o SHA-256 com o registrado.

    Não acrescenta linhas ao manifesto; o resultado vai para output/tables/rebaixamento.csv.
    """
    import csv

    from common import MANIFEST, OUTPUT, agora_utc, baixa, sha256_file

    with open(MANIFEST, newline="", encoding="utf-8") as f:
        registro = {r["arquivo"]: r for r in csv.DictReader(f)}
    saida = OUTPUT / "tables" / "rebaixamento.csv"
    novo = not saida.exists()
    with open(saida, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if novo:
            w.writerow(["arquivo", "url", "data_hora_utc", "sha256_manifesto", "sha256_rebaixado", "confere"])
        for arq in arquivos:
            r = registro[arq]
            destino = RAW / arq
            data = agora_utc()
            if not destino.exists():
                baixa(r["url"], destino)
            h = sha256_file(destino)
            w.writerow([arq, r["url"], data, r["sha256"], h, h == r["sha256"]])
            print(f"{arq}: {'CONFERE' if h == r['sha256'] else 'DIFERENTE'} ({h[:12]} vs {r['sha256'][:12]})",
                  flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("modo", choices=["lote", "bu-quadro", "bu-amostra", "bu-recebidos", "wiki", "rebaixa",
                                    "bweb", "logs"])
    p.add_argument("arquivos", nargs="*", help="modo rebaixa: caminhos relativos a data/raw, como no manifesto")
    args = p.parse_args()
    if args.modo == "rebaixa":
        roda_rebaixa(args.arquivos)
        sys.exit(0)
    {"lote": roda_lote, "bu-quadro": roda_quadro, "bu-amostra": roda_amostra,
     "bu-recebidos": roda_recebidos, "wiki": roda_wiki, "bweb": roda_bweb, "logs": roda_logs}[args.modo]()
