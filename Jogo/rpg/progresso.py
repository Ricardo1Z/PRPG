"""Progresso salvo do jogador: quantas vezes ele ZEROU o jogo (venceu as 15 fases).

Cada vez que o jogo é zerado, mais um personagem é desbloqueado. Os 4 primeiros
já vêm liberados. O progresso fica no arquivo save.json.
"""
import json
from pathlib import Path

ARQUIVO = Path(__file__).resolve().parent.parent / 'save.json'

TOTAL_PERSONAGENS = 8
BASICOS = 4  # personagens já liberados no começo

# Modo demonstração: todos os personagens já começam liberados.
MODO_DEMO = True


def _ler():
    try:
        dados = json.loads(ARQUIVO.read_text(encoding='utf-8'))
        return max(0, int(dados.get('zeradas', 0)))
    except (OSError, ValueError, TypeError, AttributeError):
        return 0  # sem arquivo (ou arquivo estragado): começa do zero


def _salvar():
    try:
        ARQUIVO.write_text(json.dumps({'zeradas': _zeradas}), encoding='utf-8')
    except OSError:
        print('[aviso] não foi possível salvar o progresso')


_zeradas = _ler()


def zeradas():
    return _zeradas


def quantos_liberados():
    """Quantos personagens estão liberados (os da frente da lista)."""
    if MODO_DEMO:
        return TOTAL_PERSONAGENS
    return min(TOTAL_PERSONAGENS, BASICOS + _zeradas)


def registrar_zerada():
    """Chame ao vencer a última fase. Retorna o índice do personagem recém
    desbloqueado, ou None se já estavam todos liberados."""
    global _zeradas
    antes = quantos_liberados()
    _zeradas += 1
    _salvar()
    depois = quantos_liberados()
    return antes if depois > antes else None
