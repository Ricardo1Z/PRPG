
from .combatentes import Combatente

class Personagem(Combatente):
    def __init__(self, nome, vida_maxima, vida, ataque, defesa, velocidade):
        super().__init__(nome, vida_maxima, vida, ataque, defesa, velocidade)

        self.limite_habilidades = {}
        self.usos_habilidades = {}

    def registrar_habilidade(self, nome, usos_maximos):
        self.limite_habilidades[nome] = usos_maximos
        self.usos_habilidades[nome] = usos_maximos

    def consumir_uso_habilidade(self, nome):
        if self.usos_habilidades.get(nome, 0) > 0:
            self.usos_habilidades[nome] -= 1
            return True

        print(f'{self.nome} não possui mais usos dessa habilidade!')
        return False

    def reiniciar_habilidades(self):
        self.usos_habilidades = self.limite_habilidades.copy()


# PERSONAGENS
guerreiro = Personagem('Python', 100, 100, 15, 8, 3)
mago = Personagem('Java', 80, 80, 25, 7, 2)
ladino = Personagem('JavaScript', 90, 90, 20, 6, 5)
paladino = Personagem('C#', 150, 150, 10, 10, 1)

# HABILIDADES
guerreiro.registrar_habilidade('picada_mortal', 2)
guerreiro.registrar_habilidade('salto_de_bits', 1)
mago.registrar_habilidade('cadeia_de_codigos', 2)
mago.registrar_habilidade('meteoro_de_variavel', 1)
ladino.registrar_habilidade('investida_assincrona', 2)
ladino.registrar_habilidade('rajada_de_scripts', 1)
paladino.registrar_habilidade('escudo_de_compilacao', 2)
paladino.registrar_habilidade('codigo_divino', 1)

personagens_liberados = [
    guerreiro,
    mago,
    ladino,
    paladino
]
