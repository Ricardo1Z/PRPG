from pathlib import Path

import pygame

from .personagens import personagens_liberados

pygame.init()

LARGURA = 1280
ALTURA = 720
tela = pygame.display.set_mode((LARGURA, ALTURA))

# jogo/assets/sprites (a pasta rpg/ fica ao lado de assets/)
SPRITES = Path(__file__).resolve().parent.parent / 'assets' / 'sprites'


def carregar(nome):
    return pygame.image.load(str(SPRITES / nome))


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
menu = carregar('tela_menu.png').convert()
selecao = carregar('tela_selecao.png').convert()
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


def tela_menu(tela, mouse):
    tela.blit(menu, (0, 0))

    for botao_m in botoes_menu:
        if botao_m.collidepoint(mouse):
            tela.blit(cursor, (botao_m.left - 35, botao_m.centery - 16))


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

    for i, botao in enumerate(botoes_selecao):
        liberado = i < len(personagens_liberados)

        if liberado and botao.collidepoint(mouse):
            tela.blit(
                cursor_vertical,
                (botao.right - 120, botao.centery - 155)
            )

        if i in selecionados:
            tela.blit(selecionado, botao.topleft)

    # Botão de confirmar: só fica "aceso" com 4 personagens escolhidos
    pronto = len(selecionados) == 4
    tela.blit(botao_confirmar if pronto else botao_confirmar_apagado, botao_jogar)

    desenhar_contador(tela, len(selecionados))


def tela_opcoes(tela, mouse):
    tela.blit(menu, (0, 0))

    escuro = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    escuro.fill((0, 0, 0, 180))
    tela.blit(escuro, (0, 0))

    titulo = fonte_titulo.render('OPÇÕES - em construção', True, (255, 255, 255))
    tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, ALTURA // 2)))

    cor = (200, 50, 40) if botao_voltar.collidepoint(mouse) else (160, 40, 30)
    pygame.draw.rect(tela, cor, botao_voltar, border_radius=6)
    pygame.draw.rect(tela, (255, 200, 60), botao_voltar, 4, border_radius=6)
    texto = fonte_botao.render('< VOLTAR', True, (255, 255, 255))
    tela.blit(texto, texto.get_rect(center=botao_voltar.center))
