"""Fonte pixel do PRPG (a mesma das telas de menu, seleção, opções e vitória).

Uso:
    from . import fonte_pixel as fp
    fp.escrever(tela, 'VOCÊ CONSEGUIU:', (640, 290))
    fp.escrever(tela, '1X POÇÃO DE HP M', (640, 340), cores=fp.VERDE)

Cada "pixel" da letra é um bloco de 4 px (como o resto da arte). k aumenta a
letra (k=2 -> blocos de 8 px). O texto é sempre em MAIÚSCULAS.
"""

# ----------------------------------------------------------------------
# glifos 5x7 (os acentos ficam em 2 linhas acima, com 1 linha de vão)
# ----------------------------------------------------------------------
GLIFOS = {
    'A': [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    'B': ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    'C': [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    'D': ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    'E': ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    'F': ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    'G': [".####", "#....", "#....", "#..##", "#...#", "#...#", ".###."],
    'H': ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    'I': ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"],
    'J': ["..###", "...#.", "...#.", "...#.", "#..#.", "#..#.", ".##.."],
    'K': ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    'L': ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    'M': ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    'N': ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    'O': [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    'P': ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    'Q': [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    'R': ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    'S': [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    'T': ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    'U': ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    'V': ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    'W': ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    'X': ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    'Y': ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    'Z': ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    '0': [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    '1': ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    '2': [".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"],
    '3': ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    '4': ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    '5': ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    '6': [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    '7': ["#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."],
    '8': [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    '9': [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    '%': ["##...", "##..#", "...#.", "..#..", ".#...", "#..##", "...##"],
    '?': [".###.", "#...#", "....#", "..##.", "..#..", ".....", "..#.."],
    '!': ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    ':': [".....", "..#..", "..#..", ".....", "..#..", "..#..", "....."],
    '.': [".....", ".....", ".....", ".....", ".....", "..#..", "..#.."],
    ',': [".....", ".....", ".....", ".....", "..#..", "..#..", ".#..."],
    '-': [".....", ".....", ".....", ".###.", ".....", ".....", "....."],
    '+': [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
    '#': [".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."],
    '(': ["...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."],
    ')': [".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."],
    '>': ["#....", ".#...", "..#..", "...#.", "..#..", ".#...", "#...."],
    '<': ["....#", "...#.", "..#..", ".#...", "..#..", "...#.", "....#"],
    '/': ["....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."],
    "'": ["..#..", "..#..", ".....", ".....", ".....", ".....", "....."],
}
_AGUDO = ["...#.", "..#.."]
_CIRC = ["..#..", ".#.#."]
_TIL = [".##.#", "#..#."]
_GRAVE = [".#...", "..#.."]
ACENTOS = {
    'Á': ('A', _AGUDO, None), 'É': ('E', _AGUDO, None), 'Í': ('I', _AGUDO, None),
    'Ó': ('O', _AGUDO, None), 'Ú': ('U', _AGUDO, None),
    'Â': ('A', _CIRC, None), 'Ê': ('E', _CIRC, None), 'Ô': ('O', _CIRC, None),
    'À': ('A', _GRAVE, None),
    'Ã': ('A', _TIL, None), 'Õ': ('O', _TIL, None),
    'Ç': ('C', None, ["..#..", ".#..."]),
}
ALT = 12   # 2 acento + 1 vão + 7 letra + 2 rabicho
TOPO = 3   # linha onde começa a letra

# degradês (de cima para baixo)
DOURADO = [(255, 246, 150), (255, 222, 60), (255, 186, 30), (255, 140, 20), (232, 92, 16)]
LARANJA = [(255, 214, 110), (255, 170, 40), (255, 128, 24), (238, 84, 18), (200, 50, 14)]
VERMELHO = [(255, 170, 110), (255, 112, 60), (236, 66, 36), (204, 38, 28), (160, 24, 24)]
CIANO = [(214, 250, 255), (140, 226, 250), (80, 190, 236), (50, 150, 210), (36, 110, 180)]
VERDE = [(220, 255, 200), (150, 240, 130), (90, 210, 100), (50, 170, 80), (30, 130, 60)]
BRANCO = [(255, 255, 255), (236, 240, 250), (210, 220, 238), (180, 192, 216), (150, 164, 196)]
CONTORNO = (34, 10, 8)
SOMBRA = (8, 10, 30)
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def _glifo(c, negrito):
    """Matriz ALT x 5 (ou 6, em negrito) de True/False."""
    acima = abaixo = None
    if c in ACENTOS:
        base, acima, abaixo = ACENTOS[c]
        linhas = GLIFOS[base]
    else:
        linhas = GLIFOS.get(c, GLIFOS['?'])
    g = [[False] * 5 for _ in range(ALT)]
    for i, l in enumerate(linhas):
        g[TOPO + i] = [ch == '#' for ch in l]
    for bloco, y0 in ((acima, 0), (abaixo, TOPO + 7)):
        if bloco:
            for i, l in enumerate(bloco):
                g[y0 + i] = [ch == '#' for ch in l]
    if negrito:
        return [[(row[x] if x < 5 else False) or (row[x - 1] if x > 0 else False)
                 for x in range(6)] for row in g]
    return g


def mascara(texto, negrito=False, espaco=3):
    """Matriz ALT x largura com o texto inteiro (1 coluna de vão entre letras)."""
    linhas = [[] for _ in range(ALT)]
    primeiro = True
    for c in texto.upper():
        if not primeiro:
            for r in linhas:
                r.append(False)
        primeiro = False
        if c == ' ':
            for r in linhas:
                r.extend([False] * espaco)
            continue
        g = _glifo(c, negrito)
        for r, gl in zip(linhas, g):
            r.extend(gl)
    return linhas


def _mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def degrade(cor):
    """Degradê de 5 tons (claro em cima, escuro embaixo) a partir de uma cor."""
    claro = _mix(cor, (255, 255, 255), 0.45)
    escuro = _mix(cor, (0, 0, 0), 0.35)
    return [claro, _mix(claro, cor, 0.5), cor, _mix(cor, escuro, 0.5), escuro]


def blocos(texto, k=1, cores=DOURADO, negrito=False, sombra=1, contorno=CONTORNO, espaco=3):
    """Desenha o texto em uma grade de blocos: {(x, y): cor}, largura, altura.
    (Não depende do pygame: o gerador das imagens usa a mesma função.)"""
    base = mascara(texto, negrito, espaco)
    h0, w0 = len(base), len(base[0]) if base else 0
    m = [[base[y // k][x // k] for x in range(w0 * k)] for y in range(h0 * k)]
    h, w = h0 * k, w0 * k
    W, H = w + 2, h + 2 + sombra
    cheio = set((x, y) for y in range(h) for x in range(w) if m[y][x])
    viz = set()
    for (x, y) in cheio:
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                viz.add((x + 1 + dx, y + 1 + dy))
    px = {}
    for s in range(1, sombra + 1):
        for (x, y) in viz:
            if (x, y + s) not in viz:
                px[(x, y + s)] = SOMBRA
    for p in viz:
        px[p] = contorno
    y0, y1 = TOPO * k, (TOPO + 7) * k
    n = len(cores) - 1
    for (x, y) in cheio:
        t = min(1, max(0, (y - y0) / max(1, (y1 - y0 - 1))))
        i = min(int(t * n), n - 1)
        f = t * n - i
        c = cores[i + 1] if f > (BAYER[y % 4][x % 4] + 0.5) / 16 else cores[i]
        if y == 0 or not m[y - 1][x]:           # brilho no topo do traço
            c = _mix(c, (255, 255, 230), 0.45)
        px[(x + 1, y + 1)] = c
    return px, W, H


# ----------------------------------------------------------------------
# pygame
# ----------------------------------------------------------------------
TAM_BLOCO = 4
_cache = {}


def texto(conteudo, k=1, cores=DOURADO, negrito=False, sombra=1, tam_bloco=TAM_BLOCO):
    """Superfície pygame com o texto (fundo transparente)."""
    import pygame
    chave = (conteudo, k, tuple(cores), negrito, sombra, tam_bloco)
    if chave not in _cache:
        px, w, h = blocos(conteudo, k, cores, negrito, sombra)
        s = pygame.Surface((w * tam_bloco, h * tam_bloco), pygame.SRCALPHA)
        for (x, y), c in px.items():
            s.fill(c, (x * tam_bloco, y * tam_bloco, tam_bloco, tam_bloco))
        _cache[chave] = s
    return _cache[chave]


def escrever(tela, conteudo, centro, k=1, cores=DOURADO, negrito=False, sombra=1,
             alinhar='centro', tam_bloco=TAM_BLOCO):
    """Escreve com o MEIO DA LETRA em centro=(x, y). alinhar: 'centro',
    'esquerda' (x = início do texto) ou 'direita' (x = fim do texto)."""
    s = texto(conteudo, k, cores, negrito, sombra, tam_bloco)
    x, y = centro
    meio_letra = int((1 + (TOPO + 3.5) * k) * tam_bloco)
    if alinhar == 'centro':
        x -= s.get_width() // 2
    elif alinhar == 'direita':
        x -= s.get_width()
    tela.blit(s, (x, y - meio_letra))
    return s.get_width()
