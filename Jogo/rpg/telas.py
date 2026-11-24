from pathlib import Path

import pygame

from . import progresso
from .personagens import todos_personagens

pygame.init()

LARGURA = 1280
ALTURA = 720
tela = pygame.display.set_mode((LARGURA, ALTURA))

# jogo/assets/sprites (a pasta rpg/ fica ao lado de assets/)
SPRITES = Path(__file__).resolve().parent.parent / 'assets' / 'sprites'
# subpastas de assets/sprites
INIMIGOS = SPRITES / 'inimigos'        # sprites dos inimigos (+ placeholder)
PERSONAGENS = SPRITES / 'personagens'  # sprites dos personagens jogáveis
TELAS = SPRITES / 'telas'              # fundos: menu, seleção, batalha
INTERFACE = SPRITES / 'interface'      # cursores, botões, molduras, contador


def carregar(nome, pasta=INTERFACE):
    return pygame.image.load(str(pasta / nome))


# ---------- ampliação suave (hover) ----------
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
    """Recorta o que já está desenhado em `rect` e desenha ampliado por cima
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
    pygame.Rect(185, 340, 310, 80),
    pygame.Rect(160, 442, 365, 82),
    pygame.Rect(215, 540, 250, 80),
]

clique_menu = [
    'selecao',
    'opcao',
    'sair',
]

botao_voltar = pygame.Rect(10, 650, 170, 65)

# IMAGENS
menu = carregar('tela_menu.png', TELAS).convert()
selecao = carregar('tela_selecao.png', TELAS).convert()
cursor_vertical = carregar('cursor.png').convert_alpha()
cursor = carregar('cursor2.png').convert_alpha()
selecionado = carregar('selecionado.png').convert_alpha()
botao_confirmar = carregar('botao_confirmar.png').convert_alpha()

# REDIMENSIONAMENTO
menu = pygame.transform.scale(menu, (LARGURA, ALTURA))
selecao = pygame.transform.scale(selecao, (LARGURA, ALTURA))
cursor = pygame.transform.scale(cursor, (32, 32))
selecionado = pygame.transform.scale(selecionado, (220, 220))  # tamanho do slot

# Botão de confirmar: canto inferior direito (alinhado ao VOLTAR) e versão
# apagada para quando ainda não há 4 personagens escolhidos
botao_jogar = pygame.Rect(
    LARGURA - 10 - botao_confirmar.get_width(),
    ALTURA - 2 - botao_confirmar.get_height(),
    *botao_confirmar.get_size()
)
botao_confirmar_apagado = botao_confirmar.copy()
botao_confirmar_apagado.fill((110, 110, 110, 255), special_flags=pygame.BLEND_RGBA_MULT)

# Contador "N/4" feito com as imagens grupo1..grupo4 e grupo (a barra "/")
ESCALA_NUMEROS = 0.6


def carregar_numero(nome):
    img = carregar(nome).convert_alpha()
    w, h = img.get_size()
    return pygame.transform.scale(
        img, (int(w * ESCALA_NUMEROS), int(h * ESCALA_NUMEROS))
    )


numeros = {n: carregar_numero(f'grupo{n}.png') for n in (1, 2, 3, 4)}
barra_contador = carregar_numero('grupo.png')

fonte_botao = pygame.font.Font(None, 44)
fonte_titulo = pygame.font.Font(None, 64)
fonte_slot = pygame.font.Font(None, 28)

# Personagens desbloqueados nos espaços de baixo ("?"): a arte do espaço fica
# coberta por um fundo igual ao dos espaços de cima e o sprite é desenhado nele.
COR_FUNDO_SLOT = (21, 41, 74)
# parte de dentro do espaço (x, y, largura, altura), relativa ao canto dele
INTERIOR_SLOT = (17, 16, 192, 196)
TAM_SPRITE_SLOT = 176
_cache_sprites_slot = {}


def sprite_do_slot(i):
    if i not in _cache_sprites_slot:
        img = carregar(todos_personagens[i].SPRITE, PERSONAGENS).convert_alpha()
        _cache_sprites_slot[i] = pygame.transform.scale(
            img, (TAM_SPRITE_SLOT, TAM_SPRITE_SLOT)
        )
    return _cache_sprites_slot[i]


def texto_contorno(tela, conteudo, centro, fonte, cor=(255, 255, 255)):
    sombra = fonte.render(conteudo, True, (0, 0, 0))
    img = fonte.render(conteudo, True, cor)
    rect = img.get_rect(center=centro)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx or dy:
                tela.blit(sombra, rect.move(dx, dy))
    tela.blit(img, rect)


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

        if i >= progresso.BASICOS:
            if i < liberados:
                # desbloqueado: cobre o "?" e mostra o personagem
                ix, iy, iw, ih = INTERIOR_SLOT
                interior = pygame.Rect(botao.x + ix, botao.y + iy, iw, ih)
                pygame.draw.rect(tela, COR_FUNDO_SLOT, interior)
                sprite = sprite_do_slot(i)
                tela.blit(sprite, sprite.get_rect(center=interior.center))
            else:
                # bloqueado: diz quantas vezes é preciso zerar o jogo
                n = i - progresso.BASICOS + 1
                texto_contorno(
                    tela, f'Zere o jogo {n} {"vez" if n == 1 else "vezes"}',
                    (botao.centerx, botao.bottom - 30), fonte_slot
                )

        if i in selecionados:
            tela.blit(selecionado, botao.topleft)

        # espaço debaixo do mouse cresce (com personagem e moldura juntos)
        sobre = i < liberados and botao.collidepoint(mouse)
        rect = destacar(tela, ('slot', i), botao, sobre, ESCALA_HOVER_SLOT)

        if sobre:
            tela.blit(
                cursor_vertical,
                (rect.centerx - 10, rect.top - 45)
            )

    # VOLTAR faz parte da imagem de fundo
    destacar(tela, ('selecao', 'voltar'), botao_voltar,
             botao_voltar.collidepoint(mouse))

    # Botão de confirmar: só fica "aceso" (e cresce) com 4 personagens escolhidos
    pronto = len(selecionados) == 4
    tela.blit(botao_confirmar if pronto else botao_confirmar_apagado, botao_jogar)
    destacar(tela, ('selecao', 'confirmar'), botao_jogar,
             pronto and botao_jogar.collidepoint(mouse))

    desenhar_contador(tela, len(selecionados))


def tela_opcoes(tela, mouse):
    tela.blit(menu, (0, 0))

    escuro = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    escuro.fill((0, 0, 0, 180))
    tela.blit(escuro, (0, 0))

    titulo = fonte_titulo.render('OPÇÕES - em construção', True, (255, 255, 255))
    tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, ALTURA // 2)))

    sobre = botao_voltar.collidepoint(mouse)
    cor = (200, 50, 40) if sobre else (160, 40, 30)
    pygame.draw.rect(tela, cor, botao_voltar, border_radius=6)
    pygame.draw.rect(tela, (255, 200, 60), botao_voltar, 4, border_radius=6)
    texto = fonte_botao.render('< VOLTAR', True, (255, 255, 255))
    tela.blit(texto, texto.get_rect(center=botao_voltar.center))
    destacar(tela, ('opcoes', 'voltar'), botao_voltar, sobre)
