from .combatentes import Combatente, causar_dano
from .registro import registrar


class Personagem(Combatente):
    """Base dos personagens jogáveis.

    Cada personagem (subclasse) define as PRÓPRIAS habilidades:
    o dicionário HABILIDADES (chave -> nome, custo de mana, tipo de alvo)
    um método com o mesmo nome da chave, que faz o efeito
    e também CLASSE (nome da classe) e SPRITE (imagem em assets/sprites/personagens).

    Tipos de alvo da habilidade (o que o método recebe):
      'inimigo' -> (alvo)     um inimigo escolhido pelo jogador
      'todos'   -> (alvos)    todos os inimigos vivos
      'nenhum'  -> ()         age só no próprio personagem
      'time'    -> (aliados)  todos os aliados vivos (inclui ele mesmo)
      'aliado'  -> (alvo)     um aliado vivo e ferido, escolhido pelo jogador
      'protegido' -> (alvo)   qualquer aliado vivo (ferido ou não), escolhido
      'mortos'  -> (mortos)   todos os aliados derrotados
      'morto'   -> (alvo)     um aliado derrotado, escolhido pelo jogador
    """

    HABILIDADES = {}
    CLASSE = ''
    SPRITE = ''

    # balanceamento: recuperação
    MANA_POR_TURNO = 2        # mana recuperada no início de cada turno
    DESCANSO_VIDA = 0.20      # fração da vida máx. recuperada entre fases
    DESCANSO_MANA = 0.35      # fração da mana máx. recuperada entre fases
    DESCANSO_REVIVER = 0      # derrotados voltam com essa fração na fase seguinte

    def __init__(self, nome, vida_maxima, vida, ataque, defesa, velocidade,
                 mana_maxima):
        super().__init__(nome, vida_maxima, vida, ataque, defesa, velocidade)
        self.mana_maxima = mana_maxima
        self.mana = mana_maxima
        self.invocacao = None

    def inicio_do_turno(self):
        super().inicio_do_turno()
        if self.vida > 0:
            self.mana = min(self.mana_maxima, self.mana + self.MANA_POR_TURNO)

    def descansar(self):
        """Chamado entre uma fase e a outra: recupera parte da vida e da mana.
        Quem foi derrotado volta com um pouco de vida."""
        if self.vida <= 0:
            if self.DESCANSO_REVIVER > 0:
                self.reviver(self.DESCANSO_REVIVER)
            else:
                return
        else:
            self.vida = min(self.vida_maxima,
                            self.vida + int(self.vida_maxima * self.DESCANSO_VIDA))
        self.mana = min(self.mana_maxima,
                        self.mana + int(self.mana_maxima * self.DESCANSO_MANA))

    # ---------- mana e habilidades ----------
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
        assim a Luta sabe se o turno deve passar."""
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

        if tipo == 'protegido' and alvo not in aliados_vivos:
            return False

        if tipo == 'mortos' and not mortos:
            registrar('Nenhum aliado está derrotado!')
            return False

        if tipo == 'morto' and alvo not in mortos:
            if alvo is not None:
                registrar(f'{alvo.nome} não está derrotado!')
            return False

        if not self.tem_mana(chave):
            registrar(
                f'{self.nome} está sem mana para {info["nome"]} '
                f'(custo {info["custo"]})!'
            )
            return False

        self.mana -= info['custo']
        efeito = getattr(self, chave)

        if tipo in ('inimigo', 'aliado', 'protegido', 'morto'):
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

    # utilitários compartilhados
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


# PYTHON - Guerreiro
class Guerreiro(Personagem):
    CLASSE = 'Guerreiro'
    SPRITE = 'gpython.png'
    HABILIDADES = {
        'picada_mortal': {'nome': 'Picada Mortal', 'custo': 10, 'alvo': 'inimigo'},
        'salto_de_bits': {'nome': 'Salto de Bits', 'custo': 20, 'alvo': 'inimigo'},
        'provocacao_global': {'nome': 'Provocação Global', 'custo': 10, 'alvo': 'nenhum'},
    }

    def __init__(self):
        super().__init__('Python', 100, 100, 20, 8, 3, mana_maxima=40)

    def provocacao_global(self):
        # Até 2 turnos do Guerreiro: todos os inimigos só atacam ele,
        # e ele ganha +5 de defesa para tankar
        rotulo = 'Provocação Global'
        self.aplicar_efeito('provocacao_global', rotulo, 'provocacao', 1, 2)
        self.aplicar_efeito('provocacao_global_def', rotulo, 'defesa', 5, 2)
        registrar(f'{self.nome} usou Provocação Global! '
                  f'Os inimigos só atacam ele. Defesa +5')

    def picada_mortal(self, alvo):
        # Dano fixo: ignora completamente a defesa
        dano = 20
        causar_dano(
            alvo, dano,
            f'{self.nome} usou Picada Mortal: {dano} de dano em {alvo.nome}!'
        )

    def salto_de_bits(self, alvo):
        # Ignora 50% da defesa do inimigo
        dano = max(1, 35 - alvo.defesa // 2)
        causar_dano(
            alvo, dano,
            f'{self.nome} usou Salto de Bits: {dano} de dano em {alvo.nome}!'
        )


# JAVA - Mago
class Mago(Personagem):
    CLASSE = 'Mago'
    SPRITE = 'mjava.png'
    HABILIDADES = {
        'lancar_excecao': {'nome': 'Lançar Exceção', 'custo': 10, 'alvo': 'inimigo'},
        'cadeia_de_codigos': {'nome': 'Cadeia de Códigos', 'custo': 15, 'alvo': 'todos'},
        'meteoro_de_variavel': {'nome': 'Meteoro de Variável', 'custo': 30, 'alvo': 'inimigo'},
    }

    def __init__(self):
        super().__init__('Java', 80, 80, 20, 7, 2, mana_maxima=60)

    def lancar_excecao(self, alvo):
        # Dano singular simples (a defesa do alvo conta normalmente)
        dano = max(1, 32 - alvo.defesa)
        causar_dano(
            alvo, dano,
            f'{self.nome} usou Lançar Exceção: {dano} de dano em {alvo.nome}!'
        )

    def cadeia_de_codigos(self, alvos):
        registrar(f'{self.nome} lançou Cadeia de Códigos!')

        for inimigo in alvos:
            dano = max(1, 25 - inimigo.defesa)
            causar_dano(
                inimigo, dano, f'{inimigo.nome} recebeu {dano} de dano!'
            )

    def meteoro_de_variavel(self, alvo):
        # Dano fixo: ignora completamente a defesa
        dano = 45
        causar_dano(
            alvo, dano,
            f'{self.nome} lançou Meteoro de Variável: '
            f'{dano} de dano (ignora defesa) em {alvo.nome}!'
        )

# JAVASCRIPT - Ladino
class Ladino(Personagem):
    CLASSE = 'Ladino'
    SPRITE = 'Ljavascript.png'
    HABILIDADES = {
        'investida_assincrona': {'nome': 'Investida Assíncrona', 'custo': 10, 'alvo': 'inimigo'},
        'rajada_de_scripts': {'nome': 'Rajada de Scripts', 'custo': 20, 'alvo': 'inimigo'},
        'promessa_pendente': {'nome': 'Promessa Pendente', 'custo': 15, 'alvo': 'nenhum'},
    }
    BONUS_PREPARADO = 1.5  # dano do próximo ataque/habilidade depois da Promessa

    def __init__(self):
        super().__init__('JavaScript', 90, 90, 25, 6, 5, mana_maxima=40)
        self.golpe_preparado = False

    # Promessa Pendente
    def promessa_pendente(self):
        # Fica intangível por 2 turnos (ou até atacar) e prepara um golpe
        # mais forte para o próximo ataque/habilidade
        self.aplicar_efeito('promessa_pendente', 'Intangibilidade',
                            'intangivel', 1, 2)
        self.golpe_preparado = True
        registrar(f'{self.nome} usou Promessa Pendente! Ficou intangível '
                  f'e o próximo golpe causa +50% de dano')

    def _poder(self, base):
        """Dano base, já com o bônus do golpe preparado (se houver)."""
        if self.golpe_preparado:
            return int(base * self.BONUS_PREPARADO)
        return base

    def _resolver_promessa(self):
        """Depois de atacar: gasta o bônus e sai da intangibilidade."""
        self.golpe_preparado = False
        if self.intangivel > 0:
            self.remover_efeito('promessa_pendente')
            registrar(f'{self.nome} atacou e deixou de ser intangível!')

    def atacar(self, alvo):
        ataque_normal = self.ataque
        self.ataque = self._poder(self.ataque)
        try:
            dano = super().atacar(alvo)
        finally:
            self.ataque = ataque_normal
        if dano:
            self._resolver_promessa()
        return dano

    def usar_habilidade(self, chave, alvo, inimigos, aliados=()):
        usou = super().usar_habilidade(chave, alvo, inimigos, aliados)
        if usou and chave != 'promessa_pendente':
            self._resolver_promessa()
        return usou

    def limpar_efeitos(self):
        super().limpar_efeitos()
        self.golpe_preparado = False

    # golpes multiplos
    def investida_assincrona(self, alvo):
        # Ignora 25% da defesa do inimigo
        dano = max(1, self._poder(30) - int(alvo.defesa * 0.75))
        causar_dano(
            alvo, dano,
            f'{self.nome} usou Investida Assíncrona: {dano} de dano em {alvo.nome}!'
        )

    def rajada_de_scripts(self, alvo):
        registrar(f'{self.nome} usou Rajada de Scripts!')

        for golpe in range(1, 4):
            if alvo.vida <= 0:
                break

            dano = max(1, self._poder(15) - alvo.defesa)
            causar_dano(
                alvo, dano, f'Golpe {golpe}: {dano} de dano em {alvo.nome}!'
            )

# C# - Paladino
class Paladino(Personagem):
    CLASSE = 'Paladino'
    SPRITE = 'Cpaladino.png'
    HABILIDADES = {
        'escudo_de_compilacao': {'nome': 'Escudo de Compilação', 'custo': 10, 'alvo': 'protegido'},
        'codigo_divino': {'nome': 'Código Divino', 'custo': 30, 'alvo': 'inimigo'},
        'restaurar_instancia': {'nome': 'Restaurar Instância', 'custo': 35, 'alvo': 'morto'},
    }
    CURA_ESCUDO = 15  # cura leve que o Escudo de Compilação dá junto

    def __init__(self):
        super().__init__('C#', 140, 140, 18, 10, 1, mana_maxima=50)

    def restaurar_instancia(self, alvo):
        # Revive 1 aliado derrotado com 50% da vida
        alvo.reviver(0.50)
        registrar(f'{self.nome} usou Restaurar Instância: '
                  f'{alvo.nome} voltou com {alvo.vida} de vida!')

    def escudo_de_compilacao(self, alvo):
        # Em qualquer aliado vivo (ou nele mesmo): +20 de defesa até o
        # próximo turno do alvo e uma cura leve
        alvo.aplicar_efeito('escudo_de_compilacao', 'Escudo de Compilação',
                            'defesa', 20, 1)
        curado = min(self.CURA_ESCUDO, alvo.vida_maxima - alvo.vida)
        alvo.vida += curado
        quem = 'em si mesmo' if alvo is self else f'em {alvo.nome}'
        cura = f', +{curado} de vida' if curado else ''
        registrar(f'{self.nome} usou Escudo de Compilação {quem}! '
                  f'Defesa +20{cura}')

    def codigo_divino(self, alvo):
        # Ignora 50% da defesa do alvo
        dano = max(1, 40 - alvo.defesa // 2)
        causar_dano(
            alvo, dano,
            f'{self.nome} usou Código Divino: {dano} de dano em {alvo.nome}!'
        )

# C++ - Engenheiro  (desbloqueado ao zerar o jogo 1 vez)
class Torreta(Combatente):
    """Invocada pelo Engenheiro. Só ataca (sozinha, um inimigo aleatório) e
    recebe dano: não usa habilidades, não defende e não recebe poções, curas
    nem escudos do time. Some no fim da luta."""
    SPRITE = 'torreta.png'

    def __init__(self):
        super().__init__('Torreta', 55, 55, 18, 6, 2)


class Engenheiro(Personagem):
    CLASSE = 'Engenheiro'
    SPRITE = 'Cengenheiro.png'
    HABILIDADES = {
        'barreira_de_ponteiros': {'nome': 'Barreira de Ponteiros', 'custo': 25, 'alvo': 'time'},
        'falha_de_segmentacao': {'nome': 'Falha de Segmentação', 'custo': 20, 'alvo': 'inimigo'},
        'invocar_torreta': {'nome': 'Invocar Torreta', 'custo': 30, 'alvo': 'nenhum'},
    }

    def __init__(self):
        super().__init__('C++', 110, 110, 14, 9, 2, mana_maxima=55)

    def usar_habilidade(self, chave, alvo, inimigos, aliados=()):
        # Só uma torreta por vez: enquanto ela estiver de pé, não gasta mana
        if (chave == 'invocar_torreta' and self.invocacao
                and self.invocacao.vida > 0):
            registrar('A Torreta já está em campo!')
            return False
        return super().usar_habilidade(chave, alvo, inimigos, aliados)

    def invocar_torreta(self):
        # Se a torreta já foi destruída nesta luta, ela volta com vida cheia
        if self.invocacao is None:
            self.invocacao = Torreta()
        else:
            self.invocacao.reviver(1.0)
        registrar(f'{self.nome} invocou uma Torreta!')

    def barreira_de_ponteiros(self, aliados):
        # Escudo no time inteiro: +12 de defesa por 2 turnos de cada um
        registrar(f'{self.nome} ergueu a Barreira de Ponteiros! Defesa do time +12')

        for aliado in aliados:
            aliado.aplicar_efeito('barreira_de_ponteiros', 'Barreira de Ponteiros',
                                  'defesa', 12, 2)

    def falha_de_segmentacao(self, alvo):
        # Dano singular (a defesa do alvo conta normalmente)
        dano = max(1, 36 - alvo.defesa)
        causar_dano(
            alvo, dano,
            f'{self.nome} usou Falha de Segmentação: {dano} de dano em {alvo.nome}!'
        )

# DELPHI - Lanceiro  (desbloqueado ao zerar o jogo 2 vezes)
class Lanceiro(Personagem):
    CLASSE = 'Lanceiro'
    SPRITE = 'Dlanceiro.png'
    HABILIDADES = {
        'estocada_em_cascata': {'nome': 'Estocada em Cascata', 'custo': 25, 'alvo': 'inimigo'},
        'giro_de_unidade': {'nome': 'Giro de Unidade', 'custo': 20, 'alvo': 'todos'},
        'lanca_perfurante': {'nome': 'Lança Perfurante', 'custo': 15, 'alvo': 'inimigo'},
    }

    def __init__(self):
        super().__init__('Delphi', 110, 110, 18, 8, 3, mana_maxima=45)

    def lanca_perfurante(self, alvo):
        # Dano singular e, se o alvo sobreviver, -6 de defesa por 3 turnos dele
        dano = max(1, 24 - alvo.defesa)
        causar_dano(
            alvo, dano,
            f'{self.nome} usou Lança Perfurante: {dano} de dano em {alvo.nome}!'
        )
        if alvo.vida > 0:
            alvo.aplicar_efeito('lanca_perfurante', 'Armadura Perfurada',
                                'defesa', -6, 3)
            registrar(f'Defesa de {alvo.nome} -6!')

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
            causar_dano(
                inimigo, dano, f'{inimigo.nome} recebeu {dano} de dano!'
            )

# PHP - Arqueiro  (desbloqueado ao zerar o jogo 3 vezes)
class Arqueiro(Personagem):
    CLASSE = 'Arqueiro'
    SPRITE = 'Parqueiro.png'
    HABILIDADES = {
        'chuva_de_requisicoes': {'nome': 'Chuva de Requisições', 'custo': 25, 'alvo': 'todos'},
        'injecao_de_sql': {'nome': 'Injeção de SQL', 'custo': 20, 'alvo': 'inimigo'},
        'flecha_depreciada': {'nome': 'Flecha Depreciada', 'custo': 20, 'alvo': 'inimigo'},
    }

    def __init__(self):
        super().__init__('PHP', 95, 95, 22, 6, 4, mana_maxima=50)

    def chuva_de_requisicoes(self, alvos):
        # Dano em área, 3 golpes em cada inimigo
        registrar(f'{self.nome} usou Chuva de Requisições! (3 golpes em cada)')

        for inimigo in alvos:
            total = self._golpes(inimigo, 3, 10)
            registrar(f'{inimigo.nome} recebeu {total} de dano!')
            self._anunciar_derrota(inimigo)

    def injecao_de_sql(self, alvo):
        # Dano singular fixo: ignora completamente a defesa
        dano = 30
        causar_dano(
            alvo, dano,
            f'{self.nome} usou Injeção de SQL: {dano} de dano (ignora defesa) em {alvo.nome}!'
        )

    def flecha_depreciada(self, alvo):
        # Dano singular e, se o alvo sobreviver, -5 de defesa e -6 de ataque
        # por 3 turnos dele
        dano = max(1, 26 - alvo.defesa)
        causar_dano(
            alvo, dano,
            f'{self.nome} usou Flecha Depreciada: {dano} de dano em {alvo.nome}!'
        )
        if alvo.vida > 0:
            rotulo = 'Flecha Depreciada'
            alvo.aplicar_efeito('flecha_depreciada_def', rotulo, 'defesa', -5, 3)
            alvo.aplicar_efeito('flecha_depreciada_atq', rotulo, 'ataque', -6, 3)
            registrar(f'{alvo.nome} ficou enfraquecido: Defesa -5, Ataque -6!')

# RUBY - Hexxer  (desbloqueado ao zerar o jogo 4 vezes)
class Hexxer(Personagem):
    CLASSE = 'Hexxer'
    SPRITE = 'Rhexxer.png'
    HABILIDADES = {
        'reiniciar_processo': {'nome': 'Reiniciar Processo', 'custo': 40, 'alvo': 'mortos'},
        'cura_em_bloco': {'nome': 'Cura em Bloco', 'custo': 15, 'alvo': 'aliado'},
        'monkey_patch': {'nome': 'Monkey Patch', 'custo': 20, 'alvo': 'todos'},
    }

    def __init__(self):
        super().__init__('Ruby', 85, 85, 18, 6, 2, mana_maxima=70)

    def reiniciar_processo(self, mortos):
        # Revive todos os aliados derrotados com 30% da vida
        registrar(f'{self.nome} usou Reiniciar Processo!')

        for aliado in mortos:
            aliado.reviver(0.30)
            registrar(f'{aliado.nome} voltou com {aliado.vida} de vida!')

    def cura_em_bloco(self, alvo):
        recuperado = min(50, alvo.vida_maxima - alvo.vida)
        alvo.vida += recuperado
        registrar(f'{self.nome} usou Cura em Bloco: '
                  f'{alvo.nome} recuperou {recuperado} de vida!')

    def monkey_patch(self, alvos):
        # Reduz em 8 a defesa de todos os inimigos por 3 turnos de cada um
        registrar(f'{self.nome} usou Monkey Patch! Defesa dos inimigos -8')

        for inimigo in alvos:
            inimigo.aplicar_efeito('monkey_patch', 'Monkey Patch', 'defesa', -8, 3)

# PERSONAGENS
# A ordem importa: é a ordem dos 8 espaços da tela de seleção. Os 4 primeiros
# já vêm liberados; os outros são liberados ao zerar o jogo em progresso.py.
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
