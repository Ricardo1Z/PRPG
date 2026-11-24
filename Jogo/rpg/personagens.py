from .combatentes import Combatente
from .registro import registrar


class Personagem(Combatente):
    """Base dos personagens jogáveis.

    Cada personagem (subclasse) define as PRÓPRIAS habilidades:
      - o dicionário HABILIDADES (chave -> nome, custo de mana, tipo de alvo)
      - um método com o mesmo nome da chave, que faz o efeito
    e também CLASSE (nome da classe) e SPRITE (imagem em assets/sprites/personagens).

    Tipos de alvo da habilidade (o que o método recebe):
      'inimigo' -> (alvo)     um inimigo escolhido pelo jogador
      'todos'   -> (alvos)    todos os inimigos vivos
      'nenhum'  -> ()         age só no próprio personagem
      'time'    -> (aliados)  todos os aliados vivos (inclui ele mesmo)
      'aliado'  -> (alvo)     um aliado vivo e ferido, escolhido pelo jogador
      'mortos'  -> (mortos)   todos os aliados derrotados
    """

    HABILIDADES = {}
    CLASSE = ''
    SPRITE = ''

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

    def usar_habilidade(self, chave, alvo, inimigos, aliados=()):
        """Tenta usar a habilidade. Retorna True só se ela foi executada
        (assim a Luta sabe se o turno deve passar)."""
        if self.vida <= 0 or chave not in self.HABILIDADES:
            return False

        info = self.HABILIDADES[chave]
        tipo = info['alvo']
        vivos = [i for i in inimigos if i.vida > 0]
        aliados_vivos = [a for a in aliados if a.vida > 0]
        mortos = [a for a in aliados if a.vida <= 0]

        if tipo == 'inimigo' and alvo not in vivos:
            return False

        if tipo == 'todos' and not vivos:
            registrar('Não existem inimigos vivos!')
            return False

        if tipo == 'aliado':
            if alvo not in aliados_vivos:
                return False
            if alvo.vida >= alvo.vida_maxima:
                registrar(f'{alvo.nome} já está com a vida cheia!')
                return False

        if tipo == 'mortos' and not mortos:
            registrar('Nenhum aliado está derrotado!')
            return False

        if not self.tem_mana(chave):
            registrar(
                f'{self.nome} está sem mana para {info["nome"]} '
                f'(custo {info["custo"]})!'
            )
            return False

        self.mana -= info['custo']
        efeito = getattr(self, chave)

        if tipo in ('inimigo', 'aliado'):
            efeito(alvo)
        elif tipo == 'todos':
            efeito(vivos)
        elif tipo == 'time':
            efeito(aliados_vivos)
        elif tipo == 'mortos':
            efeito(mortos)
        else:
            efeito()

        return True

    # ---------- utilitários compartilhados ----------
    def _causar_dano(self, alvo, dano, mensagem):
        alvo.vida = max(0, alvo.vida - dano)
        registrar(mensagem)

        if alvo.defendendo:
            alvo.remover_defesa()

        if alvo.vida == 0:
            registrar(f'{alvo.nome} foi derrotado!')

    def _golpes(self, alvo, golpes, dano_base):
        """Vários golpes seguidos no mesmo alvo (a defesa conta em cada um).
        Retorna o dano total causado. Depois de anunciar o resultado, chame
        _anunciar_derrota(alvo)."""
        total = 0
        for _ in range(golpes):
            if alvo.vida <= 0:
                break
            dano = max(1, dano_base - alvo.defesa)
            alvo.vida = max(0, alvo.vida - dano)
            total += dano
            if alvo.defendendo:
                alvo.remover_defesa()
        return total

    def _anunciar_derrota(self, alvo):
        if alvo.vida == 0:
            registrar(f'{alvo.nome} foi derrotado!')


# =====================================================================
# PYTHON - Guerreiro
# =====================================================================
class Guerreiro(Personagem):
    CLASSE = 'Guerreiro'
    SPRITE = 'gpython.png'
    HABILIDADES = {
        'picada_mortal': {'nome': 'Picada Mortal', 'custo': 10, 'alvo': 'inimigo'},
        'salto_de_bits': {'nome': 'Salto de Bits', 'custo': 20, 'alvo': 'inimigo'},
    }

    def __init__(self):
        super().__init__('Python', 100, 100, 15, 8, 3, mana_maxima=40)

    def picada_mortal(self, alvo):
        # Dano fixo: ignora completamente a defesa
        dano = 20
        self._causar_dano(
            alvo, dano,
            f'{self.nome} usou Picada Mortal: {dano} de dano em {alvo.nome}!'
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
    CLASSE = 'Mago'
    SPRITE = 'mjava.png'
    HABILIDADES = {
        'cadeia_de_codigos': {'nome': 'Cadeia de Códigos', 'custo': 15, 'alvo': 'todos'},
        'meteoro_de_variavel': {'nome': 'Meteoro de Variável', 'custo': 30, 'alvo': 'todos'},
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

    def meteoro_de_variavel(self, alvos):
        registrar(f'{self.nome} lançou Meteoro de Variável!')

        for inimigo in alvos:
            # Ignora 50% da defesa
            dano = max(1, 40 - inimigo.defesa // 2)
            self._causar_dano(
                inimigo, dano, f'{inimigo.nome} recebeu {dano} de dano!'
            )


# =====================================================================
# JAVASCRIPT - Ladino
# =====================================================================
class Ladino(Personagem):
    CLASSE = 'Ladino'
    SPRITE = 'Ljavascript.png'
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
    CLASSE = 'Paladino'
    SPRITE = 'Cpaladino.png'
    HABILIDADES = {
        'escudo_de_compilacao': {'nome': 'Escudo de Compilação', 'custo': 10, 'alvo': 'nenhum'},
        'codigo_divino': {'nome': 'Código Divino', 'custo': 30, 'alvo': 'inimigo'},
    }

    def __init__(self):
        super().__init__('C#', 150, 150, 10, 10, 1, mana_maxima=50)

    def escudo_de_compilacao(self):
        # +20 de defesa até o próximo turno do Paladino
        self.aplicar_efeito('escudo_de_compilacao', 'Escudo de Compilação',
                            'defesa', 20, 1)
        registrar(f'{self.nome} usou Escudo de Compilação! Defesa +20')

    def codigo_divino(self, alvo):
        # Ignora 50% da defesa do alvo
        dano = max(1, 40 - alvo.defesa // 2)
        self._causar_dano(
            alvo, dano,
            f'{self.nome} usou Código Divino: {dano} de dano em {alvo.nome}!'
        )


# =====================================================================
# C++ - Engenheiro  (desbloqueado ao zerar o jogo 1 vez)
# =====================================================================
class Engenheiro(Personagem):
    CLASSE = 'Engenheiro'
    SPRITE = 'Cengenheiro.png'
    HABILIDADES = {
        'barreira_de_ponteiros': {'nome': 'Barreira de Ponteiros', 'custo': 25, 'alvo': 'time'},
        'falha_de_segmentacao': {'nome': 'Falha de Segmentação', 'custo': 20, 'alvo': 'inimigo'},
    }

    def __init__(self):
        super().__init__('C++', 110, 110, 14, 9, 2, mana_maxima=55)

    def barreira_de_ponteiros(self, aliados):
        # Escudo no time inteiro: +12 de defesa por 2 turnos de cada um
        registrar(f'{self.nome} ergueu a Barreira de Ponteiros! Defesa do time +12')

        for aliado in aliados:
            aliado.aplicar_efeito('barreira_de_ponteiros', 'Barreira de Ponteiros',
                                  'defesa', 12, 2)

    def falha_de_segmentacao(self, alvo):
        # Dano singular (a defesa do alvo conta normalmente)
        dano = max(1, 36 - alvo.defesa)
        self._causar_dano(
            alvo, dano,
            f'{self.nome} usou Falha de Segmentação: {dano} de dano em {alvo.nome}!'
        )


# =====================================================================
# DELPHI - Lanceiro  (desbloqueado ao zerar o jogo 2 vezes)
# =====================================================================
class Lanceiro(Personagem):
    CLASSE = 'Lanceiro'
    SPRITE = 'Dlanceiro.png'
    HABILIDADES = {
        'estocada_em_cascata': {'nome': 'Estocada em Cascata', 'custo': 25, 'alvo': 'inimigo'},
        'giro_de_unidade': {'nome': 'Giro de Unidade', 'custo': 20, 'alvo': 'todos'},
    }

    def __init__(self):
        super().__init__('Delphi', 120, 120, 18, 8, 3, mana_maxima=45)

    def estocada_em_cascata(self, alvo):
        # Dano singular em 3 golpes
        total = self._golpes(alvo, 3, 16)
        registrar(f'{self.nome} usou Estocada em Cascata: '
                  f'3 golpes, {total} de dano em {alvo.nome}!')
        self._anunciar_derrota(alvo)

    def giro_de_unidade(self, alvos):
        # Dano em área
        registrar(f'{self.nome} usou Giro de Unidade!')

        for inimigo in alvos:
            dano = max(1, 22 - inimigo.defesa)
            self._causar_dano(
                inimigo, dano, f'{inimigo.nome} recebeu {dano} de dano!'
            )


# =====================================================================
# PHP - Arqueiro  (desbloqueado ao zerar o jogo 3 vezes)
# =====================================================================
class Arqueiro(Personagem):
    CLASSE = 'Arqueiro'
    SPRITE = 'Parqueiro.png'
    HABILIDADES = {
        'chuva_de_requisicoes': {'nome': 'Chuva de Requisições', 'custo': 25, 'alvo': 'todos'},
        'injecao_de_sql': {'nome': 'Injeção de SQL', 'custo': 20, 'alvo': 'inimigo'},
    }

    def __init__(self):
        super().__init__('PHP', 85, 85, 22, 5, 4, mana_maxima=50)

    def chuva_de_requisicoes(self, alvos):
        # Dano em área, 3 golpes em cada inimigo
        registrar(f'{self.nome} usou Chuva de Requisições! (3 golpes em cada)')

        for inimigo in alvos:
            total = self._golpes(inimigo, 3, 14)
            registrar(f'{inimigo.nome} recebeu {total} de dano!')
            self._anunciar_derrota(inimigo)

    def injecao_de_sql(self, alvo):
        # Dano singular fixo: ignora completamente a defesa
        dano = 30
        self._causar_dano(
            alvo, dano,
            f'{self.nome} usou Injeção de SQL: {dano} de dano (ignora defesa) em {alvo.nome}!'
        )


# =====================================================================
# RUBY - Hexxer  (desbloqueado ao zerar o jogo 4 vezes)
# =====================================================================
class Hexxer(Personagem):
    CLASSE = 'Hexxer'
    SPRITE = 'Rhexxer.png'
    HABILIDADES = {
        'reiniciar_processo': {'nome': 'Reiniciar Processo', 'custo': 40, 'alvo': 'mortos'},
        'cura_em_bloco': {'nome': 'Cura em Bloco', 'custo': 15, 'alvo': 'aliado'},
        'monkey_patch': {'nome': 'Monkey Patch', 'custo': 20, 'alvo': 'todos'},
    }

    def __init__(self):
        super().__init__('Ruby', 75, 75, 18, 5, 2, mana_maxima=70)

    def reiniciar_processo(self, mortos):
        # Revive todos os aliados derrotados com 30% da vida
        registrar(f'{self.nome} usou Reiniciar Processo!')

        for aliado in mortos:
            aliado.reviver(0.30)
            registrar(f'{aliado.nome} voltou com {aliado.vida} de vida!')

    def cura_em_bloco(self, alvo):
        recuperado = min(40, alvo.vida_maxima - alvo.vida)
        alvo.vida += recuperado
        registrar(f'{self.nome} usou Cura em Bloco: '
                  f'{alvo.nome} recuperou {recuperado} de vida!')

    def monkey_patch(self, alvos):
        # Reduz em 6 a defesa de todos os inimigos por 3 turnos de cada um
        registrar(f'{self.nome} usou Monkey Patch! Defesa dos inimigos -6')

        for inimigo in alvos:
            inimigo.aplicar_efeito('monkey_patch', 'Monkey Patch', 'defesa', -6, 3)


# =====================================================================
# PERSONAGENS
# =====================================================================
# A ordem importa: é a ordem dos 8 espaços da tela de seleção. Os 4 primeiros
# já vêm liberados; os outros são liberados ao zerar o jogo (ver progresso.py).
todos_personagens = [
    Guerreiro(),
    Mago(),
    Ladino(),
    Paladino(),
    Engenheiro(),
    Lanceiro(),
    Arqueiro(),
    Hexxer(),
]
