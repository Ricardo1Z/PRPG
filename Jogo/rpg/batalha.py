import math

import pygame

from .telas import (LARGURA, ALTURA, INIMIGOS, PERSONAGENS, TELAS, INTERFACE,
                    carregar, cursor_vertical, Zoom, ampliar)
from . import fonte_pixel as fp
from .luta import Luta
from .inimigos import criar_inimigo
from . import itens, progresso
from .personagens import todos_personagens
from .registro import mensagens, limpar, registrar
from .musica import tocar_dano

# Cada item é uma luta; ao vencer, passa para a próxima.
# Use as chaves do dicionário INIMIGOS (inimigos.py).
FASES = [
    ['slime', 'inseto'],                       # 1
    ['slime', 'aranha'],                       # 2
    ['inseto', 'goblin'],                      # 3
    ['aranha', 'goblin', 'inseto'],            # 4
    ['dragao', 'goblin', 'slime'],             # 5  (chefe)
    ['inseto', 'aranha', 'goblin'],            # 6
    ['doppelganger', 'virus'],                 # 7
    ['golem', 'aranha', 'goblin'],             # 8
    ['virus', 'doppelganger', 'golem'],        # 9
    ['goblin', 'compilador', 'aranha'],        # 10 (chefe)
    ['doppelganger', 'virus', 'inseto'],       # 11
    ['golem', 'doppelganger'],                 # 12
    ['dragao', 'aranha', 'goblin'],            # 13
    ['dragao', 'golem', 'doppelganger'],       # 14
    ['inseto', 'bug_original', 'virus'],       # 15 (chefe final)
]

# Botões desenhados em batalha.png
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
LARGURA_QUADRO = 290           # a moldura é esticada sem distorcer os cantos
BORDA_QUADRO = 32              # px da moldura (cantos) em quadro_habilidades.png
# parte de dentro da moldura, em fração do quadro: (esquerda, cima, direita, baixo)
INTERIOR_QUADRO = (0.12, 0.09, 0.88, 0.92)
TAM_BOTAO_HAB = (212, 60)      # tamanho dos botões dentro do quadro (= tamanho do PNG)
ALTURA_BOTAO_ITEM = 34         # botões dos itens são mais baixos

# Quadro de itens: mesma moldura, mas com os botões em 2 colunas
# (5 linhas cada: 9 itens + VOLTAR no fim da 2ª coluna).
COLUNAS_ITENS = 2
LINHAS_ITENS = 5
ESPACO_ITENS = 10              # px entre os botões dos itens
# margens (px) da parte de dentro da moldura: esquerda, cima, direita, baixo
MARGENS_QUADRO = (35, 33, 35, 30)
LARGURA_QUADRO_ITENS = (MARGENS_QUADRO[0] + MARGENS_QUADRO[2]
                        + COLUNAS_ITENS * TAM_BOTAO_HAB[0] + (COLUNAS_ITENS - 1) * 14)
ALTURA_QUADRO_ITENS = (MARGENS_QUADRO[1] + MARGENS_QUADRO[3]
                       + LINHAS_ITENS * ALTURA_BOTAO_ITEM
                       + (LINHAS_ITENS + 1) * ESPACO_ITENS)

TAM_PERSONAGEM = 96
TAM_INIMIGO = 120  # só para o placeholder (usado se o sprite do inimigo não existir)

# ---------- sprites dos inimigos ----------
# Procurados em assets/sprites/inimigos/.
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

# Posição dos inimigos: "chão" (onde ficam os pés). O chão dos cenários
# começa por volta de y = 455; quanto mais para baixo, mais "perto" da tela.
# Com 3 inimigos, o maior fica ao fundo, no centro, e os outros dois na
# frente, nas laterais. Todos ficam à direita de x = 876 (caixa do menu).
CHAO_INIMIGOS = 590         # 1 inimigo
CHAO_FUNDO_INIMIGOS = 470   # quem está mais ao fundo (logo depois da borda do chão)
CHAO_FRENTE_INIMIGOS = 650  # quem está mais à frente

# Formação do grupo: 2 linhas x 2 colunas.
# A linha de cima (1º e 2º escolhidos) fica NA FRENTE (mais perto dos
# inimigos); a de baixo fica atrás, recuada para a esquerda.
# DESLOC_TRAS = 0 alinha tudo em uma grade reta.
# O chão dos 3 cenários começa por volta de y = 445-455: os pés da linha de cima
# (y + 96) ficam logo abaixo disso, para ninguém parecer flutuar.
LINHAS_Y = (372, 545)   # y do sprite de cada linha (cabem nome + vida + mana)
X_FRENTE = 170          # x do 1º personagem da linha da frente
ESPACO_X = 125          # distância horizontal entre os dois da linha
DESLOC_TRAS = 80        # quanto a linha de trás recua para a esquerda

# Invocações (Torreta): ficam à frente do time, na altura da linha da frente
X_INVOCACAO = X_FRENTE + 2 * ESPACO_X
TAM_INVOCACAO = 80

# ---------- ampliação (destaque e hover) ----------
ESCALA_TURNO = 1.2            # personagem que está na vez
ESCALA_HOVER_INIMIGO = 1.1    # inimigo debaixo do mouse ao escolher o alvo
ESCALA_HOVER_BOTAO = 1.08     # botões debaixo do mouse
# (a animação em si — Zoom e ampliar — fica em telas.py)


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


# Um fundo a cada 5 fases (batalha1.png, batalha2.png, batalha3.png)
fundos_batalha = {
    n: pygame.transform.scale(carregar(f'batalha{n}.png', TELAS).convert(),
                              (LARGURA, ALTURA))
    for n in (1, 2, 3)
}

# Os botões de ação fazem parte do fundo: recorta cada um para poder ampliá-lo
img_botoes_acao = {nome: fundos_batalha[1].subsurface(rect).copy()
                   for nome, rect in BOTOES_ACAO.items()}
img_mensagens = carregar('mensagens.png').convert_alpha()

# contorno.png tem 4 px de borda; esticado para a largura do sprite.
# A mesma moldura é usada nas barras de vida e de mana.
BORDA_BARRA = 4
ALTURA_BARRA = 22
_contorno = carregar('contorno.png').convert_alpha()
moldura_barra = nove_fatias(_contorno, TAM_PERSONAGEM, ALTURA_BARRA, BORDA_BARRA)
moldura_invocacao = nove_fatias(_contorno, TAM_INVOCACAO, ALTURA_BARRA, BORDA_BARRA)
# Inimigos usam a moldura vermelha; chefes, a moldura própria (borda direita
# mais grossa, por isso a fatia de 8 px para não deformar o canto).
CHEFES = {'dragao', 'compilador', 'bug_original'}
moldura_inimigo = nove_fatias(
    carregar('contorno_inimigo.png').convert_alpha(),
    TAM_INIMIGO, ALTURA_BARRA, BORDA_BARRA
)
moldura_chefe = nove_fatias(
    carregar('contorno_boss.png').convert_alpha(),
    TAM_INIMIGO, ALTURA_BARRA, 8
)
# Telas de fim de luta: vitoria_fase.png é semitransparente (fica por cima
# da batalha); vitoria_final.png ocupa a tela inteira.
tela_vitoria_fase = pygame.transform.scale(
    carregar('vitoria_fase.png', TELAS).convert_alpha(), (LARGURA, ALTURA))
tela_vitoria_final = pygame.transform.scale(
    carregar('vitoria_final.png', TELAS).convert(), (LARGURA, ALTURA))

# ---------- texto (fonte pixel: rpg/fonte_pixel.py) ----------
# Tamanho do "pixel" da letra: 2 -> letras de 14 px, 3 -> 21 px, 4 -> 28 px.
TAM_NOME = 2
TAM_HP = 2
ESCALA_HP = 0.75      # números das barras um pouco menores (letras de ~10 px)
TAM_LOG = 2
TAM_DANO = 3
ESPACO_LOG = 20       # px entre as linhas do painel de mensagens


def _cores(cor):
    """Aceita um degradê pronto (lista de fonte_pixel) ou uma cor só."""
    if isinstance(cor, list):
        return cor
    if cor == (255, 255, 255):
        return fp.BRANCO
    return fp.degrade(cor)


def escrita(conteudo, tam=TAM_NOME, cor=(255, 255, 255), sombra=1):
    """Superfície com o texto na fonte pixel. Com sombra=1, o meio da letra
    fica exatamente no meio da superfície (dá para centralizar pelo rect)."""
    return fp.texto(conteudo, cores=_cores(cor), sombra=sombra, tam_bloco=tam)


def largura_texto(conteudo, tam):
    """Largura (px) que o texto vai ter, sem precisar desenhá-lo."""
    return (len(fp.mascara(conteudo)[0]) + 2) * tam


# Camadas escuras semitransparentes (criadas uma vez, não a cada quadro)
sombra_menu = pygame.Surface(CAIXA_MENU.size, pygame.SRCALPHA)
sombra_menu.fill((0, 0, 0, 150))
escuro_fim = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
escuro_fim.fill((0, 0, 0, 170))


def escurecer(superficie):
    s = superficie.copy()
    s.fill((90, 90, 90, 255), special_flags=pygame.BLEND_RGBA_MULT)
    return s


def carregar_sprite(arquivo, tamanho, pasta):
    img = carregar(arquivo, pasta).convert_alpha()
    return pygame.transform.scale(img, (tamanho, tamanho))


_cache_inimigos = {}


def achar_arquivo_inimigo(chave):
    nome = ARQUIVOS_INIMIGOS.get(chave, f'{chave}.png')
    caminho = INIMIGOS / nome
    return caminho if caminho.exists() else None


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
            img = carregar_sprite('placeholder.png', TAM_INIMIGO, INIMIGOS)

        _cache_inimigos[chave] = (img, escurecer(img))

    return _cache_inimigos[chave]


_botao_habilidade = carregar('botao_habilidade.png').convert_alpha()
botao_vazio = pygame.transform.scale(_botao_habilidade, TAM_BOTAO_HAB)
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


# 54 -> 34 px: tira 10 linhas da faixa azul-esverdeada e 10 da azul-escura
# (faixas de cor constante), então o botão não fica distorcido.
_botao_54 = pygame.transform.scale(_botao_habilidade, (TAM_BOTAO_HAB[0], 54))
botao_item = recortar_linhas(_botao_54, [(0, 16), (26, 29), (39, 54)])
botao_item_apagado = escurecer(botao_item)


def carregar_quadro(largura=LARGURA_QUADRO, altura=ALTURA_QUADRO):
    caminho = INTERFACE / 'quadro_habilidades.png'
    if caminho.exists():
        img = pygame.image.load(str(caminho)).convert_alpha()
        b = BORDA_QUADRO
        w, h = img.get_size()
        quadro = pygame.Surface((largura, altura), pygame.SRCALPHA)
        # miolo (nove_fatias só desenha as bordas)
        miolo = img.subsurface((b, b, w - 2 * b, h - 2 * b))
        quadro.blit(pygame.transform.scale(
            miolo, (largura - 2 * b, altura - 2 * b)), (b, b))
        quadro.blit(nove_fatias(img, largura, altura, b), (0, 0))
        return quadro

    print('[aviso] quadro_habilidades.png não encontrado; usando um quadro simples')
    img = pygame.Surface((largura, altura), pygame.SRCALPHA)
    img.fill((18, 30, 54, 255))
    pygame.draw.rect(img, (120, 140, 180), img.get_rect(), 6)
    return img


quadro_habilidades = carregar_quadro()
RECT_QUADRO = quadro_habilidades.get_rect(
    midbottom=(CAIXA_MENU.centerx, CAIXA_MENU.top - 2)
)
quadro_itens = carregar_quadro(LARGURA_QUADRO_ITENS, ALTURA_QUADRO_ITENS)
RECT_QUADRO_ITENS = quadro_itens.get_rect(
    midbottom=(CAIXA_MENU.centerx, CAIXA_MENU.top - 2)
)

_cache_texto = {}


# ---------- efeitos de dano ----------
# Quem leva dano pisca em branco, dá um "pulo" de tamanho (como o hover) e
# solta um número vermelho (ex.: -4) que sobe e some.
DURACAO_PISCADA = 250        # ms do brilho branco
DURACAO_PULO = 300           # ms da ampliação
ESCALA_DANO = 1.1            # tamanho máximo no meio do pulo
DURACAO_NUMERO = 1000        # ms até o número sumir
SUBIDA_NUMERO = 45           # quantos pixels o número sobe


def silhueta_branca(img):
    """Cópia do sprite toda branca (mantendo a transparência)."""
    branca = img.copy()
    branca.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_MAX)
    return branca


def texto_dano(valor):
    """'-N' vermelho com contorno escuro (para ler sobre qualquer fundo)."""
    # cópia: o alpha muda enquanto o número some, e a original fica no cache
    return escrita(f'-{valor}', TAM_DANO, fp.VERMELHO).copy()


def _quebrar_em_duas(conteudo, tam):
    """Divide o texto em 2 linhas o mais equilibradas possível (ou None)."""
    palavras = conteudo.split()
    melhor = None
    for k in range(1, len(palavras)):
        linhas = [' '.join(palavras[:k]), ' '.join(palavras[k:])]
        pior = max(largura_texto(l, tam) for l in linhas)
        if melhor is None or pior < melhor[0]:
            melhor = (pior, linhas)
    return melhor[1] if melhor else None


def texto_botao(conteudo, cor, largura_max, altura_max=34):
    """Texto legível para botões: usa o MAIOR tamanho que couber, em 1 linha
    ou, se for longo, quebrado em 2 linhas. O meio da imagem é o meio do texto."""
    chave = (conteudo, cor, largura_max, altura_max)
    if chave in _cache_texto:
        return _cache_texto[chave]

    escolhido = None
    for tam in (3, 2):  # do maior para o menor
        passo = 10 * tam  # 7 da letra + 3 de vão
        for linhas in ([conteudo], _quebrar_em_duas(conteudo, tam)):
            if not linhas:
                continue
            largura = max(largura_texto(l, tam) for l in linhas)
            # altura da letra com contorno (os acentos podem passar um pouco)
            altura = (len(linhas) - 1) * passo + 9 * tam
            if largura <= largura_max and altura <= altura_max:
                escolhido = (tam, linhas)
                break
        if escolhido:
            break

    if escolhido is None:  # nem o menor coube: usa o menor e encolhe a largura
        escolhido = (2, [conteudo])

    tam, linhas = escolhido
    passo = 10 * tam
    imgs = [escrita(l, tam, cor) for l in linhas]
    largura = max(i.get_width() for i in imgs)
    img = pygame.Surface((largura, imgs[0].get_height() + passo * (len(linhas) - 1)),
                         pygame.SRCALPHA)
    for n, i in enumerate(imgs):  # linhas centralizadas
        img.blit(i, ((largura - i.get_width()) // 2, n * passo))

    if img.get_width() > largura_max:
        img = pygame.transform.scale(img, (largura_max, img.get_height()))

    _cache_texto[chave] = img
    return img


# Cursor (seta para baixo) mostrado sobre quem está na vez e sobre o alvo
# que está debaixo do mouse (a mesma imagem da tela de seleção).
cursor_turno = cursor_vertical


def desenhar_cursor(tela, centro_x, base_y):
    """Desenha o cursor com a ponta em (centro_x, base_y), sem sair da tela."""
    rect = cursor_turno.get_rect(midbottom=(centro_x, base_y))
    rect.clamp_ip(tela.get_rect())
    tela.blit(cursor_turno, rect)


def texto(tela, conteudo, centro, tam=TAM_NOME, cor=(255, 255, 255)):
    """Escreve com o meio do texto em `centro`."""
    img = escrita(conteudo, tam, cor)
    tela.blit(img, img.get_rect(center=centro))


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

    info = texto_barra(f'{valor}/{maximo}', largura)
    # (sem sombra, o meio da letra fica meio bloco abaixo do meio da imagem)
    tela.blit(info, info.get_rect(center=(centro[0], centro[1] - 1)))


_cache_barra = {}


def texto_barra(conteudo, largura):
    """Números das barras: fonte pixel tamanho TAM_HP reduzida para ESCALA_HP."""
    chave = (conteudo, largura)
    if chave not in _cache_barra:
        img = escrita(conteudo, TAM_HP, sombra=0)
        w = round(img.get_width() * ESCALA_HP)
        h = round(img.get_height() * ESCALA_HP)
        # número grande: encolhe mais para caber na barra
        _cache_barra[chave] = pygame.transform.scale(img, (min(w, largura), h))
    return _cache_barra[chave]


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
        self.novo_personagem = None  # índice do personagem liberado ao zerar o jogo
        self.zoom = Zoom()           # personagens, inimigos e botões de ação
        self.zoom_quadro = Zoom()    # botões do quadro de habilidades/itens
        self.ultimo_dano = {}        # id(combatente) -> instante (ms) do último dano
        self.numeros_dano = []       # números flutuantes: [img, x, y, inicio]

        self.sprites = {}
        for p in self.grupo:
            img = carregar_sprite(p.SPRITE, TAM_PERSONAGEM, PERSONAGENS)
            self.sprites[id(p)] = (img, escurecer(img))

        self.iniciar_fase()

    # ---------- fases ----------
    def iniciar_fase(self):
        for p in self.grupo:
            p.remover_defesa()
            p.limpar_efeitos()  # escudos da luta anterior não passam de fase
            p.invocacao = None  # a torreta não passa de fase
            if self.fase > 0:
                p.descansar()   # recupera parte da vida/mana entre as fases
        limpar()
        self.zoom.limpar()
        self.zoom_quadro.limpar()
        self.ultimo_dano.clear()
        self.numeros_dano.clear()
        for p in self.grupo:
            p.danos_recentes.clear()

        self.inimigos = [criar_inimigo(chave) for chave in FASES[self.fase]]
        self.rects_inimigos = self.calcular_rects_inimigos()
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

    def calcular_rects_inimigos(self):
        imgs = [imagem_inimigo(e.chave)[0] for e in self.inimigos]
        n = len(imgs)

        if n == 1:
            pontos = [(1060, CHAO_INIMIGOS)]
        elif n == 2:
            # em diagonal: um mais ao fundo (direita), outro mais à frente
            pontos = [(1170, CHAO_FUNDO_INIMIGOS + 50), (970, CHAO_FRENTE_INIMIGOS - 35)]
        elif n == 3:
            fundo = max(range(3), key=lambda i: imgs[i].get_height())
            frente = [i for i in range(3) if i != fundo]
            pontos = [None] * 3
            pontos[fundo] = (1115, CHAO_FUNDO_INIMIGOS)
            pontos[frente[0]] = (1185, CHAO_FRENTE_INIMIGOS)
            pontos[frente[1]] = (950, CHAO_FRENTE_INIMIGOS)
        else:  # mais de 3: duas colunas, em várias fileiras
            pontos = [(1170 - (i % 2) * 210, CHAO_FRENTE_INIMIGOS - (i // 2) * 150)
                      for i in range(n)]

        return [img.get_rect(midbottom=ponto) for img, ponto in zip(imgs, pontos)]

    def ordem_de_tras_para_frente(self):
        """Índices dos inimigos do fundo para a frente (quem está mais abaixo
        na tela fica na frente)."""
        return sorted(range(len(self.inimigos)),
                      key=lambda i: self.rects_inimigos[i].bottom)

    def botoes_quadro(self, atual):
        """Botões dentro do quadro (habilidades ou poções, conforme o modo):
        [(rect, 'habilidade' | 'item' | 'voltar', dados)]."""
        if self.modo == 'itens':
            return self.botoes_itens()

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
        espaco = min(14, max(3, (interior.height - n * alt) // (n + 1)))
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

    def botoes_itens(self):
        """Botões do quadro de itens, em colunas (de cima para baixo, depois
        a próxima coluna); VOLTAR fica no último espaço."""
        entradas = [('item', chave) for chave in itens.POCOES]

        q = RECT_QUADRO_ITENS
        esq, cima, _, _ = MARGENS_QUADRO
        larg, alt = TAM_BOTAO_HAB[0], ALTURA_BOTAO_ITEM

        def rect(coluna, linha):
            x = q.x + esq + coluna * (larg + 14)
            y = q.y + cima + ESPACO_ITENS + linha * (alt + ESPACO_ITENS)
            return pygame.Rect(x, y, larg, alt)

        botoes = []
        for n, (tipo, dados) in enumerate(entradas):
            coluna, linha = divmod(n, LINHAS_ITENS)
            botoes.append((rect(coluna, linha), tipo, dados))
        # VOLTAR: canto de baixo à direita
        botoes.append((rect(COLUNAS_ITENS - 1, LINHAS_ITENS - 1), 'voltar', None))
        return botoes

    def inimigo_na_posicao(self, pos):
        # quem está na frente é testado primeiro
        for i in reversed(self.ordem_de_tras_para_frente()):
            inimigo = self.inimigos[i]
            if (inimigo in self.luta.grupo_inimigos and inimigo.vida > 0
                    and self.rects_inimigos[i].collidepoint(pos)):
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
        elif self.modo == 'alvo' and self.item_escolhido:  # adaga
            self.modo = 'itens'
        elif self.modo == 'alvo_aliado':
            self.modo = 'habilidades' if self.habilidade_escolhida else 'itens'
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

        elif tipo_alvo == 'aliado':
            if not any(p.vida > 0 and p.vida < p.vida_maxima for p in self.grupo):
                registrar(f'Ninguém precisa de {nome} agora!')
                return
            self.habilidade_escolhida = chave
            self.modo = 'alvo_aliado'

        elif tipo_alvo == 'protegido':  # qualquer aliado vivo
            self.habilidade_escolhida = chave
            self.modo = 'alvo_aliado'

        elif tipo_alvo == 'morto':
            if not any(p.vida <= 0 for p in self.grupo):
                registrar('Nenhum aliado está derrotado!')
                return
            self.habilidade_escolhida = chave
            self.modo = 'alvo_aliado'

        else:  # 'todos', 'time', 'mortos' ou 'nenhum': não precisa escolher alvo
            mana_antes = atual.mana
            self.luta.executar_acao_jogador(chave)
            if atual.mana < mana_antes:  # funcionou (gastou mana): fecha o quadro
                self.modo = 'acao'

    def escolher_item(self, chave):
        nome = itens.nome_pocao(chave)

        if self.inventario.get(chave, 0) <= 0:
            registrar(f'Você não tem mais {nome}!')
            return

        tipo_alvo = itens.alvo_item(chave)
        if tipo_alvo == 'inimigo':   # adaga: escolhe o inimigo
            self.item_escolhido = chave
            self.modo = 'alvo'
            return
        if tipo_alvo == 'todos':     # bomba: acerta todos na hora
            antes = self.inventario[chave]
            self.luta.usar_pocao(chave, None, self.inventario)
            if self.inventario[chave] < antes:  # funcionou: fecha o quadro
                self.modo = 'acao'
            return

        if not any(itens.pode_usar(chave, p)[0] for p in self.grupo):
            registrar(f'Ninguém precisa de {nome} agora!')
            return

        self.item_escolhido = chave
        self.modo = 'alvo_aliado'

    def aliado_valido(self, aliado):
        """Quem pode receber a poção/habilidade escolhida (para contornar)."""
        if self.item_escolhido:
            return itens.pode_usar(self.item_escolhido, aliado)[0]
        if self.habilidade_escolhida:
            atual = self.luta.combatente_atual()
            tipo = atual.HABILIDADES[self.habilidade_escolhida]['alvo']
            if tipo == 'morto':  # reviver: só derrotado
                return aliado.vida <= 0
            if tipo == 'protegido':  # escudo: qualquer aliado vivo
                return aliado.vida > 0
            # cura: só vivo e ferido
            return aliado.vida > 0 and aliado.vida < aliado.vida_maxima
        return False

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
            self.clicar_botao_acao(ev.pos)

        elif self.modo == 'alvo':
            alvo = self.inimigo_na_posicao(ev.pos)
            if alvo:
                if self.item_escolhido:  # adaga
                    self.luta.usar_pocao(self.item_escolhido, alvo, self.inventario)
                else:
                    acao = self.habilidade_escolhida or 'atacar'
                    self.luta.executar_acao_jogador(acao, alvo)
                self.modo = 'acao'
                self.habilidade_escolhida = None
                self.item_escolhido = None
            else:
                # Clique fora de um alvo não cancela (só botão direito/ESC);
                # os botões de ação ainda trocam de ação.
                self.clicar_botao_acao(ev.pos)

        elif self.modo == 'alvo_aliado':
            for i, aliado in enumerate(self.grupo):
                if self.rect_clique_personagem(i).collidepoint(ev.pos):
                    if self.item_escolhido:
                        chave = self.item_escolhido
                        antes = self.inventario[chave]
                        self.luta.usar_pocao(chave, aliado, self.inventario)
                        usou = self.inventario[chave] < antes
                    else:
                        mana_antes = atual.mana
                        tipo = atual.HABILIDADES[self.habilidade_escolhida]['alvo']
                        if not self.aliado_valido(aliado) and tipo != 'morto':
                            # (reviver em alguém vivo já avisa sozinho)
                            registrar(f'{aliado.nome} não precisa de cura!'
                                      if aliado.vida > 0 else
                                      f'{aliado.nome} está derrotado!')
                        self.luta.executar_acao_jogador(self.habilidade_escolhida, aliado)
                        usou = atual.mana < mana_antes

                    if usou:  # o turno passou
                        self.modo = 'acao'
                        self.item_escolhido = None
                        self.habilidade_escolhida = None
                    return None  # se não deu certo, continua escolhendo

            # Clique fora de um aliado não cancela (só botão direito/ESC)
            self.clicar_botao_acao(ev.pos)

        return None

    def clicar_botao_acao(self, pos):
        for nome, rect in BOTOES_ACAO.items():
            if rect.collidepoint(pos):
                self.clicar_acao(nome)
                return

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
            else:  # venceu a última fase: o jogo foi zerado (e é salvo)
                self.novo_personagem = progresso.registrar_zerada()

    # ---------- desenho ----------
    def desenhar(self, tela, mouse):
        numero_fundo = (self.fase // 5) + 1
        fundo_atual = fundos_batalha[numero_fundo]

        tela.blit(fundo_atual, (0, 0))
        atual = self.luta.combatente_atual()

        self.desenhar_inimigos(tela, mouse, atual)
        self.desenhar_personagens(tela, mouse, atual)
        self.desenhar_invocacoes(tela, atual)
        # (na vitória, a tela semitransparente fica por cima: sem mensagens
        # atrás do título)
        if self.luta.resultado != 'vitoria':
            self.desenhar_log(tela, atual)
        self.desenhar_menu(tela, mouse, atual)

        self.desenhar_numeros_dano(tela)

        if self.luta.resultado:
            self.desenhar_fim(tela)

    # ---------- efeitos de dano ----------
    def sprite_com_dano(self, combatente, img, rect, fator, acima=10):
        """Lê os danos novos do combatente e devolve (imagem, rect) já com o
        pulo de tamanho e o brilho branco aplicados."""
        agora = pygame.time.get_ticks()
        if combatente.danos_recentes:
            self.ultimo_dano[id(combatente)] = agora
            # Vários danos de uma vez (ex.: ataque múltiplo) saem um pouco
            # acima um do outro, para não ficarem sobrepostos.
            for n, valor in enumerate(combatente.danos_recentes):
                self.numeros_dano.append(
                    [texto_dano(valor), rect.centerx, rect.y - acima - n * 26, agora])
            # Um som só por combatente (o do maior golpe), para os ataques
            # múltiplos não empilharem vários sons ao mesmo tempo.
            tocar_dano(max(combatente.danos_recentes))
            combatente.danos_recentes.clear()

        t = agora - self.ultimo_dano.get(id(combatente), -10 ** 9)
        if t < DURACAO_PULO:
            fator *= 1 + (ESCALA_DANO - 1) * math.sin(math.pi * t / DURACAO_PULO)
        img_final, rect_final = ampliar(img, rect, fator, 'midbottom')

        if t < DURACAO_PISCADA:
            branca = silhueta_branca(img_final)
            branca.set_alpha(round(255 * (1 - t / DURACAO_PISCADA)))
            img_final = img_final.copy()
            img_final.blit(branca, (0, 0))
        return img_final, rect_final

    def desenhar_numeros_dano(self, tela):
        agora = pygame.time.get_ticks()
        self.numeros_dano = [n for n in self.numeros_dano
                             if agora - n[3] < DURACAO_NUMERO]
        for img, x, y, inicio in self.numeros_dano:
            progresso_t = (agora - inicio) / DURACAO_NUMERO
            # sobe rápido no começo e desacelera; some aos poucos
            subida = SUBIDA_NUMERO * (1 - (1 - progresso_t) ** 2)
            img.set_alpha(round(255 * (1 - progresso_t)))
            tela.blit(img, img.get_rect(midbottom=(x, round(y - subida))))

    def desenhar_personagens(self, tela, mouse, atual):
        for i, p in enumerate(self.grupo):
            rect = self.rect_personagem(i)
            normal, morto = self.sprites[id(p)]

            # Quem está na vez fica maior (cresce para cima, pés no lugar)
            na_vez = p is atual and p.vida > 0 and not self.luta.resultado
            fator = self.zoom.escala(('personagem', id(p)), na_vez, ESCALA_TURNO)
            img, rect_sprite = self.sprite_com_dano(
                p, normal if p.vida > 0 else morto, rect, fator)

            # Intangível: sprite meio transparente
            if p.intangivel > 0 and p.vida > 0:
                img = img.copy()
                img.set_alpha(110)
            tela.blit(img, rect_sprite)

            # Defendendo: contorno azul no sprite
            if p.defendendo and p.vida > 0:
                pygame.draw.rect(tela, (80, 160, 255), rect_sprite.inflate(6, 6), 3)

            # Provocando: contorno vermelho (os inimigos só atacam ele)
            if p.provocacao > 0 and p.vida > 0:
                pygame.draw.rect(tela, (230, 50, 50), rect_sprite.inflate(14, 14), 3)

            # Nome logo abaixo do sprite, depois a barra de vida e a de mana
            texto(tela, p.nome, (rect.centerx, rect.bottom + 14))
            y_vida = rect.bottom + 28
            barra_vida(tela, rect.x, y_vida, rect.width, p, moldura_barra)
            barra_mana(tela, rect.x, y_vida + ALTURA_BARRA + 2, rect.width,
                       p, moldura_barra)

            # Escolhendo quem recebe a poção: contorna quem pode usá-la
            if self.modo == 'alvo_aliado' and self.aliado_valido(p):
                sobre = self.rect_clique_personagem(i).collidepoint(mouse)
                cor = (80, 255, 120) if sobre else (255, 255, 255)
                pygame.draw.rect(tela, cor, rect_sprite.inflate(10, 10), 3)

            # Cursor sobre quem está na vez
            if p is atual and p.vida > 0:
                desenhar_cursor(tela, rect_sprite.centerx, rect_sprite.y - 4)

    def desenhar_invocacoes(self, tela, atual):
        for k, inv in enumerate(self.luta.invocacoes):
            if id(inv) not in self.sprites:
                img = carregar_sprite(inv.SPRITE, TAM_INVOCACAO, PERSONAGENS)
                self.sprites[id(inv)] = (img, escurecer(img))
            normal, _ = self.sprites[id(inv)]

            # pés alinhados com os da linha da frente
            base = LINHAS_Y[0] + TAM_PERSONAGEM
            rect = pygame.Rect(X_INVOCACAO + k * (TAM_INVOCACAO + 20),
                               base - TAM_INVOCACAO, TAM_INVOCACAO, TAM_INVOCACAO)

            na_vez = inv is atual and inv.vida > 0 and not self.luta.resultado
            fator = self.zoom.escala(('invocacao', id(inv)), na_vez, ESCALA_TURNO)
            # (chamado mesmo destruída, para o número do último dano aparecer)
            img, rect_sprite = self.sprite_com_dano(inv, normal, rect, fator)
            if inv.vida <= 0:
                continue  # destruída: some da tela

            tela.blit(img, rect_sprite)
            texto(tela, inv.nome, (rect.centerx, rect.bottom + 14))
            barra_vida(tela, rect.x, rect.bottom + 28, rect.width, inv,
                       moldura_invocacao)

            if inv is atual:
                desenhar_cursor(tela, rect_sprite.centerx, rect_sprite.y - 4)

    def desenhar_inimigos(self, tela, mouse, atual):
        sobre = self.inimigo_na_posicao(mouse) if self.modo == 'alvo' else None

        for i in self.ordem_de_tras_para_frente():
            inimigo = self.inimigos[i]
            if inimigo not in self.luta.grupo_inimigos:
                continue  # fugiu

            rect = self.rects_inimigos[i]
            vivo = inimigo.vida > 0
            normal, morto = imagem_inimigo(inimigo.chave)

            # Alvo debaixo do mouse fica um pouco maior (pés no lugar)
            fator = self.zoom.escala(('inimigo', id(inimigo)),
                                     vivo and inimigo is sobre, ESCALA_HOVER_INIMIGO)
            img, rect_sprite = self.sprite_com_dano(
                inimigo, normal if vivo else morto, rect, fator,
                acima=34)  # acima do nome

            # Nome sobre a cabeça, sprite, barra de vida embaixo dos pés
            nome = inimigo.nome + (' (DEF)' if inimigo.defendendo else '')
            meia = largura_texto(nome, TAM_NOME) // 2 + 6  # nome longo não sai da tela
            cx = min(max(rect.centerx, meia), LARGURA - meia)
            texto(tela, nome, (cx, rect_sprite.y - 14))
            tela.blit(img, rect_sprite)
            moldura = moldura_chefe if inimigo.chave in CHEFES else moldura_inimigo
            barra_vida(tela, rect.centerx - TAM_INIMIGO // 2, rect.bottom + 4,
                       TAM_INIMIGO, inimigo, moldura)

            # Cursor sobre quem está na vez e sobre o alvo debaixo do mouse
            # (acima do nome)
            if vivo and (inimigo is atual or inimigo is sobre):
                desenhar_cursor(tela, cx, rect_sprite.y - 24)

    def status(self, atual):
        """Linha de status mostrada no painel de mensagens."""
        if self.luta.resultado or not atual:
            return None
        if self.vez_do_jogador():
            if self.modo == 'alvo':
                if self.item_escolhido:
                    nome = itens.nome_pocao(self.item_escolhido)
                    return f'{nome}: escolha o alvo (botão direito volta)', (255, 255, 255)
                if self.habilidade_escolhida:
                    nome = atual.HABILIDADES[self.habilidade_escolhida]['nome']
                    return f'{nome}: escolha o alvo (botão direito volta)', (255, 255, 255)
                return 'Escolha o alvo (botão direito cancela)', (255, 255, 255)
            if self.modo == 'habilidades':
                return 'Escolha uma habilidade (botão direito volta)', (255, 255, 255)
            if self.modo == 'itens':
                return 'Escolha um item (botão direito volta)', (255, 255, 255)
            if self.modo == 'alvo_aliado':
                if self.item_escolhido:
                    nome = itens.nome_pocao(self.item_escolhido)
                else:
                    nome = atual.HABILIDADES[self.habilidade_escolhida]['nome']
                return f'{nome}: escolha o aliado (botão direito volta)', (255, 255, 255)
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
        # (4 px de folga em cima/embaixo para os acentos)
        tela.set_clip(AREA_TEXTO.inflate(0, 8))
        for n, (msg, cor) in enumerate(linhas):
            img = escrita(msg, TAM_LOG, cor)
            if img.get_width() > AREA_TEXTO.width:  # mensagem longa: encolhe
                img = pygame.transform.scale(
                    img, (AREA_TEXTO.width, img.get_height())
                )
            # meio da letra de cada linha
            meio_y = AREA_TEXTO.y + 12 + n * ESPACO_LOG
            tela.blit(img, img.get_rect(midleft=(AREA_TEXTO.x - TAM_LOG, meio_y)))
        tela.set_clip(None)

    def botao_escolhido(self):
        """Qual botão de ação está em uso agora (fica ampliado até a ação acontecer)."""
        if self.modo == 'alvo':
            if self.item_escolhido:
                return 'itens'
            return 'habilidades' if self.habilidade_escolhida else 'atacar'
        if self.modo == 'alvo_aliado':
            return 'itens' if self.item_escolhido else 'habilidades'
        if self.modo in ('habilidades', 'itens'):
            return self.modo
        return None

    def desenhar_menu(self, tela, mouse, atual):
        vez = self.vez_do_jogador()
        escolhido = self.botao_escolhido() if vez else None

        # Botões de ação: ampliados quando o mouse está em cima e
        # enquanto a ação deles está escolhida (até ser executada)
        for nome, rect in BOTOES_ACAO.items():
            ampliado = vez and (rect.collidepoint(mouse) or nome == escolhido)
            fator = self.zoom.escala(('botao', nome), ampliado, ESCALA_HOVER_BOTAO)
            img, rect_img = ampliar(img_botoes_acao[nome], rect, fator)
            if fator != 1.0:
                tela.blit(img, rect_img)

        if vez and self.modo in ('habilidades', 'itens'):
            self.desenhar_quadro(tela, mouse, atual)
        else:
            self.zoom_quadro.limpar()
            if not vez:  # menu apagado durante o turno dos inimigos
                tela.blit(sombra_menu, CAIXA_MENU)

    def desenhar_quadro(self, tela, mouse, atual):
        if self.modo == 'itens':
            tela.blit(quadro_itens, RECT_QUADRO_ITENS)
        else:
            tela.blit(quadro_habilidades, RECT_QUADRO)

        desenhos = []
        for rect, tipo, dados in self.botoes_quadro(atual):
            sobre = rect.collidepoint(mouse)
            chave = (tipo, dados[0] if tipo == 'habilidade' else dados)
            fator = self.zoom_quadro.escala(chave, sobre, ESCALA_HOVER_BOTAO)
            img, rect_img = ampliar(
                self.superficie_botao_quadro(rect, tipo, dados, atual), rect, fator
            )
            desenhos.append((fator, img, rect_img))

        # os ampliados por último, para ficarem por cima dos vizinhos
        for _, img, rect_img in sorted(desenhos, key=lambda d: d[0]):
            tela.blit(img, rect_img)

    def superficie_botao_quadro(self, rect, tipo, dados, atual):
        """Desenha um botão do quadro numa superfície do tamanho dele."""
        sup = pygame.Surface(rect.size, pygame.SRCALPHA)
        w, h = rect.size
        baixo = h == ALTURA_BOTAO_ITEM
        normal = botao_item if baixo else botao_vazio
        apagado = botao_item_apagado if baixo else botao_vazio_apagado
        centro_y = h // 2 - (2 if baixo else 3)
        alt_texto = h - 12 if baixo else h - 20
        # nome à esquerda (~70% da largura), número à direita
        x_nome, larg_nome = round(w * 0.41), round(w * 0.69)
        x_num, larg_num = round(w * 0.885), round(w * 0.19)

        if tipo == 'voltar':
            sup.blit(normal, (0, 0))
            img = texto_botao('VOLTAR', (255, 200, 50), w - 24, alt_texto)
            sup.blit(img, img.get_rect(center=(w // 2, centro_y)))

        elif tipo == 'item':
            nome = itens.nome_pocao(dados)
            qtd = self.inventario.get(dados, 0)
            tem = qtd > 0
            sup.blit(normal if tem else apagado, (0, 0))
            img = texto_botao(nome, (255, 200, 50) if tem else (150, 150, 150),
                              larg_nome, alt_texto)
            sup.blit(img, img.get_rect(center=(x_nome, centro_y)))
            img = texto_botao(f'x{qtd}', (120, 205, 255) if tem else (230, 90, 80),
                              larg_num, alt_texto)
            sup.blit(img, img.get_rect(center=(x_num, centro_y)))

        else:
            chave, nome, custo, _ = dados
            tem_mana = atual.tem_mana(chave)
            sup.blit(normal if tem_mana else apagado, (0, 0))
            cor_nome = (255, 200, 50) if tem_mana else (150, 150, 150)
            cor_custo = (120, 205, 255) if tem_mana else (230, 90, 80)
            # nome à esquerda, custo de mana à direita
            img = texto_botao(nome, cor_nome, larg_nome, alt_texto)
            sup.blit(img, img.get_rect(center=(x_nome, centro_y)))
            img = texto_botao(str(custo), cor_custo, larg_num, 30)
            sup.blit(img, img.get_rect(center=(x_num, centro_y)))

        return sup

    def desenhar_fim(self, tela):
        if self.luta.resultado == 'vitoria':
            if self.fase + 1 >= len(FASES):
                self.desenhar_vitoria_final(tela)
            else:
                self.desenhar_vitoria_fase(tela)
            return

        meio = LARGURA // 2
        tela.blit(escuro_fim, (0, 0))
        fp.escrever(tela, 'DERROTA...', (meio, 290), k=3, cores=fp.VERMELHO)
        fp.escrever(tela, 'CLIQUE PARA VOLTAR AO MENU', (meio, 420), cores=fp.BRANCO)

    def desenhar_vitoria_fase(self, tela):
        """vitoria_fase.png + as poções ganhas dentro do quadro
        (entre as duas linhas douradas: y de ~300 a ~500)."""
        meio = LARGURA // 2
        tela.blit(tela_vitoria_fase, (0, 0))

        if not self.drops:
            fp.escrever(tela, 'NENHUMA POÇÃO DESTA VEZ...', (meio, 400),
                        cores=fp.BRANCO, tam_bloco=3)
            return

        fp.escrever(tela, 'VOCÊ CONSEGUIU:', (meio, 332), cores=fp.DOURADO)
        linhas = [f'{qtd}X {itens.nome_pocao(chave)}' for chave, qtd in self.drops.items()]
        if len(linhas) <= 4:  # uma coluna
            for n, linha in enumerate(linhas):
                fp.escrever(tela, linha, (meio, 378 + n * 34),
                            cores=fp.VERDE, tam_bloco=3)
        else:                 # muitas poções: duas colunas, letra menor
            por_coluna = (len(linhas) + 1) // 2
            for n, linha in enumerate(linhas):
                coluna, lin = divmod(n, por_coluna)
                fp.escrever(tela, linha, (meio - 240 + coluna * 270, 372 + lin * 28),
                            cores=fp.VERDE, tam_bloco=2, alinhar='esquerda')

    def desenhar_vitoria_final(self, tela):
        """vitoria_final.png + quantas vezes zerou e quem foi desbloqueado
        (no quadro abaixo do troféu: y de ~430 a ~580)."""
        meio = LARGURA // 2
        tela.blit(tela_vitoria_final, (0, 0))

        n = progresso.zeradas()
        linhas = [(f'JOGO ZERADO {n} {"VEZ" if n == 1 else "VEZES"}!', fp.DOURADO)]
        if self.novo_personagem is not None:
            novo = todos_personagens[self.novo_personagem]
            linhas.append(('PERSONAGEM DESBLOQUEADO:', fp.BRANCO))
            linhas.append((f'{novo.nome} ({novo.CLASSE})', fp.VERDE))
        else:
            linhas.append(('OBRIGADO POR JOGAR!', fp.CIANO))

        espaco = 38
        y0 = 504 - (len(linhas) - 1) * espaco // 2   # centralizado no quadro
        for k, (linha, cores) in enumerate(linhas):
            fp.escrever(tela, linha, (meio, y0 + k * espaco), cores=cores, tam_bloco=3)
