from .registro import registrar


class Combatente:
    def __init__(self, nome, vida_maxima, vida, ataque, defesa, velocidade):
        self.nome = nome
        self.vida_maxima = vida_maxima
        self.vida = vida
        self.ataque = ataque
        self.defesa = defesa
        self.velocidade = velocidade
        self.defendendo = False

    def atacar(self, alvo):
        if self.vida <= 0:
            registrar(f'{self.nome} está derrotado e não pode agir!')
            return 0

        if alvo.vida <= 0:
            registrar(f'{alvo.nome} já está derrotado!')
            return 0

        dano_real = max(1, self.ataque - alvo.defesa)
        alvo.vida = max(0, alvo.vida - dano_real)
        registrar(f'{self.nome} atacou {alvo.nome}: {dano_real} de dano!')

        if alvo.defendendo:
            alvo.remover_defesa()

        if alvo.vida == 0:
            registrar(f'{alvo.nome} foi derrotado!')

        return dano_real

    def defender(self):
        if not self.defendendo:
            self.defesa += 10
            self.defendendo = True
            registrar(f'{self.nome} entrou em posição defensiva!')

    def remover_defesa(self):
        if self.defendendo:
            self.defesa -= 10
            self.defendendo = False
