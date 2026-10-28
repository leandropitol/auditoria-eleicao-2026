"""Testes do verificador do T1: arquivos íntegros passam; qualquer adulteração é detectada.

Usa um par bu.dat/vota.vsc real de data/raw (copiado para pasta temporária; o bruto não é tocado).
Rodar: .venv/Scripts/python -m pytest tests -q
"""

import importlib.util
import shutil
import sys
from pathlib import Path

import asn1tools
import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
_spec = importlib.util.spec_from_file_location("validate_bu", SRC / "02_validate_bu.py")
v = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v)

MR = v._carrega_util()
CONV_ASS = asn1tools.compile_files([str(v.SPEC / "spec" / "assinatura.asn1")], codec="ber", numeric_enums=True)
CONV_BU = asn1tools.compile_files([str(v.SPEC / "spec" / "bu.asn1")], codec="ber", numeric_enums=True)


def _par_real() -> Path:
    for bu in sorted((v.RAW / "D1" / "bu").rglob("*-bu.dat")):
        if list(bu.parent.glob("*-vota.vsc")):
            return bu.parent
    pytest.skip("nenhum BU baixado ainda")


@pytest.fixture
def copia(tmp_path):
    origem = _par_real()
    destino = v.RAW / "_teste_tmp"  # verifica_bu exige caminho sob data/raw
    if destino.exists():
        shutil.rmtree(destino)
    shutil.copytree(origem, destino)
    yield destino
    shutil.rmtree(destino)


def _adultera(path: Path, offset_rel: float):
    b = bytearray(path.read_bytes())
    i = int(len(b) * offset_rel)
    b[i] ^= 0x01
    path.write_bytes(bytes(b))


def _verifica(pasta):
    return v.verifica_bu(MR, CONV_ASS, CONV_BU, pasta)


def test_integro_passa(copia):
    r = _verifica(copia)
    assert r["assinatura_valida"]
    votos = __import__("json").loads(r["votos"])
    assert sum(votos.values()) == r["comparecimento_cargo"]


def test_bu_adulterado_falha(copia):
    _adultera(next(copia.glob("*-bu.dat")), 0.9)
    r = _verifica(copia)
    assert not r["c2_hash_bu"]
    assert not r["assinatura_valida"]


def _localiza(vsc: Path, alvo: bytes) -> int:
    b = vsc.read_bytes()
    i = b.find(alvo)
    assert i >= 0
    return i


def test_assinatura_do_bu_adulterada_falha(copia):
    vsc = next(copia.glob("*-vota.vsc"))
    ent = CONV_ASS.decode("EntidadeAssinaturaEcourna", vsc.read_bytes())
    lista = CONV_ASS.decode("Assinatura", ent["assinaturaHW"]["conteudoAutoAssinado"])["arquivosAssinados"]
    nome_bu = next(copia.glob("*-bu.dat")).name
    ass = next(a["assinatura"]["assinatura"] for a in lista if a["nomeArquivo"] == nome_bu)
    i = _localiza(vsc, bytes(ass)) + len(ass) // 2
    b = bytearray(vsc.read_bytes())
    b[i] ^= 0x01
    vsc.write_bytes(bytes(b))
    r = _verifica(copia)
    # o byte alterado está dentro de conteudoAutoAssinado: falham o critério 1 e o 4
    assert not r["c1_autoassinado"]
    assert not r["c4_assinatura_bu"]
    assert not r["assinatura_valida"]


def test_certificado_adulterado_falha(copia):
    vsc = next(copia.glob("*-vota.vsc"))
    ent = CONV_ASS.decode("EntidadeAssinaturaEcourna", vsc.read_bytes())
    _, cert = ent["assinaturaHW"]["informacaoChave"]
    # certificado PEM (UE2020/UE2022): troca um caractere base64 da assinatura do certificado por
    # outro caractere base64 válido, preservando o parse
    assert bytes(cert).startswith(b"-----BEGIN CERTIFICATE-----")
    i = _localiza(vsc, bytes(cert)) + len(cert) - 60
    b = bytearray(vsc.read_bytes())
    assert chr(b[i]).isalnum()
    b[i] = ord("A") if b[i] != ord("A") else ord("B")
    vsc.write_bytes(bytes(b))
    r = _verifica(copia)
    assert not r["c3_certificado"]
    assert not r["assinatura_valida"]
