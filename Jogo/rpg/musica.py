import json
from pathlib import Path
import pygame

# assets/audio (a pasta rpg/ fica ao lado de assets/)
PASTA = Path(__file__).resolve().parent.parent / 'assets' / 'audio'
EXT = '.mp3'   # mudança entre .mp3 ou .wav se for necessário

MUSICA_MENU = str(PASTA / f'musica_menu{EXT}')
MUSICA_VITORIA = str(PASTA / 'vitoria.mp3')

# Cada volume vai de 0 a 100 (%). O volume final de um som é
# volume_base_do_som × geral × (musica ou efeitos).
# Os valores ficam salvos em opcoes.json.
ARQUIVO_OPCOES = Path(__file__).resolve().parent.parent / 'opcoes.json'
VOLUMES_PADRAO = {'geral': 80, 'musica': 60, 'efeitos': 70}


def _ler_volumes():
    volumes = dict(VOLUMES_PADRAO)
    try:
        dados = json.loads(ARQUIVO_OPCOES.read_text(encoding='utf-8'))
        for chave in volumes:
            if chave in dados:
                volumes[chave] = max(0, min(100, int(dados[chave])))
    except (OSError, ValueError, TypeError, AttributeError):
        pass  # sem arquivo (ou arquivo estragado): usa os padrões
    return volumes


volumes = _ler_volumes()


def salvar_volumes():
    try:
        ARQUIVO_OPCOES.write_text(json.dumps(volumes), encoding='utf-8')
    except OSError:
        print('[aviso] não foi possível salvar as opções')


def definir_volume(chave, valor):
    """Muda um volume ('geral', 'musica' ou 'efeitos') na hora."""
    volumes[chave] = max(0, min(100, int(round(valor))))
    _aplicar_volume_musica()


def _fator(chave):
    return volumes['geral'] / 100 * volumes[chave] / 100


FASE_CHEFE_FINAL = 15
MUSICA_FINAL = str(PASTA / 'musica_final.wav')


def musica_da_fase(fase):
    if fase >= FASE_CHEFE_FINAL:
        return MUSICA_FINAL
    if fase <= 5:
        nome = 'musica_fase1'
    elif fase <= 10:
        nome = 'musica_fase6'
    else:
        nome = 'musica_fase11'
    return str(PASTA / f'{nome}{EXT}')


_atual = None
_volume_base_musica = 0.5


def _aplicar_volume_musica():
    if pygame.mixer.get_init():
        pygame.mixer.music.set_volume(_volume_base_musica * _fator('musica'))


def tocar(caminho, volume=0.5, repetir=True):
    global _atual, _volume_base_musica
    if caminho == _atual:      # já está tocando, não reinicia
        return
    _atual = caminho
    _volume_base_musica = volume
    pygame.mixer.music.fadeout(500)
    pygame.mixer.music.load(caminho)
    _aplicar_volume_musica()
    pygame.mixer.music.play(-1 if repetir else 0)


# efeitos sonoros de dano 
DANO_LEVE = str(PASTA / 'dano_leve.wav')
DANO_PESADO = str(PASTA / 'dano_pesado.wav')
LIMITE_DANO_LEVE = 20 

_sons = {}  # carregados na primeira vez que forem usados


def _som(caminho):
    if caminho not in _sons:
        try:
            _sons[caminho] = pygame.mixer.Sound(caminho)
        except (pygame.error, FileNotFoundError):
            _sons[caminho] = None  # sem áudio / arquivo faltando: fica mudo
    return _sons[caminho]


def tocar_efeito(caminho, volume=0.7):
    som = _som(caminho)
    if som:
        som.set_volume(volume * _fator('efeitos'))
        som.play()


def tocar_dano(valor, volume=0.7):
    """Toca o som de dano leve ou pesado."""
    if valor <= 0:
        return
    tocar_efeito(DANO_LEVE if valor <= LIMITE_DANO_LEVE else DANO_PESADO, volume)
