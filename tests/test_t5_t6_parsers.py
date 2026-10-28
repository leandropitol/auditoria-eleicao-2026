"""Testes dos extratores de T5 (datas e nomes de institutos) e de T6 (tabela de resultados em dois turnos)."""

import importlib.util
import sys
from datetime import date
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))


def _carrega(nome, arquivo):
    spec = importlib.util.spec_from_file_location(nome, SRC / arquivo)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


T5 = _carrega("t5", "07_polls.py")
T6 = _carrega("t6", "08_historical.py")


def test_data_fim_nao_confunde_ano_com_dia():
    assert T5._data_fim("8–10 October 2018", 2018) == date(2018, 10, 10)
    assert T5._data_fim("17–18 October 2018", 2018) == date(2018, 10, 18)
    assert T5._data_fim("14–19 Oct 2022", 2022) == date(2022, 10, 19)
    assert T5._data_fim("29 Jun – 2 Jul 2022", 2022) == date(2022, 7, 2)
    assert T5._data_fim("Oct 25–27, 2022", 2022) == date(2022, 10, 27)
    assert T5._data_fim("30 Oct", 2010) == date(2010, 10, 30)


def test_instituto_independe_da_ordem_cliente_instituto():
    assert T5.instituto("Genial/Quaest[227]", True) == "quaest"
    assert T5.instituto("Quaest/Genial[61]", True) == "quaest"
    assert T5.instituto("CNT/Sensus") == "sensus"
    assert T5.instituto("ModalMais/Futura[233]", True) == "futura"
    assert T5.instituto("Datafolha archived 2011-07-11 at the Wayback Machine") == "datafolha"
    assert T5.instituto("Ibope") != T5.instituto("Ipec")  # empresas distintas, não fundidas


def test_tabela_dois_turnos_e_reversao():
    html = """<table><tr><th rowspan="2">Candidate</th><th colspan="2">First round</th>
    <th colspan="2">Second round</th></tr><tr><th>Votes</th><th>%</th><th>Votes</th><th>%</th></tr>
    <tr><td>X</td><td>100</td><td>40.0</td><td>200</td><td>45.0</td></tr>
    <tr><td>Y</td><td>90</td><td>36.0</td><td>244</td><td>55.0</td></tr>
    <tr><td>Z</td><td>60</td><td>24.0</td><td></td><td></td></tr>
    <tr><td>Valid votes</td><td>250</td><td>100.0</td><td>444</td><td>100.0</td></tr></table>"""
    t = T6.tabela_resultados(html)
    t = t[~t["candidato"].str.contains(T6._ROTULOS_NAO_CANDIDATO)].set_index("candidato")
    c = T6.caso("Teste", 2000, t["pct1"], t["pct2"].dropna(), "teste")
    assert c["lider_1t"] == "X" and c["margem_1t_pp"] == 4.0
    assert c["reversao"] and c["finalistas_sao_top2"]


def test_sem_segundo_turno():
    html = "<table><tr><th>Candidate</th><th>Votes</th><th>%</th></tr><tr><td>X</td><td>1</td><td>60</td></tr></table>"
    assert T6.tabela_resultados(html) is None
