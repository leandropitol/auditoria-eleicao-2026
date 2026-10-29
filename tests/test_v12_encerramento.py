"""Testes das regras do plano v1.2 (fuso, grupos de encerramento e contagem de votos no log)."""

import importlib.util
import sys
from pathlib import Path

import pandas as pd

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
spec = importlib.util.spec_from_file_location("v12", SRC / "15_encerramento_v12.py")
V12 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V12)


def test_deslocamento_pela_mediana_da_abertura():
    s = pd.DataFrame({"uf": ["AC", "AC", "AC", "SP"], "mun": ["1", "1", "1", "2"],
                      "abertura_local": pd.to_datetime(["2026-10-25 06:00:01", "2026-10-25 06:02:00",
                                                        "2026-10-25 08:30:00", "2026-10-25 08:00:05"])})
    assert V12.deslocamentos(s).tolist() == [-2, -2, -2, 0]


def test_grupos_nos_cortes():
    h = pd.to_datetime(pd.Series(["2026-10-25 17:15:59", "2026-10-25 17:16:00", "2026-10-25 18:59:59",
                                  "2026-10-25 19:00:00", None]))
    assert V12.grupo(h).tolist()[:4] == ["G0", "G1", "G1", "G2"]
    assert pd.isna(V12.grupo(h).iloc[4])


def test_conta_so_votos_do_dia_do_2o_turno():
    texto = "\n".join([
        "04/10/2026 16:59:00\tINFO\t1\tVOTA\tO voto do eleitor foi computado\tAA",
        "25/10/2026 16:59:59\tINFO\t1\tVOTA\tO voto do eleitor foi computado\tAB",
        "25/10/2026 17:00:00\tINFO\t1\tVOTA\tVoto confirmado para [Presidente]\tAC",
        "25/10/2026 17:00:01\tINFO\t1\tVOTA\tO voto do eleitor foi computado\tAD",
    ])
    assert V12.horas_de_voto(texto) == ["16:59:59", "17:00:01"]
