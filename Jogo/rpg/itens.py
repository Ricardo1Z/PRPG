"""Itens (poções e armas de uso único): efeitos, sorteio de drops e inventário.

Não tem nada visual: os itens são só entradas de texto no inventário.
Para criar um item novo, basta acrescentar uma linha em POCOES.
"""
import random

from .registro import registrar

# chave -> nome, tipo ('hp' cura vida / 'mp' recupera mana / 'revive'), quanto
# recupera, chance de cair ao vencer uma luta (0 a 1), quantidade que cai
# (mín, máx) e quantidade no começo do jogo ('inicial'; padrão QUANTIDADE_INICIAL)
#
# Itens de dano ('adaga' / 'bomba') são usados nos INIMIGOS:
#   'adaga' -> um inimigo escolhido: 'valor' de dano (a defesa conta)
#   'bomba' -> todos os inimigos vivos: 'valor' de dano em cada (ignora
#              metade da defesa)
POCOES = {
    'hp_p': {'nome': 'POÇÃO DE HP P', 'tipo': 'hp', 'valor': 30,  'chance': 0.40, 'qtd': (1, 2), 'inicial': 2},
    'hp_m': {'nome': 'POÇÃO DE HP M', 'tipo': 'hp', 'valor': 60,  'chance': 0.25, 'qtd': (1, 1), 'inicial': 0},
    'hp_g': {'nome': 'POÇÃO DE HP G', 'tipo': 'hp', 'valor': 100, 'chance': 0.10, 'qtd': (1, 1), 'inicial': 0},
    'mp_p': {'nome': 'POÇÃO DE MP P', 'tipo': 'mp', 'valor': 15,  'chance': 0.35, 'qtd': (1, 2), 'inicial': 2},
    'mp_m': {'nome': 'POÇÃO DE MP M', 'tipo': 'mp', 'valor': 30,  'chance': 0.20, 'qtd': (1, 1), 'inicial': 0},
    'mp_g': {'nome': 'POÇÃO DE MP G', 'tipo': 'mp', 'valor': 50,  'chance': 0.08, 'qtd': (1, 1), 'inicial': 0},

    'revive': {'nome': 'POÇÃO DE REVIVER', 'tipo': 'revive', 'valor': 0.5, 'chance': 0.05,
               'qtd': (1, 1), 'inicial': 0},

    'adaga': {'nome': 'ADAGA', 'tipo': 'adaga', 'valor': 40, 'chance': 0.25,
              'qtd': (1, 2), 'inicial': 1},
    'bomba': {'nome': 'BOMBA', 'tipo': 'bomba', 'valor': 25, 'chance': 0.15,
              'qtd': (1, 1), 'inicial': 1},
}

# Em quem cada tipo de item é usado (o que não está aqui vai num aliado)
ALVO_POR_TIPO = {'adaga': 'inimigo', 'bomba': 'todos'}

QUANTIDADE_INICIAL = 2        # de cada tipo (exceto as que definem 'inicial')
BONUS_CHANCE_POR_FASE = 0.05  


def inventario_inicial():
    return {chave: p.get('inicial', QUANTIDADE_INICIAL) for chave, p in POCOES.items()}


def nome_pocao(chave):
    return POCOES[chave]['nome']


def alvo_item(chave):
    """'aliado' (poções), 'inimigo' (adaga) ou 'todos' (bomba)."""
    return ALVO_POR_TIPO.get(POCOES[chave]['tipo'], 'aliado')


def pode_usar(chave, alvo):
    """Devolve (pode, motivo). A poção só vale em quem está vivo e precisa dela."""
    pocao = POCOES[chave]

    if pocao['tipo'] == 'revive':
        if alvo.vida > 0:
            return False, f'{alvo.nome} não está derrotado!'
        return True, ''

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

    if pocao['tipo'] == 'revive':
        alvo.reviver(pocao['valor'])
        registrar(f'{usuario.nome} usou {pocao["nome"]}: '
                  f'{alvo.nome} voltou com {alvo.vida} de vida!')
    elif pocao['tipo'] == 'hp':
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


def usar_item_de_dano(chave, usuario, alvos, inventario):
    """Usa a adaga (alvos = [o inimigo escolhido]) ou a bomba (alvos = todos
    os inimigos vivos). Retorna True só se o item foi usado de fato."""
    item = POCOES[chave]

    if inventario.get(chave, 0) <= 0:
        registrar(f'Você não tem mais {item["nome"]}!')
        return False

    alvos = [a for a in alvos if a.vida > 0]
    if not alvos:
        registrar('Não existem inimigos vivos!')
        return False

    inventario[chave] -= 1

    if item['tipo'] == 'bomba':
        registrar(f'{usuario.nome} jogou uma {item["nome"]}!')
        for alvo in alvos:
            _causar_dano(alvo, max(1, item['valor'] - alvo.defesa // 2),
                         '{alvo} recebeu {dano} de dano!')
    else:
        alvo = alvos[0]
        _causar_dano(alvo, max(1, item['valor'] - alvo.defesa),
                     f'{usuario.nome} usou {item["nome"]}: '
                     '{dano} de dano em {alvo}!')

    return True


def _causar_dano(alvo, dano, mensagem):
    alvo.vida = max(0, alvo.vida - dano)
    registrar(mensagem.format(alvo=alvo.nome, dano=dano))

    if alvo.defendendo:
        alvo.remover_defesa()

    if alvo.vida == 0:
        registrar(f'{alvo.nome} foi derrotado!')


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
