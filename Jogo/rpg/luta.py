
import random
from .registro import registrar

from .habilidades import (
    picada_mortal,
    salto_de_bits,
    cadeia_de_codigos,
    meteoro_de_variavel,
    investida_assincrona,
    rajada_de_scripts,
    escudo_de_compilacao,
    codigo_divino
)

class Luta:
    def __init__(self, grupo_jogador, grupo_inimigos):
        self.grupo_jogador = grupo_jogador
        self.grupo_inimigos = grupo_inimigos

        # Restaura as habilidades no início da luta
        for personagem in self.grupo_jogador:
            personagem.reiniciar_habilidades()

        self.participantes = grupo_jogador + grupo_inimigos

        self.ordem_turnos = sorted(
            self.participantes,
            key=lambda c: c.velocidade,
            reverse=True
        )

        self.indice_turno = 0
        self.tempo_inimigo = 0
        self.resultado = None

    def combatente_atual(self):
        if self.resultado:
            return None

        if not self.ordem_turnos:
            return None

        return self.ordem_turnos[self.indice_turno]

    def verificar_fim(self):
        jogadores_vivos = any(
            p.vida > 0 for p in self.grupo_jogador
        )

        inimigos_vivos = any(
            i.vida > 0 for i in self.grupo_inimigos
        )

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
            self.indice_turno = (
                self.indice_turno + 1
            ) % quantidade

            combatente = self.combatente_atual()

            if combatente and combatente.vida > 0:

                # Remove o Escudo de Compilação
                # quando chega novamente o turno do Paladino
                if (
                    combatente in self.grupo_jogador
                    and getattr(combatente, "escudo_compilacao_ativo", False)
                ):
                   combatente.defesa -= 20
                   combatente.escudo_compilacao_ativo = False

                   print(f"Escudo de Compilação de {combatente.nome} terminou!")

                return

def executar_acao_jogador(self, acao, alvo=None):
    combatente = self.combatente_atual()

    if combatente not in self.grupo_jogador:
        return

    if combatente.vida <= 0:
        return

    if acao == "atacar":
        if alvo not in self.grupo_inimigos:
            return

        if alvo.vida <= 0:
            return

        combatente.atacar(alvo)

    elif acao == "defender":
        combatente.defender()

    elif acao == "picada_mortal":
        if "picada_mortal" not in combatente.usos_habilidades:
            return

        if alvo not in self.grupo_inimigos or alvo.vida <= 0:
            return

        if picada_mortal(combatente, alvo):
            self.avancar_turno()

        return

    elif acao == "salto_de_bits":
        if "salto_de_bits" not in combatente.usos_habilidades:
            return

        if alvo not in self.grupo_inimigos or alvo.vida <= 0:
            return

        if salto_de_bits(combatente, alvo):
            self.avancar_turno()

        return

    elif acao == "cadeia_de_codigos":
        if "cadeia_de_codigos" not in combatente.usos_habilidades:
            return

        if cadeia_de_codigos(combatente, self.grupo_inimigos):
            self.avancar_turno()

        return

    elif acao == "meteoro_de_variavel":
        if "meteoro_de_variavel" not in combatente.usos_habilidades:
            return

        if meteoro_de_variavel(combatente, self.grupo_inimigos):
            self.avancar_turno()

            return

    
    elif acao == "investida_assincrona":
        if alvo not in self.grupo_inimigos or alvo.vida <= 0:
            return

        if investida_assincrona(combatente, alvo):
            self.avancar_turno()

            return

    elif acao == "rajada_de_scripts":
        if alvo not in self.grupo_inimigos or alvo.vida <= 0:
            return

        if rajada_de_scripts(combatente, alvo):
            self.avancar_turno()

            return

    elif acao == "escudo_de_compilacao":
        if escudo_de_compilacao(combatente):
            self.avancar_turno()

            return

    elif acao == "codigo_divino":
        if alvo not in self.grupo_inimigos or alvo.vida <= 0:
            return

        if codigo_divino(combatente, alvo):
            self.avancar_turno()

            return

    else:
        return

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
                    alvos = [
                        p for p in self.grupo_jogador
                        if p.vida > 0
                    ]

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
