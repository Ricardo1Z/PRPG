import pygame

from .telas import LARGURA, ALTURA, carregar
from .luta import Luta
from .inimigos import criar_inimigo
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

TAM_PERSONAGEM = 96
TAM_INIMIGO = 120

# Formação do grupo: 2 linhas x 2 colunas.
# A linha de cima (1º e 2º escolhidos) fica NA FRENTE (mais perto dos
# inimigos); a de baixo fica atrás, recuada para a esquerda.
# DESLOC_TRAS = 0 alinha tudo em uma grade reta.
LINHAS_Y = (200, 380)   # y do sprite de cada linha
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

# contorno.png tem 4 px de borda; esticado para a largura do sprite
BORDA_VIDA = 4
ALTURA_BARRA = 22
moldura_vida = nove_fatias(
    carregar('contorno.png').convert_alpha(),
    TAM_PERSONAGEM, ALTURA_BARRA, BORDA_VIDA
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


def texto(tela, conteudo, pos, fonte, cor=(255, 255, 255), centro=False):
    sombra = fonte.render(conteudo, True, (0, 0, 0))
    img = fonte.render(conteudo, True, cor)
    rect = img.get_rect(center=pos) if centro else img.get_rect(topleft=pos)
    tela.blit(sombra, rect.move(2, 2))
    tela.blit(img, rect)


def barra_vida(tela, x, y, largura, combatente, moldura=None):
    proporcao = max(0, combatente.vida) / combatente.vida_maxima
    if proporcao > 0.5:
        cor = (60, 200, 70)
    elif proporcao > 0.25:
        cor = (230, 200, 40)
    else:
        cor = (220, 50, 40)

    if moldura:
        # Preenchimento dentro da moldura (contorno.png) e moldura por cima
        ix, iy = x + BORDA_VIDA, y + BORDA_VIDA
        iw = largura - 2 * BORDA_VIDA
        ih = moldura.get_height() - 2 * BORDA_VIDA
        pygame.draw.rect(tela, (60, 15, 15), (ix, iy, iw, ih))
        pygame.draw.rect(tela, cor, (ix, iy, int(iw * proporcao), ih))
        tela.blit(moldura, (x, y))
        centro = (x + largura // 2, y + moldura.get_height() // 2)
    else:
        pygame.draw.rect(tela, (60, 15, 15), (x, y, largura, 14))
        pygame.draw.rect(tela, cor, (x, y, int(largura * proporcao), 14))
        pygame.draw.rect(tela, (0, 0, 0), (x, y, largura, 14), 2)
        centro = (x + largura // 2, y + 7)

    info = fonte_hp.render(f'{combatente.vida}/{combatente.vida_maxima}', True, (255, 255, 255))
    sombra = fonte_hp.render(f'{combatente.vida}/{combatente.vida_maxima}', True, (0, 0, 0))
    tela.blit(sombra, sombra.get_rect(center=(centro[0] + 1, centro[1] + 1)))
    tela.blit(info, info.get_rect(center=centro))


class Batalha:
    def __init__(self, grupo_jogador):
        self.grupo = grupo_jogador
        self.fase = 0
        self.modo = 'acao'  # 'acao' (menu) ou 'alvo' (escolhendo inimigo)

        self.sprites = {}
        for p in self.grupo:
            img = carregar_sprite(SPRITES_PERSONAGENS[p.nome], TAM_PERSONAGEM)
            self.sprites[id(p)] = (img, escurecer(img))

        self.sprite_inimigo = carregar_sprite('placeholder.png', TAM_INIMIGO)
        self.sprite_inimigo_morto = escurecer(self.sprite_inimigo)

        self.iniciar_fase()

    # ---------- fases ----------
    def iniciar_fase(self):
        for p in self.grupo:
            p.remover_defesa()
        limpar()

        self.inimigos = [criar_inimigo(chave) for chave in FASES[self.fase]]
        self.luta = Luta(self.grupo, list(self.inimigos))
        self.modo = 'acao'
        registrar(f'Fase {self.fase + 1}/{len(FASES)}: inimigos à frente!')

    # ---------- posições ----------
    def rect_personagem(self, i):
        linha, coluna = divmod(i, 2)
        x = X_FRENTE - linha * DESLOC_TRAS + coluna * ESPACO_X
        return pygame.Rect(x, LINHAS_Y[linha], TAM_PERSONAGEM, TAM_PERSONAGEM)

    def rect_inimigo(self, i):
        coluna = i % 2
        linha = i // 2
        return pygame.Rect(
            1060 - coluna * 190, 170 + linha * 210, TAM_INIMIGO, TAM_INIMIGO
        )

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
    def evento(self, ev):
        """Retorna 'menu' quando a batalha termina e deve voltar ao menu."""
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            self.modo = 'acao'
            return None

        if ev.type != pygame.MOUSEBUTTONDOWN:
            return None

        # Botão direito cancela a escolha de alvo
        if ev.button == 3:
            self.modo = 'acao'
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

        if self.modo == 'acao':
            for nome, rect in BOTOES_ACAO.items():
                if rect.collidepoint(ev.pos):
                    if nome == 'atacar':
                        self.modo = 'alvo'
                    elif nome == 'defender':
                        self.luta.executar_acao_jogador('defender')
                    else:
                        registrar('Ainda não disponível!')
                    break

        elif self.modo == 'alvo':
            alvo = self.inimigo_na_posicao(ev.pos)
            if alvo:
                self.luta.executar_acao_jogador('atacar', alvo)
                self.modo = 'acao'
            elif not CAIXA_MENU.collidepoint(ev.pos):
                self.modo = 'acao'

        return None

    # ---------- atualização ----------
    def atualizar(self):
        self.luta.atualizar()
        if not self.vez_do_jogador():
            self.modo = 'acao'

    # ---------- desenho ----------
    def desenhar(self, tela, mouse):
        tela.blit(fundo, (0, 0))
        atual = self.luta.combatente_atual()

        self.desenhar_inimigos(tela, mouse, atual)
        self.desenhar_personagens(tela, atual)
        self.desenhar_log(tela, atual)
        self.desenhar_menu(tela, mouse, atual)

        if self.luta.resultado:
            self.desenhar_fim(tela)

    def desenhar_personagens(self, tela, atual):
        for i, p in enumerate(self.grupo):
            rect = self.rect_personagem(i)
            normal, morto = self.sprites[id(p)]

            tela.blit(normal if p.vida > 0 else morto, rect)

            # Defendendo: contorno azul no sprite
            if p.defendendo and p.vida > 0:
                pygame.draw.rect(tela, (80, 160, 255), rect.inflate(6, 6), 3)

            # Nome logo abaixo do sprite e a barra de vida abaixo do nome
            texto(tela, p.nome, (rect.centerx, rect.bottom + 14),
                  fonte_nome, centro=True)
            barra_vida(tela, rect.x, rect.bottom + 28, rect.width, p, moldura_vida)

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
            texto(tela, inimigo.nome + (' (DEF)' if inimigo.defendendo else ''),
                  (rect.centerx, rect.y - 14), fonte_nome, centro=True)
            tela.blit(self.sprite_inimigo if vivo else self.sprite_inimigo_morto, rect)
            barra_vida(tela, rect.x, rect.bottom + 4, rect.width, inimigo)

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
                return 'Escolha o alvo (botão direito cancela)', (255, 255, 255)
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
            if self.modo == 'acao':
                for rect in BOTOES_ACAO.values():
                    if rect.collidepoint(mouse):
                        pygame.draw.rect(tela, (255, 255, 255), rect, 3)
        else:
            # Menu apagado durante o turno dos inimigos
            sombra = pygame.Surface(CAIXA_MENU.size, pygame.SRCALPHA)
            sombra.fill((0, 0, 0, 150))
            tela.blit(sombra, CAIXA_MENU)

    def desenhar_fim(self, tela):
        escuro = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        escuro.fill((0, 0, 0, 170))
        tela.blit(escuro, (0, 0))

        if self.luta.resultado == 'vitoria':
            ultima = self.fase + 1 >= len(FASES)
            titulo = 'VOCÊ VENCEU!' if ultima else 'VITÓRIA!'
            sub = 'Clique para voltar ao menu' if ultima else 'Clique para a próxima fase'
            cor = (255, 220, 40)
        else:
            titulo, sub, cor = 'DERROTA...', 'Clique para voltar ao menu', (230, 70, 60)

        texto(tela, titulo, (LARGURA // 2, 290), fonte_grande, cor, centro=True)
        texto(tela, sub, (LARGURA // 2, 390), fonte_info, centro=True)
