import random

from .registro import registrar


class Luta:
    def __init__(self, grupo_jogador, grupo_inimigos):
        self.grupo_jogador = grupo_jogador
        self.grupo_inimigos = grupo_inimigos

        # Restaura a mana no início de cada luta
        for personagem in self.grupo_jogador:
            personagem.restaurar_mana()

        self.participantes = grupo_jogador + grupo_inimigos

        self.ordem_turnos = sorted(
            self.participantes,
            key=lambda c: c.velocidade,
            reverse=True
        )

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
        if self.resultado:
            return None

        if not self.ordem_turnos:
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

                # Cada personagem trata o que acontece no início do seu turno
                # (ex.: o Paladino remove o Escudo de Compilação)
                if combatente in self.grupo_jogador:
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
            if not combatente.usar_habilidade(acao, alvo, self.grupo_inimigos):
                return

        else:
            return

        # Só chega aqui se a ação deu certo
        self.avancar_turno()

    def atualizar(self):
        self.verificar_fim()

        if self.resultado:
            return

        combatente = self.combatente_atual()

        if combatente in self.grupo_inimigos:
            self.tempo_inimigo += 1

            # Espera um pouco antes da ação do inimigo
            if self.tempo_inimigo >= 45:
                self.tempo_inimigo = 0

                acao = combatente.escolher_acao()

                if acao == "atacar":
                    alvos = [p for p in self.grupo_jogador if p.vida > 0]

                    if alvos:
                        alvo = random.choice(alvos)
                        combatente.atacar(alvo)

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
