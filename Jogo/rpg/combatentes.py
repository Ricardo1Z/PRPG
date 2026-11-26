from .registro import registrar


def causar_dano(alvo, dano, mensagem):
    """Tira `dano` de vida do alvo, registra a mensagem, quebra a defesa dele
    e avisa se ele foi derrotado."""
    alvo.vida = max(0, alvo.vida - dano)
    registrar(mensagem)

    if alvo.defendendo:
        alvo.remover_defesa()

    if alvo.vida == 0:
        registrar(f'{alvo.nome} foi derrotado!')


class Combatente:
    def __init__(self, nome, vida_maxima, vida, ataque, defesa, velocidade):
        self.nome = nome
        self.vida_maxima = vida_maxima
        self.danos_recentes = []  # danos ainda não mostrados na tela (ver vida.setter)
        self._vida = vida
        self.ataque = ataque
        self.defesa = defesa
        self.velocidade = velocidade
        self.defendendo = False
        self.efeitos = []  # escudos, reduções de defesa... (ver aplicar_efeito)
        # Contadores usados por efeitos temporários (0 = desligado):
        self.provocacao = 0  # > 0: inimigos só atacam quem está provocando
        self.intangivel = 0  # > 0: inimigos não conseguem atacar

    # ---------- vida ----------
    # Toda vez que a vida cai, a perda é anotada em `danos_recentes`; a tela
    # de batalha lê essa lista para piscar o sprite e mostrar o "-N" flutuando.
    @property
    def vida(self):
        return self._vida

    @vida.setter
    def vida(self, valor):
        perda = self._vida - valor
        if perda > 0:
            self.danos_recentes.append(perda)
        self._vida = valor

    def atacar(self, alvo):
        if self.vida <= 0:
            registrar(f'{self.nome} está derrotado e não pode agir!')
            return 0

        if alvo.vida <= 0:
            registrar(f'{alvo.nome} já está derrotado!')
            return 0

        dano_real = max(1, self.ataque - alvo.defesa)
        causar_dano(alvo, dano_real,
                    f'{self.nome} atacou {alvo.nome}: {dano_real} de dano!')
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

    # ---------- efeitos temporários ----------
    def aplicar_efeito(self, chave, rotulo, atributo, delta, turnos):
        """Muda um atributo (ex.: 'defesa') por `turnos` turnos DESTE combatente.

        A contagem diminui no início de cada turno dele; ao chegar a 0 o
        efeito acaba e o atributo volta ao normal. Aplicar o mesmo efeito de
        novo só renova a duração (não acumula)."""
        for efeito in self.efeitos:
            if efeito['chave'] == chave:
                efeito['turnos'] = max(efeito['turnos'], turnos)
                return

        if atributo == 'defesa' and delta < 0:
            delta = -min(self.defesa, -delta)  # a defesa nunca fica negativa
        if atributo == 'ataque' and delta < 0:
            delta = -min(self.ataque - 1, -delta)  # o ataque fica no mínimo 1

        setattr(self, atributo, getattr(self, atributo) + delta)
        self.efeitos.append({
            'chave': chave, 'rotulo': rotulo, 'atributo': atributo,
            'delta': delta, 'turnos': turnos,
        })

    def inicio_do_turno(self):
        """Chamado pela Luta quando começa o turno deste combatente."""
        avisados = set()  # efeitos com várias partes avisam uma vez só
        for efeito in list(self.efeitos):
            efeito['turnos'] -= 1
            if efeito['turnos'] <= 0:
                self._desfazer_efeito(efeito)
                if efeito['rotulo'] not in avisados:
                    avisados.add(efeito['rotulo'])
                    registrar(f'{self.nome}: {efeito["rotulo"]} terminou!')

    def remover_efeito(self, chave):
        """Encerra antes da hora o efeito com essa chave (se existir)."""
        for efeito in list(self.efeitos):
            if efeito['chave'] == chave:
                self._desfazer_efeito(efeito)

    def limpar_efeitos(self):
        for efeito in list(self.efeitos):
            self._desfazer_efeito(efeito)

    def _desfazer_efeito(self, efeito):
        setattr(self, efeito['atributo'],
                getattr(self, efeito['atributo']) - efeito['delta'])
        self.efeitos.remove(efeito)

    # ---------- reviver ----------
    def reviver(self, fracao_da_vida):
        """Traz um combatente derrotado de volta com uma parte da vida."""
        self.limpar_efeitos()
        self.remover_defesa()
        self.vida = max(1, int(self.vida_maxima * fracao_da_vida))
