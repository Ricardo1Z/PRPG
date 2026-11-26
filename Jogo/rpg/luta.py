import random

from .registro import registrar
from . import itens

ESPERA_ACAO = 45


class Luta:
    def __init__(self, grupo_jogador, grupo_inimigos):
        self.grupo_jogador = grupo_jogador
        self.grupo_inimigos = grupo_inimigos

        self.ordem_turnos = sorted(
            grupo_jogador + grupo_inimigos,
            key=lambda c: c.velocidade,
            reverse=True
        )

        self.invocacoes = []

        self.indice_turno = 0
        self.tempo_inimigo = 0
        self.resultado = None

        # O 1º turno é do combatente VIVO mais rápido. Sem isso, quem morreu
        # numa luta anterior (a vida dos personagens passa de uma fase para
        # a outra) começaria com a vez e o jogo travaria.
        if self.ordem_turnos and self.ordem_turnos[0].vida <= 0:
            self.indice_turno = len(self.ordem_turnos) - 1
            self.avancar_turno()

    def combatente_atual(self):
        if self.resultado or not self.ordem_turnos:
            return None
        return self.ordem_turnos[self.indice_turno]

    def verificar_fim(self):
        jogadores_vivos = any(p.vida > 0 for p in self.grupo_jogador)
        inimigos_vivos = any(i.vida > 0 for i in self.grupo_inimigos)

        if not jogadores_vivos:
            self.resultado = "derrota"

        elif not inimigos_vivos:
            self.resultado = "vitoria"

    def avancar_turno(self):
        self.verificar_fim()

        if self.resultado:
            return

        quantidade = len(self.ordem_turnos)

        for _ in range(quantidade):
            self.indice_turno = (self.indice_turno + 1) % quantidade

            combatente = self.combatente_atual()

            if combatente and combatente.vida > 0:

                # Início do turno: escudos e reduções de defesa vão acabando
                combatente.inicio_do_turno()

                return

    def executar_acao_jogador(self, acao, alvo=None):
        combatente = self.combatente_atual()

        if combatente not in self.grupo_jogador:
            return

        if combatente.vida <= 0:
            return

        # Cada ramo faz "return" se a ação NÃO pôde ser feita (sem alvo
        # válido, sem mana...), assim o turno só passa quando deu certo.
        if acao == "atacar":
            if alvo not in self.grupo_inimigos or alvo.vida <= 0:
                return

            combatente.atacar(alvo)

        elif acao == "defender":
            combatente.defender()

        elif acao in combatente.HABILIDADES:
            # Habilidade do personagem (classe dele). Se não deu certo
            # (alvo inválido, sem mana...), o turno NÃO passa.
            if not combatente.usar_habilidade(
                acao, alvo, self.grupo_inimigos, self.grupo_jogador
            ):
                return

        else:
            return

        # Só chega aqui se a ação deu certo
        self.receber_invocacoes()
        self.avancar_turno()

    def receber_invocacoes(self):
        """Coloca na ordem de turnos as invocações novas do time. Ela entra
        logo ANTES de quem invocou, então só age na próxima rodada."""
        for p in self.grupo_jogador:
            inv = getattr(p, 'invocacao', None)
            if inv is not None and inv not in self.invocacoes:
                self.invocacoes.append(inv)
                posicao = self.ordem_turnos.index(p)
                self.ordem_turnos.insert(posicao, inv)
                if posicao <= self.indice_turno:
                    self.indice_turno += 1

    def usar_pocao(self, chave, alvo, inventario):
        """O personagem da vez usa um item e gasta o turno: poção em alvo
        (um aliado), adaga em alvo (um inimigo) ou bomba (todos os
        inimigos, alvo é ignorado). Se não deu certo (sem estoque, vida/mana
        já cheia), o turno não passa."""
        combatente = self.combatente_atual()

        if combatente not in self.grupo_jogador or combatente.vida <= 0:
            return

        tipo_alvo = itens.alvo_item(chave)

        if tipo_alvo == 'inimigo':  # adaga
            if alvo not in self.grupo_inimigos or alvo.vida <= 0:
                return
            if not itens.usar_item_de_dano(chave, combatente, [alvo], inventario):
                return

        elif tipo_alvo == 'todos':  # bomba (não precisa de alvo)
            if not itens.usar_item_de_dano(chave, combatente, self.grupo_inimigos, inventario):
                return

        else:  # poções: num aliado
            if alvo not in self.grupo_jogador:
                return
            if not itens.usar_pocao(chave, combatente, alvo, inventario):
                return

        self.avancar_turno()

    def atualizar(self):
        self.verificar_fim()

        if self.resultado:
            return

        combatente = self.combatente_atual()

        if combatente in self.invocacoes:
            # Invocação: espera um pouco e ataca um inimigo vivo aleatório
            self.tempo_inimigo += 1
            if self.tempo_inimigo >= ESPERA_ACAO:
                self.tempo_inimigo = 0
                alvos = [i for i in self.grupo_inimigos if i.vida > 0]
                if alvos:
                    combatente.atacar(random.choice(alvos))
                self.avancar_turno()

        elif combatente in self.grupo_inimigos:
            self.tempo_inimigo += 1

            # Espera um pouco antes da ação do inimigo
            if self.tempo_inimigo >= ESPERA_ACAO:
                self.tempo_inimigo = 0

                acao = combatente.escolher_acao()

                if acao == "atacar":
                    # Intangíveis não podem ser atacados; se alguém está
                    # provocando, os inimigos só atacam quem provoca.
                    alvos = [p for p in self.grupo_jogador + self.invocacoes
                             if p.vida > 0 and p.intangivel <= 0]
                    provocando = [p for p in alvos if p.provocacao > 0]
                    if provocando:
                        alvos = provocando

                    if alvos:
                        alvo = random.choice(alvos)
                        combatente.atacar(alvo)
                    else:
                        registrar(f"{combatente.nome} não encontrou ninguém para atacar!")

                elif acao == "defender":
                    combatente.defender()

                elif acao == "fugir":
                    registrar(f"{combatente.nome} fugiu!")

                    self.grupo_inimigos.remove(combatente)
                    self.ordem_turnos.remove(combatente)

                    self.verificar_fim()
                    if self.resultado:
                        return

                    # Recua um passo para o avancar_turno() cair no próximo
                    # combatente VIVO (evita travar num jogador morto)
                    self.indice_turno = (
                        self.indice_turno - 1
                    ) % len(self.ordem_turnos)
                    self.avancar_turno()
                    return

                self.avancar_turno()
        else:
            self.tempo_inimigo = 0
