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
        self.efeitos = []  # escudos, reduções de defesa... (ver aplicar_efeito)

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

        setattr(self, atributo, getattr(self, atributo) + delta)
        self.efeitos.append({
            'chave': chave, 'rotulo': rotulo, 'atributo': atributo,
            'delta': delta, 'turnos': turnos,
        })

    def inicio_do_turno(self):
        """Chamado pela Luta quando começa o turno deste combatente."""
        for efeito in list(self.efeitos):
            efeito['turnos'] -= 1
            if efeito['turnos'] <= 0:
                self._desfazer_efeito(efeito)
                registrar(f'{self.nome}: {efeito["rotulo"]} terminou!')

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
