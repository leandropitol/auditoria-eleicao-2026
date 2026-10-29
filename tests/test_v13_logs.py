"""Testes da checagem v1.3.1 dos logs (erros de assinatura em qualquer formato e desfecho da inicialização)."""

import importlib.util
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
spec = importlib.util.spec_from_file_location("v13", SRC / "16_logs_assinaturas_v13.py")
V13 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V13)


def _p(nivel, app, msg, hora="04/10/2026 12:00:00"):
    return [hora, nivel, "1", app, msg]


def test_erro_de_assinatura_em_todos_os_formatos():
    assert V13.erro_de_assinatura(_p("INFO", "GAP", "Verificação de assinatura - Etapa [26] - [/x/infomidia.vsc] - [ERRO]"))
    assert V13.erro_de_assinatura(_p("ERRO", "GAP", "GAP erro 73 | Validação do VOTA | Erro verificando assinatura"))
    assert V13.erro_de_assinatura(_p("ERRO", "GAP", "Erro na verificação de assinatura do arquivo - uenux.vsu"))
    assert not V13.erro_de_assinatura(_p("INFO", "GAP", "Verificação de assinatura - Etapa [1] - [/b/a.vst] - [SUCESSO]"))
    assert not V13.erro_de_assinatura(_p("ERRO", "GAP", "Problema ao desmontar a MR"))


def test_desfecho_por_inicializacao():
    linhas = [_p("INFO", "LOGD", "Início das operações do logd"),
              _p("ERRO", "GAP", "Erro na verificação de assinatura do arquivo - uenux.vsu"),
              _p("INFO", "VOTA", "Iniciando aplicação - 1º turno"),
              _p("INFO", "LOGD", "Início das operações do logd"),
              _p("ERRO", "GAP", "GAP erro 73 | Erro verificando assinatura"),
              _p("INFO", "INITJE", "Urna desligada pela chave")]
    blocos = V13.inicializacoes(linhas)
    assert len(blocos) == 2
    assert V13.desfecho(blocos[0], 1) == "aplicativo de votação iniciado"
    assert V13.desfecho(blocos[1], 1) == "aplicativo de votação não iniciado"
