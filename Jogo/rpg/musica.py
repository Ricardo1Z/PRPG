from pathlib import Path
import pygame

# assets/audio (a pasta rpg/ fica ao lado de assets/)
PASTA = Path(__file__).resolve().parent.parent / 'assets' / 'audio'
EXT = '.mp3'   # troque para '.mp3' ou '.wav' se for o caso

MUSICA_MENU = str(PASTA / f'musica_menu{EXT}')


def musica_da_fase(fase):
    if fase <= 5:
        nome = 'musica_fase1'
    elif fase <= 10:
        nome = 'musica_fase6'
    else:
        nome = 'musica_fase11'
    return str(PASTA / f'{nome}{EXT}')


_atual = None


def tocar(caminho, volume=0.5):
    global _atual
    if caminho == _atual:      # já está tocando, não reinicia
        return
    _atual = caminho
    pygame.mixer.music.fadeout(500)
    pygame.mixer.music.load(caminho)
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(-1)