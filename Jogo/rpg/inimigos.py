import copy
import random

from .combatentes import Combatente


def sortear(**pesos):
    """Sorteia uma ação pelo peso de cada uma, ex.: sortear(atacar=70, fugir=30)."""
    return random.choices(list(pesos), weights=list(pesos.values()))[0]


class Inimigo(Combatente):
    def __init__(self, nome, vida_maxima, vida, ataque, defesa, velocidade, prob_ataque):
        super().__init__(nome, vida_maxima, vida, ataque, defesa, velocidade)
        self.prob_ataque = prob_ataque

    def escolher_acao(self):
        return sortear(atacar=self.prob_ataque, defender=100 - self.prob_ataque)

    def vida_abaixo(self, fracao):
        return self.vida <= self.vida_maxima * fracao


class Slime(Inimigo):
    def escolher_acao(self):
        return 'atacar'


class Inseto(Inimigo):
    def escolher_acao(self):
        if self.vida_abaixo(0.3):
            return 'defender'
        return super().escolher_acao()


class Aranha(Inimigo):
    def escolher_acao(self):
        if self.vida_abaixo(0.2):
            return sortear(atacar=60, fugir=40)
        return super().escolher_acao()


class Goblin(Inimigo):
    def escolher_acao(self):
        if self.vida_abaixo(0.6):
            return sortear(atacar=70, fugir=30)
        return super().escolher_acao()


class Golem(Inimigo):
    def escolher_acao(self):
        if self.vida_abaixo(0.4):
            return sortear(atacar=10, defender=90)
        return super().escolher_acao()


class Doppelganger(Inimigo):
    def escolher_acao(self):
        if self.vida_abaixo(0.5):
            return sortear(atacar=50, defender=30, fugir=20)
        return super().escolher_acao()


class Virus(Inimigo):
    def escolher_acao(self):
        if self.vida >= self.vida_maxima * 0.45:
            return 'atacar'
        return super().escolher_acao()


class Dragao(Inimigo):
    def escolher_acao(self):
        if self.vida >= self.vida_maxima * 0.6:
            return sortear(atacar=75, defender=25)
        return super().escolher_acao()


class Compilador(Inimigo):
    def escolher_acao(self):
        if self.vida >= self.vida_maxima * 0.5:
            return sortear(atacar=70, defender=30)
        return super().escolher_acao()


class BugOriginal(Inimigo):
    def escolher_acao(self):
        if self.vida >= self.vida_maxima * 0.5:
            return 'atacar'
        return super().escolher_acao()


# Modelos de inimigos. Use criar_inimigo() para ter uma cópia nova a cada luta
# (nome, vida máx., vida, ataque, defesa, velocidade, % de chance de atacar)
INIMIGOS = {
    'slime': Slime('Slime de Código', 45, 45, 15, 2, 1, 100),
    'inseto': Inseto('Inseto Bugado', 60, 60, 18, 4, 2, 65),
    'aranha': Aranha('Aranha de Firewall', 50, 50, 21, 3, 3, 80),       # foge
    'goblin': Goblin('Goblin de Sintaxe', 55, 55, 17, 2, 4, 75),        # foge
    'golem': Golem('Golem de Erro de Compilação', 170, 170, 32, 12, 1, 45),
    'doppelganger': Doppelganger('Plagiador de Código', 110, 110, 30, 6, 3, 60),  # foge
    'virus': Virus('Vírus Corrompido', 120, 120, 28, 5, 2, 80),
    'dragao': Dragao('Dragão do Infinito', 260, 260, 38, 10, 1, 90),
    'compilador': Compilador('Compilador Supremo', 340, 340, 40, 14, 1, 90),
    'bug_original': BugOriginal('Bug Original', 480, 480, 36, 12, 1, 95),
}


def criar_inimigo(chave):
    inimigo = copy.deepcopy(INIMIGOS[chave])
    inimigo.chave = chave  # usada pela batalha para achar o sprite
    return inimigo
