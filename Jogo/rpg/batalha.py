import pygame

from .telas import LARGURA, ALTURA, SPRITES, carregar
from .luta import Luta
from .inimigos import criar_inimigo
from . import itens
from .registro import mensagens, limpar, registrar

# Cada item é uma luta; ao vencer, passa para a próxima.
# Use as chaves do dicionário INIMIGOS (inimigos.py).
FASES = [
    ['slime', 'inseto'],
    ['aranha', 'goblin'],
    ['golem'],
    ['virus', 'doppelganger'],
    ['dragao'],
    ['compilador'],
    ['bug_original'],
]

SPRITES_PERSONAGENS = {
    'Python': 'gpython.png',
    'Java': 'mjava.png',
    'JavaScript': 'Ljavascript.png',
    'C#': 'Cpaladino.png',
}

# Botões desenhados em batalha.png (ajuste se o fundo mudar)
BOTOES_ACAO = {
    'atacar': pygame.Rect(432, 550, 198, 52),
    'defender': pygame.Rect(650, 550, 198, 52),
    'habilidades': pygame.Rect(432, 622, 198, 52),
    'itens': pygame.Rect(650, 622, 198, 52),
}
CAIXA_MENU = pygame.Rect(404, 529, 472, 166)
PAINEL_LOG = pygame.Rect(300, 6, 640, 140)           # tamanho de mensagens.png
AREA_TEXTO = pygame.Rect(334, 44, 572, 64)           # parte de dentro da moldura (3 linhas)

# Quadro de habilidades (quadro_habilidades.png): aparece logo ACIMA da caixa
# de menu, com um botão para cada habilidade e um VOLTAR no fim.
ALTURA_QUADRO = 370
# parte de dentro da moldura, em fração do quadro: (esquerda, cima, direita, baixo)
INTERIOR_QUADRO = (0.12, 0.09, 0.88, 0.92)
TAM_BOTAO_HAB = (172, 54)      # tamanho dos botões dentro do quadro
ALTURA_BOTAO_ITEM = 38         # botões das poções são mais baixos (cabem 6 + VOLTAR)

TAM_PERSONAGEM = 96
TAM_INIMIGO = 120  # só para o placeholder (usado se o sprite do inimigo não existir)

# ---------- sprites dos inimigos ----------
# Procurados em assets/sprites/inimigos/ e em assets/sprites/.
# chave do inimigo (INIMIGOS em inimigos.py) -> nome do arquivo
ARQUIVOS_INIMIGOS = {
    'slime': 'slime.png',
    'inseto': 'inseto.png',
    'aranha': 'aranha.png',
    'goblin': 'goblin.png',
    'golem': 'golem.png',
    'doppelganger': 'plagiador.png',
    'virus': 'virus.png',
    'dragao': 'dragao.png',
    'compilador': 'compilador.png',
    'bug_original': 'bug_original.png',
}

# Altura (em pixels NA TELA) de cada inimigo; a largura acompanha o sprite.
# Os chefes ficam maiores que os inimigos comuns.
ALTURA_INIMIGO = {
    'slime': 76, 'goblin': 82, 'inseto': 72, 'aranha': 96, 'doppelganger': 90,
    'golem': 128, 'virus': 146, 'dragao': 226, 'compilador': 218,
    'bug_original': 256,
}
ALTURA_PADRAO_INIMIGO = 120

# Se preferir um aumento fixo e inteiro (pixel-art sempre nítida), coloque
# aqui um número (ex.: 3): todo sprite fica "tamanho do arquivo x 3" e a
# tabela de alturas acima é ignorada.
ESCALA_INIMIGOS = None

# Posição dos inimigos: "chão" (onde ficam os pés) e centro de cada coluna.
CHAO_INIMIGOS = 500
CENTROS_INIMIGOS = {1: [1010], 2: [1110, 880]}

# Formação do grupo: 2 linhas x 2 colunas.
# A linha de cima (1º e 2º escolhidos) fica NA FRENTE (mais perto dos
# inimigos); a de baixo fica atrás, recuada para a esquerda.
# DESLOC_TRAS = 0 alinha tudo em uma grade reta.
LINHAS_Y = (200, 400)   # y do sprite de cada linha (cabem nome + vida + mana)
X_FRENTE = 190          # x do 1º personagem da linha da frente
ESPACO_X = 130          # distância horizontal entre os dois da linha
DESLOC_TRAS = 80        # quanto a linha de trás recua para a esquerda

def nove_fatias(img, largura, altura, borda):
    """Estica uma moldura para qualquer tamanho mantendo os cantos intactos."""
    iw, ih = img.get_size()
    b = borda
    s = pygame.Surface((largura, altura), pygame.SRCALPHA)

    for sx, sy, dx, dy in [
        (0, 0, 0, 0), (iw - b, 0, largura - b, 0),
        (0, ih - b, 0, altura - b), (iw - b, ih - b, largura - b, altura - b),
    ]:
        s.blit(img, (dx, dy), (sx, sy, b, b))

    horiz = largura - 2 * b
    vert = altura - 2 * b
    s.blit(pygame.transform.scale(img.subsurface((b, 0, iw - 2 * b, b)), (horiz, b)), (b, 0))
    s.blit(pygame.transform.scale(img.subsurface((b, ih - b, iw - 2 * b, b)), (horiz, b)), (b, altura - b))
    s.blit(pygame.transform.scale(img.subsurface((0, b, b, ih - 2 * b)), (b, vert)), (0, b))
    s.blit(pygame.transform.scale(img.subsurface((iw - b, b, b, ih - 2 * b)), (b, vert)), (largura - b, b))
    return s


fundo = pygame.transform.scale(carregar('batalha.png').convert(), (LARGURA, ALTURA))
img_mensagens = carregar('mensagens.png').convert_alpha()

# contorno.png tem 4 px de borda; esticado para a largura do sprite.
# A mesma moldura é usada nas barras de vida e de mana.
BORDA_BARRA = 4
ALTURA_BARRA = 22
moldura_barra = nove_fatias(
    carregar('contorno.png').convert_alpha(),
    TAM_PERSONAGEM, ALTURA_BARRA, BORDA_BARRA
)
fonte_nome = pygame.font.Font(None, 24)
fonte_hp = pygame.font.Font(None, 18)
fonte_log = pygame.font.Font(None, 22)
fonte_info = pygame.font.Font(None, 34)
fonte_grande = pygame.font.Font(None, 120)


def escurecer(superficie):
    s = superficie.copy()
    s.fill((90, 90, 90, 255), special_flags=pygame.BLEND_RGBA_MULT)
    return s


def carregar_sprite(arquivo, tamanho):
    img = carregar(arquivo).convert_alpha()
    return pygame.transform.scale(img, (tamanho, tamanho))


_cache_inimigos = {}


def achar_arquivo_inimigo(chave):
    nome = ARQUIVOS_INIMIGOS.get(chave, f'{chave}.png')
    for pasta in (SPRITES / 'inimigos', SPRITES):
        if (pasta / nome).exists():
            return pasta / nome
    return None


def imagem_inimigo(chave):
    """(imagem, imagem escurecida) do inimigo, já no tamanho de tela."""
    if chave not in _cache_inimigos:
        caminho = achar_arquivo_inimigo(chave)

        if caminho:
            img = pygame.image.load(str(caminho)).convert_alpha()
            w, h = img.get_size()
            if ESCALA_INIMIGOS:
                fator = ESCALA_INIMIGOS
            else:
                fator = ALTURA_INIMIGO.get(chave, ALTURA_PADRAO_INIMIGO) / h
            img = pygame.transform.scale(
                img, (max(1, round(w * fator)), max(1, round(h * fator)))
            )
        else:
            print(f'[aviso] sprite do inimigo "{chave}" não encontrado; usando placeholder')
            img = carregar_sprite('placeholder.png', TAM_INIMIGO)

        _cache_inimigos[chave] = (img, escurecer(img))

    return _cache_inimigos[chave]


botao_vazio = pygame.transform.scale(
    carregar('botao_habilidade.png').convert_alpha(), TAM_BOTAO_HAB
)
botao_vazio_apagado = escurecer(botao_vazio)


def recortar_linhas(img, trechos):
    """Monta uma imagem mais baixa juntando só alguns trechos de linhas."""
    largura = img.get_width()
    altura = sum(fim - ini for ini, fim in trechos)
    novo = pygame.Surface((largura, altura), pygame.SRCALPHA)
    y = 0
    for ini, fim in trechos:
        novo.blit(img, (0, y), (0, ini, largura, fim - ini))
        y += fim - ini
    return novo


# 54 -> 38 px: tira 8 linhas da faixa azul-esverdeada e 8 da azul-escura
# (faixas de cor constante), então o botão não fica distorcido.
botao_item = recortar_linhas(botao_vazio, [(0, 15), (23, 30), (38, 54)])
botao_item_apagado = escurecer(botao_item)


def carregar_quadro():
    caminho = SPRITES / 'quadro_habilidades.png'
    if caminho.exists():
        img = pygame.image.load(str(caminho)).convert_alpha()
        w, h = img.get_size()
        return pygame.transform.scale(
            img, (round(w * ALTURA_QUADRO / h), ALTURA_QUADRO)
        )

    print('[aviso] quadro_habilidades.png não encontrado; usando um quadro simples')
    img = pygame.Surface((247, ALTURA_QUADRO), pygame.SRCALPHA)
    img.fill((18, 30, 54, 255))
    pygame.draw.rect(img, (120, 140, 180), img.get_rect(), 6)
    return img


quadro_habilidades = carregar_quadro()
RECT_QUADRO = quadro_habilidades.get_rect(
    midbottom=(CAIXA_MENU.centerx, CAIXA_MENU.top - 2)
)

# ---------- texto dos botões ----------
# Se existir assets/fonts/pixel.ttf (uma fonte pixel-art), ela é usada; senão,
# a fonte padrão do pygame (suavizada, bem mais fácil de ler em tamanho pequeno).
_ttf_pixel = SPRITES.parent / 'fonts' / 'pixel.ttf'
_arquivo_fonte = str(_ttf_pixel) if _ttf_pixel.exists() else None
SUAVIZAR_TEXTO = _arquivo_fonte is None   # fonte pixel-art fica melhor SEM suavização
_TAMANHOS_FONTE = (28, 26, 24, 22, 20, 18, 16, 15, 14) if _arquivo_fonte is None \
    else (24, 20, 16, 14, 12, 10, 8)
FONTES_BOTAO = {tam: pygame.font.Font(_arquivo_fonte, tam) for tam in _TAMANHOS_FONTE}
_cache_texto = {}


def _quebrar_em_duas(conteudo, fonte):
    """Divide o texto em 2 linhas o mais equilibradas possível (ou None)."""
    palavras = conteudo.split()
    melhor = None
    for k in range(1, len(palavras)):
        linhas = [' '.join(palavras[:k]), ' '.join(palavras[k:])]
        pior = max(fonte.size(l)[0] for l in linhas)
        if melhor is None or pior < melhor[0]:
            melhor = (pior, linhas)
    return melhor[1] if melhor else None


def texto_botao(conteudo, cor, largura_max, altura_max=34, contorno=(35, 12, 0)):
    """Texto legível para botões: usa o MAIOR tamanho que couber, em 1 linha
    ou, se for longo, quebrado em 2 linhas. Tem contorno escuro."""
    chave = (conteudo, cor, largura_max, altura_max)
    if chave in _cache_texto:
        return _cache_texto[chave]

    escolhido = None
    for fonte in FONTES_BOTAO.values():  # do maior para o menor
        passo = fonte.get_linesize()
        for linhas in ([conteudo], _quebrar_em_duas(conteudo, fonte)):
            if not linhas:
                continue
            largura = max(fonte.size(l)[0] for l in linhas) + 2
            altura = passo * len(linhas) + 2
            if largura <= largura_max and altura <= altura_max:
                escolhido = (fonte, linhas)
                break
        if escolhido:
            break

    if escolhido is None:  # nem o menor coube: usa o menor e encolhe a largura
        fonte = list(FONTES_BOTAO.values())[-1]
        escolhido = (fonte, [conteudo])

    fonte, linhas = escolhido
    passo = fonte.get_linesize()
    largura = max(fonte.size(l)[0] for l in linhas) + 2
    img = pygame.Surface((largura, passo * len(linhas) + 2), pygame.SRCALPHA)

    for n, linha in enumerate(linhas):
        base = fonte.render(linha, SUAVIZAR_TEXTO, cor)
        borda = fonte.render(linha, SUAVIZAR_TEXTO, contorno)
        x = (largura - base.get_width()) // 2   # linhas centralizadas
        y = n * passo
        for dx in (0, 1, 2):
            for dy in (0, 1, 2):
                if (dx, dy) != (1, 1):
                    img.blit(borda, (x + dx, y + dy))
        img.blit(base, (x + 1, y + 1))

    if img.get_width() > largura_max:
        img = pygame.transform.smoothscale(img, (largura_max, img.get_height()))

    _cache_texto[chave] = img
    return img


# Se existir assets/sprites/habilidades/<chave_da_habilidade>.png (por exemplo
# picada_mortal.png), essa imagem é usada no lugar do botão gerado pelo código.
_cache_botoes = {}


def imagem_botao_habilidade(chave, tem_mana):
    item = (chave, tem_mana)
    if item not in _cache_botoes:
        img = None
        caminho = SPRITES / 'habilidades' / f'{chave}.png'
        if caminho.exists():
            img = pygame.transform.scale(
                pygame.image.load(str(caminho)).convert_alpha(), TAM_BOTAO_HAB
            )
            if not tem_mana:
                img = escurecer(img)
        _cache_botoes[item] = img
    return _cache_botoes[item]


def texto(tela, conteudo, pos, fonte, cor=(255, 255, 255), centro=False):
    sombra = fonte.render(conteudo, True, (0, 0, 0))
    img = fonte.render(conteudo, True, cor)
    rect = img.get_rect(center=pos) if centro else img.get_rect(topleft=pos)
    tela.blit(sombra, rect.move(2, 2))
    tela.blit(img, rect)


def _desenhar_barra(tela, x, y, largura, valor, maximo, cor, cor_fundo, moldura):
    proporcao = max(0, valor) / maximo if maximo else 0

    if moldura:
        # Preenchimento dentro da moldura (contorno.png) e moldura por cima
        ix, iy = x + BORDA_BARRA, y + BORDA_BARRA
        iw = largura - 2 * BORDA_BARRA
        ih = moldura.get_height() - 2 * BORDA_BARRA
        pygame.draw.rect(tela, cor_fundo, (ix, iy, iw, ih))
        pygame.draw.rect(tela, cor, (ix, iy, int(iw * proporcao), ih))
        tela.blit(moldura, (x, y))
        centro = (x + largura // 2, y + moldura.get_height() // 2)
    else:
        pygame.draw.rect(tela, cor_fundo, (x, y, largura, 14))
        pygame.draw.rect(tela, cor, (x, y, int(largura * proporcao), 14))
        pygame.draw.rect(tela, (0, 0, 0), (x, y, largura, 14), 2)
        centro = (x + largura // 2, y + 7)

    numeros = f'{valor}/{maximo}'
    info = fonte_hp.render(numeros, True, (255, 255, 255))
    sombra = fonte_hp.render(numeros, True, (0, 0, 0))
    tela.blit(sombra, sombra.get_rect(center=(centro[0] + 1, centro[1] + 1)))
    tela.blit(info, info.get_rect(center=centro))


def barra_vida(tela, x, y, largura, combatente, moldura=None):
    proporcao = max(0, combatente.vida) / combatente.vida_maxima
    if proporcao > 0.5:
        cor = (60, 200, 70)
    elif proporcao > 0.25:
        cor = (230, 200, 40)
    else:
        cor = (220, 50, 40)

    _desenhar_barra(tela, x, y, largura, combatente.vida,
                    combatente.vida_maxima, cor, (60, 15, 15), moldura)


def barra_mana(tela, x, y, largura, personagem, moldura=None):
    _desenhar_barra(tela, x, y, largura, personagem.mana,
                    personagem.mana_maxima, (60, 130, 240), (12, 20, 60), moldura)


class Batalha:
    def __init__(self, grupo_jogador):
        self.grupo = grupo_jogador
        self.fase = 0
        # 'acao' (menu), 'habilidades', 'itens', 'alvo' (escolhendo inimigo)
        # ou 'alvo_aliado' (escolhendo quem recebe a poção)
        self.modo = 'acao'
        self.habilidade_escolhida = None
        self.item_escolhido = None
        self.inventario = itens.inventario_inicial()  # poções do grupo (passa de fase)
        self.drops = {}
        self.drops_sorteados = False

        self.sprites = {}
        for p in self.grupo:
            img = carregar_sprite(SPRITES_PERSONAGENS[p.nome], TAM_PERSONAGEM)
            self.sprites[id(p)] = (img, escurecer(img))

        self.iniciar_fase()

    # ---------- fases ----------
    def iniciar_fase(self):
        for p in self.grupo:
            p.remover_defesa()
        limpar()

        self.inimigos = [criar_inimigo(chave) for chave in FASES[self.fase]]
        self.luta = Luta(self.grupo, list(self.inimigos))
        self.modo = 'acao'
        self.habilidade_escolhida = None
        self.item_escolhido = None
        self.drops = {}
        self.drops_sorteados = False
        registrar(f'Fase {self.fase + 1}/{len(FASES)}: inimigos à frente!')

    # ---------- posições ----------
    def rect_personagem(self, i):
        linha, coluna = divmod(i, 2)
        x = X_FRENTE - linha * DESLOC_TRAS + coluna * ESPACO_X
        return pygame.Rect(x, LINHAS_Y[linha], TAM_PERSONAGEM, TAM_PERSONAGEM)

    def rect_clique_personagem(self, i):
        """Sprite + nome + barras (área onde se clica para escolher o aliado)."""
        r = self.rect_personagem(i)
        return pygame.Rect(r.x, r.y, r.width, r.height + 2 * ALTURA_BARRA + 30)

    def rect_inimigo(self, i):
        """Retângulo do sprite do inimigo i (pés no chão, centrado na coluna)."""
        img = imagem_inimigo(self.inimigos[i].chave)[0]
        total = len(self.inimigos)

        if total in CENTROS_INIMIGOS:
            centro, fileira = CENTROS_INIMIGOS[total][i], 0
        else:  # mais inimigos: duas colunas, em várias fileiras
            centro, fileira = CENTROS_INIMIGOS[2][i % 2], i // 2

        return img.get_rect(midbottom=(centro, CHAO_INIMIGOS - fileira * 150))

    def botoes_quadro(self, atual):
        """Botões dentro do quadro (habilidades ou poções, conforme o modo):
        [(rect, 'habilidade' | 'item' | 'voltar', dados)]."""
        if self.modo == 'itens':
            entradas = [('item', chave) for chave in itens.POCOES]
            alt = ALTURA_BOTAO_ITEM
        else:
            entradas = [('habilidade', h) for h in atual.lista_habilidades()]
            alt = TAM_BOTAO_HAB[1]

        fx0, fy0, fx1, fy1 = INTERIOR_QUADRO
        q = RECT_QUADRO
        interior = pygame.Rect(
            q.x + round(q.width * fx0), q.y + round(q.height * fy0),
            round(q.width * (fx1 - fx0)), round(q.height * (fy1 - fy0)),
        )
        larg = TAM_BOTAO_HAB[0]
        x = interior.centerx - larg // 2

        # itens de cima para baixo; VOLTAR fixo no fim do quadro
        n = len(entradas) + 1
        espaco = min(14, max(4, (interior.height - n * alt) // (n + 1)))
        botoes = [
            (pygame.Rect(x, interior.y + espaco + i * (alt + espaco), larg, alt),
             tipo, dados)
            for i, (tipo, dados) in enumerate(entradas)
        ]
        botoes.append((
            pygame.Rect(x, interior.bottom - espaco - alt, larg, alt),
            'voltar', None
        ))
        return botoes

    def inimigo_na_posicao(self, pos):
        for i, inimigo in enumerate(self.inimigos):
            if (inimigo in self.luta.grupo_inimigos and inimigo.vida > 0
                    and self.rect_inimigo(i).collidepoint(pos)):
                return inimigo
        return None

    def vez_do_jogador(self):
        atual = self.luta.combatente_atual()
        return (
            not self.luta.resultado
            and atual in self.grupo
            and atual.vida > 0
        )

    # ---------- eventos ----------
    def voltar(self):
        """Botão direito / ESC: volta um passo no menu."""
        if self.modo == 'alvo' and self.habilidade_escolhida:
            self.modo = 'habilidades'
        elif self.modo == 'alvo_aliado':
            self.modo = 'itens'
        else:
            self.modo = 'acao'
        self.habilidade_escolhida = None
        self.item_escolhido = None

    def escolher_habilidade(self, atual, habilidade):
        chave, nome, custo, tipo_alvo = habilidade

        if not atual.tem_mana(chave):
            registrar(f'{atual.nome} está sem mana para {nome} (custo {custo})!')
            return

        if tipo_alvo == 'inimigo':
            self.habilidade_escolhida = chave
            self.modo = 'alvo'
        else:  # 'todos' ou 'nenhum': não precisa escolher alvo
            self.luta.executar_acao_jogador(chave)
            self.modo = 'acao'

    def escolher_item(self, chave):
        nome = itens.nome_pocao(chave)

        if self.inventario.get(chave, 0) <= 0:
            registrar(f'Você não tem mais {nome}!')
            return

        if not any(itens.pode_usar(chave, p)[0] for p in self.grupo):
            registrar(f'Ninguém precisa de {nome} agora!')
            return

        self.item_escolhido = chave
        self.modo = 'alvo_aliado'

    def evento(self, ev):
        """Retorna 'menu' quando a batalha termina e deve voltar ao menu."""
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            self.voltar()
            return None

        if ev.type != pygame.MOUSEBUTTONDOWN:
            return None

        # Botão direito volta um passo
        if ev.button == 3:
            self.voltar()
            return None

        if ev.button != 1:
            return None

        # Fim da luta: clique avança
        if self.luta.resultado:
            if self.luta.resultado == 'vitoria' and self.fase + 1 < len(FASES):
                self.fase += 1
                self.iniciar_fase()
                return None
            return 'menu'

        if not self.vez_do_jogador():
            return None

        atual = self.luta.combatente_atual()

        if self.modo in ('acao', 'habilidades', 'itens'):
            # Com um quadro aberto, os botões dele vêm primeiro
            if self.modo in ('habilidades', 'itens'):
                for rect, tipo, dados in self.botoes_quadro(atual):
                    if rect.collidepoint(ev.pos):
                        if tipo == 'voltar':
                            self.voltar()
                        elif tipo == 'item':
                            self.escolher_item(dados)
                        else:
                            self.escolher_habilidade(atual, dados)
                        return None

            # Os 4 botões de ação continuam valendo com o quadro aberto
            for nome, rect in BOTOES_ACAO.items():
                if rect.collidepoint(ev.pos):
                    self.clicar_acao(nome)
                    break

        elif self.modo == 'alvo':
            alvo = self.inimigo_na_posicao(ev.pos)
            if alvo:
                acao = self.habilidade_escolhida or 'atacar'
                self.luta.executar_acao_jogador(acao, alvo)
                self.modo = 'acao'
                self.habilidade_escolhida = None
            elif not CAIXA_MENU.collidepoint(ev.pos):
                self.voltar()

        elif self.modo == 'alvo_aliado':
            for i, aliado in enumerate(self.grupo):
                if aliado.vida > 0 and self.rect_clique_personagem(i).collidepoint(ev.pos):
                    chave = self.item_escolhido
                    antes = self.inventario[chave]
                    self.luta.usar_pocao(chave, aliado, self.inventario)
                    if self.inventario[chave] < antes:  # foi usada: o turno passou
                        self.modo = 'acao'
                        self.item_escolhido = None
                    return None  # se não deu certo, continua escolhendo

            if not CAIXA_MENU.collidepoint(ev.pos):
                self.voltar()

        return None

    def clicar_acao(self, nome):
        self.habilidade_escolhida = None
        self.item_escolhido = None

        if nome == 'atacar':
            self.modo = 'alvo'
        elif nome == 'defender':
            self.luta.executar_acao_jogador('defender')
            self.modo = 'acao'
        elif nome == 'habilidades':
            # clicar de novo em Habilidades fecha o quadro
            self.modo = 'acao' if self.modo == 'habilidades' else 'habilidades'
        elif nome == 'itens':
            self.modo = 'acao' if self.modo == 'itens' else 'itens'

    # ---------- atualização ----------
    def atualizar(self):
        self.luta.atualizar()
        if not self.vez_do_jogador():
            self.modo = 'acao'
            self.habilidade_escolhida = None
            self.item_escolhido = None

        # Ao vencer, sorteia (uma única vez) as poções ganhas.
        # Depois da última luta não há prêmio: o jogo acabou.
        if self.luta.resultado == 'vitoria' and not self.drops_sorteados:
            self.drops_sorteados = True
            if self.fase + 1 < len(FASES):
                self.drops = itens.sortear_drops(self.fase)
                itens.ganhar(self.inventario, self.drops)

    # ---------- desenho ----------
    def desenhar(self, tela, mouse):
        tela.blit(fundo, (0, 0))
        atual = self.luta.combatente_atual()

        self.desenhar_inimigos(tela, mouse, atual)
        self.desenhar_personagens(tela, mouse, atual)
        self.desenhar_log(tela, atual)
        self.desenhar_menu(tela, mouse, atual)

        if self.luta.resultado:
            self.desenhar_fim(tela)

    def desenhar_personagens(self, tela, mouse, atual):
        for i, p in enumerate(self.grupo):
            rect = self.rect_personagem(i)
            normal, morto = self.sprites[id(p)]

            tela.blit(normal if p.vida > 0 else morto, rect)

            # Defendendo: contorno azul no sprite
            if p.defendendo and p.vida > 0:
                pygame.draw.rect(tela, (80, 160, 255), rect.inflate(6, 6), 3)

            # Nome logo abaixo do sprite, depois a barra de vida e a de mana
            texto(tela, p.nome, (rect.centerx, rect.bottom + 14),
                  fonte_nome, centro=True)
            y_vida = rect.bottom + 28
            barra_vida(tela, rect.x, y_vida, rect.width, p, moldura_barra)
            barra_mana(tela, rect.x, y_vida + ALTURA_BARRA + 2, rect.width,
                       p, moldura_barra)

            # Escolhendo quem recebe a poção: contorna quem pode usá-la
            if self.modo == 'alvo_aliado' and p.vida > 0 \
                    and itens.pode_usar(self.item_escolhido, p)[0]:
                sobre = self.rect_clique_personagem(i).collidepoint(mouse)
                cor = (80, 255, 120) if sobre else (255, 255, 255)
                pygame.draw.rect(tela, cor, rect.inflate(10, 10), 3)

            # Seta amarela sobre quem está na vez
            if p is atual and p.vida > 0:
                pygame.draw.polygon(tela, (255, 220, 40), [
                    (rect.centerx - 11, rect.y - 26),
                    (rect.centerx + 11, rect.y - 26),
                    (rect.centerx, rect.y - 7),
                ])

    def desenhar_inimigos(self, tela, mouse, atual):
        sobre = self.inimigo_na_posicao(mouse) if self.modo == 'alvo' else None

        for i, inimigo in enumerate(self.inimigos):
            if inimigo not in self.luta.grupo_inimigos:
                continue  # fugiu

            rect = self.rect_inimigo(i)
            vivo = inimigo.vida > 0
            normal, morto = imagem_inimigo(inimigo.chave)

            # Nome sobre a cabeça, sprite, barra de vida embaixo dos pés
            texto(tela, inimigo.nome + (' (DEF)' if inimigo.defendendo else ''),
                  (rect.centerx, rect.y - 14), fonte_nome, centro=True)
            tela.blit(normal if vivo else morto, rect)
            barra_vida(tela, rect.centerx - TAM_INIMIGO // 2, rect.bottom + 4,
                       TAM_INIMIGO, inimigo)

            if self.modo == 'alvo' and vivo:
                cor = (255, 70, 60) if inimigo is sobre else (255, 255, 255)
                pygame.draw.rect(tela, cor, rect.inflate(8, 8), 3)

            if inimigo is atual and vivo:
                cy = rect.centery
                pygame.draw.polygon(tela, (255, 220, 40), [
                    (rect.right + 24, cy - 11), (rect.right + 24, cy + 11),
                    (rect.right + 5, cy)
                ])

    def status(self, atual):
        """Linha de status mostrada no painel de mensagens."""
        if self.luta.resultado or not atual:
            return None
        if self.vez_do_jogador():
            if self.modo == 'alvo':
                if self.habilidade_escolhida:
                    nome = atual.HABILIDADES[self.habilidade_escolhida]['nome']
                    return f'{nome}: escolha o alvo (botão direito volta)', (255, 255, 255)
                return 'Escolha o alvo (botão direito cancela)', (255, 255, 255)
            if self.modo == 'habilidades':
                return 'Escolha uma habilidade (botão direito volta)', (255, 255, 255)
            if self.modo == 'itens':
                return 'Escolha uma poção (botão direito volta)', (255, 255, 255)
            if self.modo == 'alvo_aliado':
                nome = itens.nome_pocao(self.item_escolhido)
                return f'{nome}: escolha quem vai usar (botão direito volta)', (255, 255, 255)
            return f'Vez de {atual.nome}: escolha uma ação', (255, 220, 40)
        return f'Turno de {atual.nome}...', (170, 190, 220)

    def desenhar_log(self, tela, atual):
        tela.blit(img_mensagens, PAINEL_LOG)

        status = self.status(atual)
        if status:
            linhas = [(m, (235, 235, 235)) for m in mensagens[-2:]]
            linhas.append(status)
        else:
            linhas = [(m, (235, 235, 235)) for m in mensagens[-3:]]

        # Tudo que é escrito fica recortado dentro da moldura
        tela.set_clip(AREA_TEXTO)
        for n, (msg, cor) in enumerate(linhas):
            img = fonte_log.render(msg, True, cor)
            if img.get_width() > AREA_TEXTO.width:
                img = pygame.transform.smoothscale(
                    img, (AREA_TEXTO.width, img.get_height())
                )
            tela.blit(img, (AREA_TEXTO.x, AREA_TEXTO.y + n * 21))
        tela.set_clip(None)

    def desenhar_menu(self, tela, mouse, atual):
        if self.vez_do_jogador():
            if self.modo in ('acao', 'habilidades', 'itens'):
                for nome, rect in BOTOES_ACAO.items():
                    if rect.collidepoint(mouse):
                        pygame.draw.rect(tela, (255, 255, 255), rect, 3)

            if self.modo in ('habilidades', 'itens'):
                # botão "marcado" enquanto o quadro dele está aberto
                pygame.draw.rect(tela, (255, 220, 40), BOTOES_ACAO[self.modo], 3)
                self.desenhar_quadro(tela, mouse, atual)
        else:
            # Menu apagado durante o turno dos inimigos
            sombra = pygame.Surface(CAIXA_MENU.size, pygame.SRCALPHA)
            sombra.fill((0, 0, 0, 150))
            tela.blit(sombra, CAIXA_MENU)

    def desenhar_quadro(self, tela, mouse, atual):
        tela.blit(quadro_habilidades, RECT_QUADRO)

        for rect, tipo, dados in self.botoes_quadro(atual):
            baixo = rect.height == ALTURA_BOTAO_ITEM
            normal = botao_item if baixo else botao_vazio
            apagado = botao_item_apagado if baixo else botao_vazio_apagado
            centro_y = rect.centery - (2 if baixo else 3)
            alt_texto = rect.height - 12 if baixo else 34

            if tipo == 'voltar':
                tela.blit(normal, rect)
                img = texto_botao('VOLTAR', (255, 200, 50), rect.width - 24, alt_texto)
                tela.blit(img, img.get_rect(center=(rect.centerx, centro_y)))

            elif tipo == 'item':
                nome = itens.nome_pocao(dados)
                qtd = self.inventario.get(dados, 0)
                tem = qtd > 0
                tela.blit(normal if tem else apagado, rect)
                img = texto_botao(nome, (255, 200, 50) if tem else (150, 150, 150),
                                  118, alt_texto)
                tela.blit(img, img.get_rect(center=(rect.x + 70, centro_y)))
                img = texto_botao(f'x{qtd}', (120, 205, 255) if tem else (230, 90, 80),
                                  32, alt_texto)
                tela.blit(img, img.get_rect(center=(rect.x + 152, centro_y)))

            else:
                chave, nome, custo, _ = dados
                tem_mana = atual.tem_mana(chave)
                personalizada = imagem_botao_habilidade(chave, tem_mana)

                if personalizada:
                    tela.blit(personalizada, rect)
                else:
                    tela.blit(normal if tem_mana else apagado, rect)
                    cor_nome = (255, 200, 50) if tem_mana else (150, 150, 150)
                    cor_custo = (120, 205, 255) if tem_mana else (230, 90, 80)
                    # nome à esquerda, custo de mana à direita
                    img = texto_botao(nome, cor_nome, 118, alt_texto)
                    tela.blit(img, img.get_rect(center=(rect.x + 70, centro_y)))
                    img = texto_botao(str(custo), cor_custo, 32, 26)
                    tela.blit(img, img.get_rect(center=(rect.x + 152, centro_y)))

            if rect.collidepoint(mouse):
                pygame.draw.rect(tela, (255, 255, 255), rect, 3)

    def desenhar_fim(self, tela):
        escuro = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        escuro.fill((0, 0, 0, 170))
        tela.blit(escuro, (0, 0))
        meio = LARGURA // 2

        if self.luta.resultado == 'vitoria':
            ultima = self.fase + 1 >= len(FASES)
            titulo = 'VOCÊ VENCEU!' if ultima else 'VITÓRIA!'
            sub = 'Clique para voltar ao menu' if ultima else 'Clique para a próxima fase'
            texto(tela, titulo, (meio, 140), fonte_grande, (255, 220, 40), centro=True)

            if not ultima:
                y = 235
                if self.drops:
                    texto(tela, 'Você conseguiu:', (meio, y), fonte_info, centro=True)
                    for chave, qtd in self.drops.items():
                        y += 38
                        texto(tela, f'{qtd}x {itens.nome_pocao(chave)}', (meio, y),
                              fonte_info, (120, 230, 140), centro=True)
                else:
                    texto(tela, 'Nenhuma poção desta vez...', (meio, y),
                          fonte_info, (200, 200, 200), centro=True)

            # acima da caixa de menu do fundo (que começa em y = 529)
            texto(tela, sub, (meio, 390 if ultima else 505), fonte_info, centro=True)
        else:
            texto(tela, 'DERROTA...', (meio, 290), fonte_grande, (230, 70, 60), centro=True)
            texto(tela, 'Clique para voltar ao menu', (meio, 390), fonte_info, centro=True)
