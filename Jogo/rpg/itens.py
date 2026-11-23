"""Poções: efeitos, sorteio de drops e inventário.

Não tem nada visual: as poções são só entradas de texto no inventário.
Para criar uma poção nova, basta acrescentar uma linha em POCOES.
"""
import random

from .registro import registrar

# chave -> nome, tipo ('hp' cura vida / 'mp' recupera mana), quanto recupera,
# chance de cair ao vencer uma luta (0 a 1) e quantidade que cai (mín, máx)
POCOES = {
    'hp_p': {'nome': 'POÇÃO DE HP P', 'tipo': 'hp', 'valor': 15,  'chance': 0.40, 'qtd': (1, 2)},
    'hp_m': {'nome': 'POÇÃO DE HP M', 'tipo': 'hp', 'valor': 20,  'chance': 0.25, 'qtd': (1, 1)},
    'hp_g': {'nome': 'POÇÃO DE HP G', 'tipo': 'hp', 'valor': 50, 'chance': 0.10, 'qtd': (1, 1)},
    'mp_p': {'nome': 'POÇÃO DE MP P', 'tipo': 'mp', 'valor': 5,  'chance': 0.35, 'qtd': (1, 2)},
    'mp_m': {'nome': 'POÇÃO DE MP M', 'tipo': 'mp', 'valor': 15,  'chance': 0.20, 'qtd': (1, 1)},
    'mp_g': {'nome': 'POÇÃO DE MP G', 'tipo': 'mp', 'valor': 25,  'chance': 0.08, 'qtd': (1, 1)},
}

QUANTIDADE_INICIAL = 0        
BONUS_CHANCE_POR_FASE = 0.05  


def inventario_inicial():
    return {chave: QUANTIDADE_INICIAL for chave in POCOES}


def nome_pocao(chave):
    return POCOES[chave]['nome']


def pode_usar(chave, alvo):
    """Devolve (pode, motivo). A poção só vale em quem está vivo e precisa dela."""
    pocao = POCOES[chave]

    if alvo.vida <= 0:
        return False, f'{alvo.nome} está derrotado!'

    if pocao['tipo'] == 'hp' and alvo.vida >= alvo.vida_maxima:
        return False, f'{alvo.nome} já está com a vida cheia!'

    if pocao['tipo'] == 'mp' and alvo.mana >= alvo.mana_maxima:
        return False, f'{alvo.nome} já está com a mana cheia!'

    return True, ''


def usar_pocao(chave, usuario, alvo, inventario):
    """Usa uma poção em `alvo`. Retorna True só se ela foi usada de fato
    (a Luta usa isso para saber se o turno deve passar)."""
    pocao = POCOES[chave]

    if inventario.get(chave, 0) <= 0:
        registrar(f'Você não tem mais {pocao["nome"]}!')
        return False

    pode, motivo = pode_usar(chave, alvo)
    if not pode:
        registrar(motivo)
        return False

    inventario[chave] -= 1

    if pocao['tipo'] == 'hp':
        recuperado = min(pocao['valor'], alvo.vida_maxima - alvo.vida)
        alvo.vida += recuperado
        registrar(f'{usuario.nome} usou {pocao["nome"]}: '
                  f'{alvo.nome} recuperou {recuperado} de vida!')
    else:
        recuperado = min(pocao['valor'], alvo.mana_maxima - alvo.mana)
        alvo.mana += recuperado
        registrar(f'{usuario.nome} usou {pocao["nome"]}: '
                  f'{alvo.nome} recuperou {recuperado} de mana!')

    return True


def sortear_drops(indice_fase, sorte=random):
    """Sorteia as poções ganhas ao vencer uma luta: {chave: quantidade}.
    Cada tipo tem a sua própria chance; fases mais avançadas dão mais sorte."""
    bonus = 1 + BONUS_CHANCE_POR_FASE * indice_fase
    drops = {}

    for chave, pocao in POCOES.items():
        if sorte.random() < min(0.95, pocao['chance'] * bonus):
            drops[chave] = sorte.randint(*pocao['qtd'])

    return drops


def ganhar(inventario, drops):
    for chave, qtd in drops.items():
        inventario[chave] = inventario.get(chave, 0) + qtd
