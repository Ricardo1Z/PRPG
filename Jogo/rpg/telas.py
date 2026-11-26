from pathlib import Path

import pygame

from . import progresso
from . import fonte_pixel as fp
from .personagens import todos_personagens
from .musica import volumes, definir_volume, salvar_volumes

pygame.init()

LARGURA = 1280
ALTURA = 720
tela = pygame.display.set_mode((LARGURA, ALTURA))

SPRITES = Path(__file__).resolve().parent.parent / 'assets' / 'sprites'
# subpastas de assets/sprites
INIMIGOS = SPRITES / 'inimigos'        # sprites dos inimigos (+ placeholder)
PERSONAGENS = SPRITES / 'personagens'  # sprites dos personagens jogáveis
TELAS = SPRITES / 'telas'              # fundos: menu, seleção, opções, batalha
INTERFACE = SPRITES / 'interface'      # cursores, botões, molduras, contador


def carregar(nome, pasta=INTERFACE):
    return pygame.image.load(str(pasta / nome))


# hover
ESCALA_HOVER_MENU = 1.04      # botões do menu / VOLTAR / confirmar
ESCALA_HOVER_SLOT = 1.02      # espaços da tela de seleção
VELOCIDADE_ZOOM = 0.25         # 0..1: quanto anda em direção ao tamanho final por quadro


class Zoom:
    """Guarda a escala atual de cada coisa e a anima suavemente."""

    def __init__(self):
        self.valores = {}

    def escala(self, chave, ampliado, alvo):
        atual = self.valores.get(chave, 1.0)
        destino = alvo if ampliado else 1.0
        atual += (destino - atual) * VELOCIDADE_ZOOM
        if abs(destino - atual) < 0.003:
            atual = destino
        self.valores[chave] = atual
        return atual

    def limpar(self):
        self.valores.clear()


def ampliar(img, rect, fator, ancora='center'):
    """(imagem, rect) ampliados por `fator`, presos no ponto `ancora` do rect."""
    if fator == 1.0:
        return img, rect
    nova = pygame.transform.scale(
        img, (round(rect.width * fator), round(rect.height * fator))
    )
    return nova, nova.get_rect(**{ancora: getattr(rect, ancora)})


zoom_telas = Zoom()


def destacar(tela, chave, rect, sobre, alvo=ESCALA_HOVER_MENU):
    """Recorta o que já está desenhado em 'rect' e desenha ampliado por cima
    quando o mouse está em cima. Devolve o rect (ampliado ou não)."""
    fator = zoom_telas.escala(chave, sobre, alvo)
    if fator == 1.0:
        return rect
    img, rect_img = ampliar(tela.subsurface(rect).copy(), rect, fator)
    tela.blit(img, rect_img)
    return rect_img


# BOTÕES
botoes_selecao = [
    pygame.Rect(100, 160, 220, 220),
    pygame.Rect(388, 160, 220, 220),
    pygame.Rect(670, 160, 220, 220),
    pygame.Rect(956, 160, 220, 220),
    pygame.Rect(100, 434, 220, 220),
    pygame.Rect(388, 434, 220, 220),
    pygame.Rect(670, 434, 220, 220),
    pygame.Rect(956, 434, 220, 220),
]

botoes_menu = [
    pygame.Rect(210, 340, 260, 82),   # JOGAR
    pygame.Rect(190, 442, 305, 86),   # OPÇÕES
    pygame.Rect(230, 540, 220, 80),   # SAIR
]

clique_menu = [
    'selecao',
    'opcao',
    'sair',
]

# IMAGENS
menu = carregar('tela_menu.png', TELAS).convert()
selecao = carregar('tela_selecao.png', TELAS).convert()
opcoes = carregar('tela_opcoes.png', TELAS).convert()
cursor_vertical = carregar('cursor.png').convert_alpha()
cursor = carregar('cursor2.png').convert_alpha()
selecionado = carregar('selecionado.png').convert_alpha()
botao_confirmar = carregar('botao_confirmar.png').convert_alpha()
botao_voltar_img = carregar('botao_voltar.png').convert_alpha()

# REDIMENSIONAMENTO
menu = pygame.transform.scale(menu, (LARGURA, ALTURA))
selecao = pygame.transform.scale(selecao, (LARGURA, ALTURA))
opcoes = pygame.transform.scale(opcoes, (LARGURA, ALTURA))
cursor = pygame.transform.scale(cursor, (32, 32))
selecionado = pygame.transform.scale(selecionado, (220, 220))  # tamanho do slot

# Botão de confirmar: canto inferior direito e versão apagada para quando
# ainda não há 4 personagens escolhidos
botao_jogar = pygame.Rect(
    LARGURA - 10 - botao_confirmar.get_width(),
    ALTURA - 2 - botao_confirmar.get_height(),
    *botao_confirmar.get_size()
)
# Botão VOLTAR
botao_voltar = pygame.Rect(
    10, ALTURA - 2 - botao_voltar_img.get_height(), *botao_voltar_img.get_size()
)
botao_confirmar_apagado = botao_confirmar.copy()
botao_confirmar_apagado.fill((110, 110, 110, 255), special_flags=pygame.BLEND_RGBA_MULT)

# Contador "N/4"
numeros = {n: carregar(f'grupo{n}.png').convert_alpha() for n in (1, 2, 3, 4)}
barra_contador = carregar('grupo.png').convert_alpha()

# Os personagens liberados são desenhados pelo código dentro dos espaços.
# Nos espaços de baixo a arte tem o "?" e o aviso "ZERE O JOGO N VEZES": ao
# liberar, o espaço é coberto com o espaço vazio de cima (mesma arte, sem "?").
INTERIOR_SLOT = (16, 16, 188, 188)
TAM_SPRITE_SLOT = 176
COLUNAS_SELECAO = 4
_cache_sprites_slot = {}


def sprite_do_slot(i):
    if i not in _cache_sprites_slot:
        img = carregar(todos_personagens[i].SPRITE, PERSONAGENS).convert_alpha()
        _cache_sprites_slot[i] = pygame.transform.scale(
            img, (TAM_SPRITE_SLOT, TAM_SPRITE_SLOT)
        )
    return _cache_sprites_slot[i]


def tela_menu(tela, mouse):
    tela.blit(menu, (0, 0))

    for i, botao_m in enumerate(botoes_menu):
        sobre = botao_m.collidepoint(mouse)
        rect = destacar(tela, ('menu', i), botao_m, sobre)
        if sobre:
            tela.blit(cursor, (rect.left - 35, rect.centery - 16))


def desenhar_contador(tela, quantidade):
    """Mostra N / 4 ao lado do botão (não aparece com 0 escolhidos)."""
    if quantidade == 0:
        return

    pecas = [numeros[quantidade], barra_contador, numeros[4]]
    espaco = 6
    largura = sum(p.get_width() for p in pecas) + espaco * (len(pecas) - 1)
    x = botao_jogar.left - 24 - largura

    for peca in pecas:
        tela.blit(peca, (x, botao_jogar.centery - peca.get_height() // 2))
        x += peca.get_width() + espaco


def tela_selecao(tela, mouse, selecionados):
    tela.blit(selecao, (0, 0))
    liberados = progresso.quantos_liberados()

    for i, botao in enumerate(botoes_selecao):
        if i >= len(todos_personagens):
            continue

        if i < liberados:
            if i >= progresso.BASICOS:
                # cobre o "?" com o espaço vazio da linha de cima
                acima = botoes_selecao[i % COLUNAS_SELECAO]
                tela.blit(selecao, botao.topleft, acima)
            ix, iy, iw, ih = INTERIOR_SLOT
            interior = pygame.Rect(botao.x + ix, botao.y + iy, iw, ih)
            sprite = sprite_do_slot(i)
            tela.blit(sprite, sprite.get_rect(center=interior.center))

        if i in selecionados:
            tela.blit(selecionado, botao.topleft)

        # espaço debaixo do mouse cresce (com personagem e moldura juntos)
        sobre = i < liberados and botao.collidepoint(mouse)
        rect = destacar(tela, ('slot', i), botao, sobre, ESCALA_HOVER_SLOT)

        if sobre:
            tela.blit(cursor_vertical, (rect.centerx - 16, rect.top - 40))

    tela.blit(botao_voltar_img, botao_voltar)
    destacar(tela, ('selecao', 'voltar'), botao_voltar,
             botao_voltar.collidepoint(mouse))

    # Botão de confirmar: só fica aceso com 4 os personagens escolhidos
    pronto = len(selecionados) == 4
    tela.blit(botao_confirmar if pronto else botao_confirmar_apagado, botao_jogar)
    destacar(tela, ('selecao', 'confirmar'), botao_jogar,
             pronto and botao_jogar.collidepoint(mouse))

    desenhar_contador(tela, len(selecionados))


# tela de opções (volumes) 
OPCOES = ['geral', 'musica', 'efeitos']
DY_OPCAO = 120                       
COR_FUNDO_PAINEL = (14, 26, 58)
COR_SEGMENTO_VAZIO = (18, 30, 62)
COR_SEPARADOR = (8, 16, 40)

CORES_BARRA = {
    'geral': ((255, 214, 110), (255, 150, 30), (210, 80, 16)),
    'musica': ((190, 246, 255), (60, 196, 230), (24, 120, 180)),
    'efeitos': ((190, 246, 255), (60, 196, 230), (24, 120, 180)),
}
CORES_PORCENTO = {'geral': (255, 200, 70), 'musica': (120, 210, 240),
                  'efeitos': (120, 210, 240)}

X_PREENCHE, Y_PREENCHE = 336, 308 
LARG_PREENCHE, ALT_PREENCHE = 572, 12
SEPARADORES = [388, 448, 504, 564, 620, 676, 736, 792, 852]  
RECT_BARRA = pygame.Rect(320, 292, 600, 44)  
RECT_PORCENTO = pygame.Rect(896, 248, 104, 56)
RECT_SETA = pygame.Rect(266, 248, 32, 48)
RECT_PINO = pygame.Rect(784, 296, 12, 40) 
COLUNA_LIMPA_X = 850                           
PASSO_TECLADO = 5

pino = opcoes.subsurface(RECT_PINO).copy()
seta_opcao = opcoes.subsurface(RECT_SETA).copy()

barra_limpa = opcoes.subsurface(RECT_BARRA).copy()
_coluna = opcoes.subsurface((COLUNA_LIMPA_X, RECT_BARRA.y, 1, RECT_BARRA.height))
for _x in range(RECT_PINO.left - RECT_BARRA.x, RECT_PINO.right - RECT_BARRA.x):
    barra_limpa.blit(_coluna, (_x, 0))

opcoes_base = opcoes.copy()
for _k in range(len(OPCOES)):
    _dy = _k * DY_OPCAO
    opcoes_base.fill(COR_FUNDO_PAINEL, RECT_SETA.move(0, _dy))
    opcoes_base.fill(COR_FUNDO_PAINEL, RECT_PORCENTO.move(0, _dy))
    opcoes_base.blit(barra_limpa, RECT_BARRA.move(0, _dy))
    opcoes_base.fill(COR_SEGMENTO_VAZIO,
                     (X_PREENCHE, Y_PREENCHE + _dy, LARG_PREENCHE, ALT_PREENCHE))
    for _sx in SEPARADORES:
        opcoes_base.fill(COR_SEPARADOR, (_sx, Y_PREENCHE + _dy, 4, ALT_PREENCHE))

estado_opcoes = {'selecionada': 0, 'arrastando': None}


def _texto_porcento(valor, cor):
    """'NN%' na fonte pixel (rpg/fonte_pixel.py), em degradê da cor."""
    return fp.texto(f'{valor}%', cores=fp.degrade(cor))


def _desenhar_barra_volume(tela, k, chave):
    dy = k * DY_OPCAO
    valor = volumes[chave]
    fim = X_PREENCHE + round(LARG_PREENCHE * valor / 100)

    claro, medio, escuro = CORES_BARRA[chave]
    terco = ALT_PREENCHE // 3
    y = Y_PREENCHE + dy
    largura = fim - X_PREENCHE
    tela.fill(claro, (X_PREENCHE, y, largura, terco))
    tela.fill(medio, (X_PREENCHE, y + terco, largura, terco))
    tela.fill(escuro, (X_PREENCHE, y + 2 * terco, largura, ALT_PREENCHE - 2 * terco))
    for sx in SEPARADORES:
        if sx < fim:
            tela.fill(COR_SEPARADOR, (sx, y, 4, ALT_PREENCHE))

    x_pino = min(max(fim - 10, X_PREENCHE - 2), X_PREENCHE + LARG_PREENCHE - 10)
    tela.blit(pino, (x_pino, RECT_PINO.y + dy))

    txt = _texto_porcento(valor, CORES_PORCENTO[chave])
    tela.blit(txt, txt.get_rect(midright=RECT_PORCENTO.move(0, dy).midright))


def _opcao_na_posicao(pos):
    for k in range(len(OPCOES)):
        # área da linha: do nome até a barra
        linha = pygame.Rect(RECT_SETA.x, RECT_SETA.y + k * DY_OPCAO,
                            RECT_BARRA.right - RECT_SETA.x, RECT_BARRA.bottom - RECT_SETA.y)
        if linha.collidepoint(pos):
            return k
    return None


def _volume_pelo_mouse(k, x):
    valor = (x - X_PREENCHE) / LARG_PREENCHE * 100
    definir_volume(OPCOES[k], max(0, min(100, valor)))


def evento_opcoes(evento):
    """Trata um evento na tela de opções. Devolve 'menu' para sair dela."""
    est = estado_opcoes

    if evento.type == pygame.KEYDOWN:
        if evento.key == pygame.K_ESCAPE:
            salvar_volumes()
            return 'menu'
        if evento.key in (pygame.K_UP, pygame.K_w):
            est['selecionada'] = (est['selecionada'] - 1) % len(OPCOES)
        elif evento.key in (pygame.K_DOWN, pygame.K_s):
            est['selecionada'] = (est['selecionada'] + 1) % len(OPCOES)
        elif evento.key in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d):
            sinal = -1 if evento.key in (pygame.K_LEFT, pygame.K_a) else 1
            chave = OPCOES[est['selecionada']]
            definir_volume(chave, volumes[chave] + sinal * PASSO_TECLADO)
            salvar_volumes()

    elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
        if botao_voltar.collidepoint(evento.pos):
            salvar_volumes()
            return 'menu'
        k = _opcao_na_posicao(evento.pos)
        if k is not None:
            est['selecionada'] = k
            if RECT_BARRA.move(0, k * DY_OPCAO).collidepoint(evento.pos):
                est['arrastando'] = k
                _volume_pelo_mouse(k, evento.pos[0])

    elif evento.type == pygame.MOUSEMOTION:
        if est['arrastando'] is not None:
            _volume_pelo_mouse(est['arrastando'], evento.pos[0])
        else:
            k = _opcao_na_posicao(evento.pos)
            if k is not None:
                est['selecionada'] = k

    elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
        if est['arrastando'] is not None:
            est['arrastando'] = None
            salvar_volumes()

    return None


def tela_opcoes(tela, mouse):
    tela.blit(opcoes_base, (0, 0))

    for k, chave in enumerate(OPCOES):
        _desenhar_barra_volume(tela, k, chave)

    k = estado_opcoes['selecionada']
    tela.blit(seta_opcao, RECT_SETA.move(0, k * DY_OPCAO))

    tela.blit(botao_voltar_img, botao_voltar)
    destacar(tela, ('opcoes', 'voltar'), botao_voltar,
             botao_voltar.collidepoint(mouse))
