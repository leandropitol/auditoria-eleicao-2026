"""T1 — verificação criptográfica e reconciliação dos BUs (docs/desenho_amostral_T1.md).

Uso:
    python src/02_validate_bu.py sorteia      # quadro amostral -> data/processed/t1_amostra.csv
    python src/02_validate_bu.py valida       # assinatura + extração dos votos -> t1_bu_validacao.parquet
    python src/02_validate_bu.py valida-recebidos  # complemento exploratório (DESVIOS.md)
    python src/02_validate_bu.py reconcilia   # BU x totalização (D2) e classificação -> output/tables/
"""

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from common import OUTPUT, PROCESSED, RAW, SEMENTE

PLEITO_2T = "3221"
ELEICAO_PRES_2T = 6258
N_PLANEJADO = 6000
N_MINIMO_ESTRATO = 5
SPEC = PROCESSED / "tse_spec"


def porte(n_secoes: int) -> str:
    if n_secoes <= 30:
        return "pequeno"
    if n_secoes <= 300:
        return "medio"
    return "grande"


def quadro_amostral() -> pd.DataFrame:
    linhas = []
    for arq in sorted((RAW / "D1" / "config").glob(f"*-p00{PLEITO_2T}-cs.json")):
        cfg = json.loads(arq.read_text(encoding="utf-8"))
        for abr in cfg["abr"]:
            for mu in abr["mu"]:
                for zo in mu["zon"]:
                    for se in zo["sec"]:
                        linhas.append((abr["cd"].upper(), mu["cd"], zo["cd"], se["ns"]))
    q = pd.DataFrame(linhas, columns=["uf", "mun", "zona", "secao"]).drop_duplicates()
    q["n_secoes_mun"] = q.groupby(["uf", "mun"])["secao"].transform("size")
    q["porte"] = q["n_secoes_mun"].map(porte)
    q["estrato"] = q["uf"] + "_" + q["porte"]
    return q.sort_values(["uf", "mun", "zona", "secao"]).reset_index(drop=True)


def sorteia() -> None:
    q = quadro_amostral()
    N = len(q)
    rng = np.random.default_rng(SEMENTE)
    partes = []
    for estrato, g in q.groupby("estrato", sort=True):
        N_h = len(g)
        n_h = max(min(N_h, N_MINIMO_ESTRATO), round(N_PLANEJADO * N_h / N))
        idx = rng.choice(N_h, size=n_h, replace=False)
        s = g.iloc[np.sort(idx)].copy()
        s["N_h"], s["n_h"] = N_h, n_h
        s["peso"] = N_h / n_h
        partes.append(s)
    amostra = pd.concat(partes, ignore_index=True)
    amostra.to_csv(PROCESSED / "t1_amostra.csv", index=False)
    resumo = q.groupby(["uf", "porte"]).size().rename("N_h").to_frame().join(
        amostra.groupby(["uf", "porte"]).size().rename("n_h"))
    resumo.to_csv(PROCESSED / "t1_estratos.csv")
    print(f"universo N={N} seções; estratos={q['estrato'].nunique()}; amostra n={len(amostra)}")
    print(q["porte"].value_counts().to_string())


def secoes_agregadas() -> dict:
    """Seções agregadas (campo `nsp` na configuração): votam na urna da seção principal e não têm BU próprio."""
    agregadas = {}
    for arq in sorted((RAW / "D1" / "config").glob(f"*-p00{PLEITO_2T}-cs.json")):
        cfg = json.loads(arq.read_text(encoding="utf-8"))
        for abr in cfg["abr"]:
            for mu in abr["mu"]:
                for zo in mu["zon"]:
                    for se in zo["sec"]:
                        if "nsp" in se:
                            agregadas[(abr["cd"].upper(), mu["cd"], zo["cd"], se["ns"])] = se["nsp"]
    return agregadas


# --- verificação -------------------------------------------------------------------------------

SPEC_ZIP = RAW / "tse_doc" / "formato-arquivos-de-bu-rdv-e-assinatura-digital.zip"


def extrai_spec() -> None:
    """Extrai o pacote oficial do TSE (data/raw é imutável; a cópia extraída fica em data/processed)."""
    if not (SPEC / "spec" / "bu.asn1").exists():
        with zipfile.ZipFile(SPEC_ZIP) as z:
            z.extractall(SPEC)


def _carrega_util():
    extrai_spec()
    sys.path.insert(0, str(SPEC / "python"))
    from lib import mr_util  # pacote oficial do TSE (formato-arquivos-de-bu-rdv-e-assinatura-digital.zip)
    return mr_util


def _sha512(b: bytes) -> bytes:
    return hashlib.sha512(b).digest()


def verifica_bu(mr, conv_ass, conv_bu, pasta: Path) -> dict:
    """Aplica os critérios 1–4 da Seção 4 a um par bu.dat/vota.vsc e extrai os votos de Presidente."""
    bu_path = next(pasta.glob("*-bu.dat"))
    vsc_path = next(pasta.glob("*-vota.vsc"))
    bu_bytes = bu_path.read_bytes()
    r = {"arquivo_bu": bu_path.relative_to(RAW).as_posix()}

    ent = conv_ass.decode("EntidadeAssinaturaEcourna", vsc_path.read_bytes())
    r["modelo_urna"] = ent["origemAssinaturaHW"]["modeloEquipamento"]
    ok_auto, ok_hash_bu = True, True
    for campo in ("assinaturaSW", "assinaturaHW"):
        env = ent[campo]
        ok_auto &= _sha512(env["conteudoAutoAssinado"]) == env["autoAssinado"]["assinatura"]["hash"]
        lista = conv_ass.decode("Assinatura", env["conteudoAutoAssinado"])["arquivosAssinados"]
        hashes = [a["assinatura"]["hash"] for a in lista if a["nomeArquivo"] == bu_path.name]
        ok_hash_bu &= len(hashes) == 1 and hashes[0] == _sha512(bu_bytes)
    r["c1_autoassinado"] = bool(ok_auto)
    r["c2_hash_bu"] = bool(ok_hash_bu)

    x509, _, chave, verificador = mr.extrai_chave_certificado_hw(str(SPEC / "spec" / "assinatura.asn1"), str(vsc_path))
    r["emissor_certificado"] = mr.common_name(x509["tbsCertificate"]["issuer"][1])
    try:
        r["c3_certificado"] = bool(mr.valida_certificado(x509, verificador))
    except ValueError:  # emissor fora das AC raiz publicadas
        r["c3_certificado"] = False

    lista_hw = conv_ass.decode("Assinatura", ent["assinaturaHW"]["conteudoAutoAssinado"])["arquivosAssinados"]
    ass = [a["assinatura"] for a in lista_hw if a["nomeArquivo"] == bu_path.name]
    r["c4_assinatura_bu"] = bool(len(ass) == 1 and verificador.verify(
        _sha512(ass[0]["hash"]), ass[0]["assinatura"], chave))
    r["assinatura_valida"] = r["c1_autoassinado"] and r["c2_hash_bu"] and r["c3_certificado"] and r["c4_assinatura_bu"]

    envelope = conv_bu.decode("EntidadeEnvelopeGenerico", bu_bytes)
    bu = conv_bu.decode("EntidadeBoletimUrna", envelope["conteudo"])
    votos, n_pres = {}, 0
    for res_eleicao in bu["resultadosVotacaoPorEleicao"]:
        if res_eleicao["idEleicao"] != ELEICAO_PRES_2T:
            continue
        for res in res_eleicao["resultadosVotacao"]:
            for cargo in res["totaisVotosCargo"]:
                if cargo["codigoCargo"] != ("cargoConstitucional", 1):
                    continue
                n_pres += 1
                r["comparecimento_cargo"] = res["qtdComparecimento"]
                for v in cargo["votosVotaveis"]:
                    tipo = v["tipoVoto"]
                    if tipo == 1:
                        chave_voto = str(v["identificacaoVotavel"]["codigo"])
                    elif tipo == 2:
                        chave_voto = "95"
                    elif tipo == 3:
                        chave_voto = "96"
                    else:
                        chave_voto = f"tipo{tipo}"
                    votos[chave_voto] = votos.get(chave_voto, 0) + v["quantidadeVotos"]
    r["n_blocos_presidente"] = n_pres
    r["votos"] = json.dumps(votos, sort_keys=True)
    ident = bu["identificacaoSecao"]
    r["bu_mun"] = ident["municipioZona"]["municipio"]
    r["bu_zona"] = ident["municipioZona"]["zona"]
    r["bu_secao"] = ident["secao"]
    return r


def valida(estado: str = "Totalizado", saida: str = "t1_bu_validacao.parquet") -> None:
    """`estado`=Totalizado: T1 confirmatório; `estado`=Recebido: complemento exploratório (DESVIOS.md)."""
    import asn1tools

    mr = _carrega_util()
    conv_ass = asn1tools.compile_files([str(SPEC / "spec" / "assinatura.asn1")], codec="ber", numeric_enums=True)
    conv_bu = asn1tools.compile_files([str(SPEC / "spec" / "bu.asn1")], codec="ber", numeric_enums=True)
    amostra = pd.read_csv(PROCESSED / "t1_amostra.csv", dtype=str)
    agregadas = secoes_agregadas()
    linhas = []
    for s in amostra.itertuples():
        uf = s.uf.lower()
        pasta = RAW / "D1" / "bu" / uf / f"{s.mun}-{s.zona}-{s.secao}"
        base = {"uf": s.uf, "mun": s.mun, "zona": s.zona, "secao": s.secao,
                "estrato": s.estrato, "peso": float(s.peso)}
        aux_path = pasta / f"p00{PLEITO_2T}-{uf}-m{s.mun}-z{s.zona}-s{s.secao}-aux.json"
        principal = agregadas.get((s.uf, s.mun, s.zona, s.secao))
        if principal:
            linhas.append({**base, "situacao": f"secao_agregada[principal={principal}]"})
            continue
        if not aux_path.exists():
            linhas.append({**base, "situacao": "aux_nao_baixado"})
            continue
        aux = json.loads(aux_path.read_text(encoding="utf-8"))
        totalizados = [h for h in aux.get("hashes", []) if h.get("st") == estado]
        if not totalizados:
            if estado != "Totalizado":
                continue
            estados = ";".join(sorted({h.get("st", "") for h in aux.get("hashes", [])})) or "sem_hashes"
            linhas.append({**base, "situacao": f"sem_bu_totalizado[{aux.get('st', '')}|{estados}]"})
            continue
        for h in totalizados:
            sub = pasta / h["hash"][:16]
            try:
                r = verifica_bu(mr, conv_ass, conv_bu, sub)
                linhas.append({**base, "situacao": "bu_verificado", "hash_tse": h["hash"], **r})
            except Exception as e:  # noqa: BLE001 - erro de leitura vira falha registrada, nunca é descartado
                linhas.append({**base, "situacao": "erro_leitura", "hash_tse": h["hash"],
                               "erro": f"{type(e).__name__}: {e}", "assinatura_valida": False})
    df = pd.DataFrame(linhas)
    df.to_parquet(PROCESSED / saida, index=False)
    print(df["situacao"].value_counts().to_string())
    if "assinatura_valida" in df:
        print("assinatura_valida:", df["assinatura_valida"].value_counts(dropna=False).to_dict())


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("modo", choices=["sorteia", "valida", "valida-recebidos", "reconcilia"])
    args = p.parse_args()
    if args.modo == "reconcilia":
        from importlib import import_module
        sys.path.insert(0, str(Path(__file__).parent))
        import_module("t1_reconcilia").main()
    else:
        {"sorteia": sorteia, "valida": valida,
         "valida-recebidos": lambda: valida("Recebido", "t1_bu_validacao_recebidos.parquet")}[args.modo]()
