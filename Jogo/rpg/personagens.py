from .combatentes import Combatente
from .registro import registrar


class Personagem(Combatente):
    """Base dos personagens jogáveis.

    Cada personagem (subclasse) define as PRÓPRIAS habilidades:
      - o dicionário HABILIDADES (chave -> nome, custo de mana, tipo de alvo)
      - um método com o mesmo nome da chave, que faz o efeito

    Tipos de alvo: 'inimigo' (um inimigo), 'todos' (todos os inimigos vivos)
    ou 'nenhum' (age no próprio personagem).
    """

    HABILIDADES = {}

    def __init__(self, nome, vida_maxima, vida, ataque, defesa, velocidade,
                 mana_maxima):
        super().__init__(nome, vida_maxima, vida, ataque, defesa, velocidade)
        self.mana_maxima = mana_maxima
        self.mana = mana_maxima

    # ---------- mana e habilidades ----------
    def restaurar_mana(self):
        self.mana = self.mana_maxima

    def tem_mana(self, chave):
        return self.mana >= self.HABILIDADES[chave]['custo']

    def lista_habilidades(self):
        """Para o menu: (chave, nome, custo de mana, tipo de alvo)."""
        return [
            (chave, info['nome'], info['custo'], info['alvo'])
            for chave, info in self.HABILIDADES.items()
        ]

    def usar_habilidade(self, chave, alvo, inimigos):
        """Tenta usar a habilidade. Retorna True só se ela foi executada
        (assim a Luta sabe se o turno deve passar)."""
        if self.vida <= 0 or chave not in self.HABILIDADES:
            return False

        info = self.HABILIDADES[chave]
        vivos = [i for i in inimigos if i.vida > 0]

        if info['alvo'] == 'inimigo' and alvo not in vivos:
            return False

        if info['alvo'] == 'todos' and not vivos:
            registrar('Não existem inimigos vivos!')
            return False

        if not self.tem_mana(chave):
            registrar(
                f'{self.nome} está sem mana para {info["nome"]} '
                f'(custo {info["custo"]})!'
            )
            return False

        self.mana -= info['custo']
        efeito = getattr(self, chave)

        if info['alvo'] == 'inimigo':
            efeito(alvo)
        elif info['alvo'] == 'todos':
            efeito(vivos)
        else:
            efeito()

        return True

    def inicio_do_turno(self):
        """Chamado pela Luta quando o turno deste personagem começa."""
        pass

    # ---------- utilitário compartilhado ----------
    def _causar_dano(self, alvo, dano, mensagem):
        alvo.vida = max(0, alvo.vida - dano)
        registrar(mensagem)

        if alvo.defendendo:
            alvo.remover_defesa()

        if alvo.vida == 0:
            registrar(f'{alvo.nome} foi derrotado!')


# =====================================================================
# PYTHON - Guerreiro
# =====================================================================
class Guerreiro(Personagem):
    HABILIDADES = {
        'golpe_pesado': {'nome': 'Golpe Pesado', 'custo': 10, 'alvo': 'inimigo'},
        'salto_de_bits': {'nome': 'Salto de Bits', 'custo': 20, 'alvo': 'inimigo'},
    }

    def __init__(self):
        super().__init__('Python', 100, 100, 15, 8, 3, mana_maxima=40)

    def golpe_pesado(self, alvo):
        # Dano fixo: ignora completamente a defesa
        dano = 20
        self._causar_dano(
            alvo, dano,
            f'{self.nome} usou Golpe Pesado: {dano} de dano em {alvo.nome}!'
        )

    def salto_de_bits(self, alvo):
        # Ignora 50% da defesa do inimigo
        dano = max(1, 35 - alvo.defesa // 2)
        self._causar_dano(
            alvo, dano,
            f'{self.nome} usou Salto de Bits: {dano} de dano em {alvo.nome}!'
        )


# =====================================================================
# JAVA - Mago
# =====================================================================
class Mago(Personagem):
    HABILIDADES = {
        'cadeia_de_codigos': {'nome': 'Cadeia de Códigos', 'custo': 15, 'alvo': 'todos'},
        'meteoro_de_variavel': {'nome': 'Meteoro de Variável', 'custo': 30, 'alvo': 'inimigo'},
    }

    def __init__(self):
        super().__init__('Java', 80, 80, 25, 7, 2, mana_maxima=60)

    def cadeia_de_codigos(self, alvos):
        registrar(f'{self.nome} lançou Cadeia de Códigos!')

        for inimigo in alvos:
            dano = max(1, 25 - inimigo.defesa)
            self._causar_dano(
                inimigo, dano, f'{inimigo.nome} recebeu {dano} de dano!'
            )

    def meteoro_de_variavel(self, alvo):
        registrar(f'{self.nome} lançou Meteoro de Variável!')
        dano = max(1, 40 - alvo.defesa // 2)
        self._causar_dano(alvo, dano, 
        f'{alvo.nome} recebeu {dano} de dano!'
        )


# =====================================================================
# JAVASCRIPT - Ladino
# =====================================================================
class Ladino(Personagem):
    HABILIDADES = {
        'investida_assincrona': {'nome': 'Investida Assíncrona', 'custo': 10, 'alvo': 'inimigo'},
        'rajada_de_scripts': {'nome': 'Rajada de Scripts', 'custo': 20, 'alvo': 'inimigo'},
    }

    def __init__(self):
        super().__init__('JavaScript', 90, 90, 20, 6, 5, mana_maxima=40)

    def investida_assincrona(self, alvo):
        # Ignora 25% da defesa do inimigo
        dano = max(1, 30 - int(alvo.defesa * 0.75))
        self._causar_dano(
            alvo, dano,
            f'{self.nome} usou Investida Assíncrona: {dano} de dano em {alvo.nome}!'
        )

    def rajada_de_scripts(self, alvo):
        registrar(f'{self.nome} usou Rajada de Scripts!')

        for golpe in range(1, 4):
            if alvo.vida <= 0:
                break

            dano = max(1, 15 - alvo.defesa)
            self._causar_dano(
                alvo, dano, f'Golpe {golpe}: {dano} de dano em {alvo.nome}!'
            )


# =====================================================================
# C# - Paladino
# =====================================================================
class Paladino(Personagem):
    HABILIDADES = {
        'escudo_de_compilacao': {'nome': 'Escudo de Compilação', 'custo': 10, 'alvo': 'nenhum'},
        'codigo_divino': {'nome': 'Código Divino', 'custo': 30, 'alvo': 'inimigo'},
    }

    def __init__(self):
        super().__init__('C#', 150, 150, 10, 10, 1, mana_maxima=50)
        self.escudo_compilacao_ativo = False

    def escudo_de_compilacao(self):
        self.defesa += 20
        self.escudo_compilacao_ativo = True
        registrar(f'{self.nome} usou Escudo de Compilação! Defesa +20')

    def codigo_divino(self, alvo):
        # Ignora 50% da defesa do alvo
        dano = max(1, 40 - alvo.defesa // 2)
        self._causar_dano(
            alvo, dano,
            f'{self.nome} usou Código Divino: {dano} de dano em {alvo.nome}!'
        )

    def inicio_do_turno(self):
        # O escudo dura até o próximo turno do Paladino
        if self.escudo_compilacao_ativo:
            self.defesa -= 20
            self.escudo_compilacao_ativo = False
            registrar(f'Escudo de Compilação de {self.nome} terminou!')


# =====================================================================
# PERSONAGENS DISPONÍVEIS
# =====================================================================
guerreiro = Guerreiro()
mago = Mago()
ladino = Ladino()
paladino = Paladino()

personagens_liberados = [
    guerreiro,
    mago,
    ladino,
    paladino,
]
