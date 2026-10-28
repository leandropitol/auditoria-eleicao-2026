"""Controle positivo da reconciliação: divergências e ausências injetadas precisam ser detectadas."""

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from t1_reconcilia import clopper_pearson, reconcilia_bus  # noqa: E402

BU = pd.DataFrame([
    {"uf": "AC", "mun": "01015", "zona": "0002", "secao": "0072", "estrato": "AC_medio", "peso": 10.0,
     "hash_tse": "h1", "votos": json.dumps({"13": 51, "22": 127, "95": 1, "96": 6})},
    {"uf": "AC", "mun": "01015", "zona": "0002", "secao": "0073", "estrato": "AC_medio", "peso": 10.0,
     "hash_tse": "h2", "votos": json.dumps({"13": 10, "22": 20})},
])


def _tot(linhas):
    df = pd.DataFrame(linhas, columns=["uf", "mun", "zona", "secao", "NR_VOTAVEL", "QT_VOTOS"])
    return df.pivot_table(index=["uf", "mun", "zona", "secao"], columns="NR_VOTAVEL",
                          values="QT_VOTOS", aggfunc="sum", fill_value=0)


def test_iguais_nao_divergem():
    tot = _tot([("AC", "01015", "0002", "0072", "13", 51), ("AC", "01015", "0002", "0072", "22", 127),
                ("AC", "01015", "0002", "0072", "95", 1), ("AC", "01015", "0002", "0072", "96", 6),
                ("AC", "01015", "0002", "0073", "13", 10), ("AC", "01015", "0002", "0073", "22", 20)])
    rec = reconcilia_bus(BU, tot)
    assert not rec["divergente"].any()


def test_um_voto_de_diferenca_diverge():
    tot = _tot([("AC", "01015", "0002", "0072", "13", 52), ("AC", "01015", "0002", "0072", "22", 126),
                ("AC", "01015", "0002", "0072", "95", 1), ("AC", "01015", "0002", "0072", "96", 6),
                ("AC", "01015", "0002", "0073", "13", 10), ("AC", "01015", "0002", "0073", "22", 20)])
    rec = reconcilia_bus(BU, tot).set_index("secao")
    assert rec.loc["0072", "divergente"] and rec.loc["0072", "soma_abs_dif"] == 2
    assert not rec.loc["0073", "divergente"]


def test_secao_ausente_na_totalizacao_diverge():
    tot = _tot([("AC", "01015", "0002", "0072", "13", 51), ("AC", "01015", "0002", "0072", "22", 127),
                ("AC", "01015", "0002", "0072", "95", 1), ("AC", "01015", "0002", "0072", "96", 6)])
    rec = reconcilia_bus(BU, tot).set_index("secao")
    assert rec.loc["0073", "divergente"] and not rec.loc["0073", "presente_totalizacao"]


def test_clopper_pearson_zero():
    lo, hi = clopper_pearson(0, 5692)
    assert lo == 0 and abs(hi - (1 - 0.025 ** (1 / 5692))) < 1e-9
