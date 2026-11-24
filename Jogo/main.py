import copy

import pygame

from rpg.telas import (
    LARGURA,
    ALTURA,
    tela,
    tela_selecao,
    tela_menu,
    tela_opcoes,
    clique_menu,
    botoes_menu,
    botao_voltar,
    botao_jogar,
    botoes_selecao,
)
from rpg.personagens import todos_personagens
from rpg import progresso
from rpg.batalha import Batalha

personagens_selecionados = []
batalha = None

clock = pygame.time.Clock()
rodando = True
tela_atual = "menu"

pygame.display.set_caption("PRPG")

while rodando:
    mouse = pygame.mouse.get_pos()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        elif tela_atual == 'batalha':
            if batalha.evento(evento) == 'menu':
                tela_atual = 'menu'
                batalha = None

        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:

            if tela_atual == 'menu':
                for i, botao_m in enumerate(botoes_menu):
                    if botao_m.collidepoint(evento.pos):
                        if clique_menu[i] == 'sair':
                            rodando = False
                        else:
                            tela_atual = clique_menu[i]

            elif tela_atual == 'opcao':
                if botao_voltar.collidepoint(evento.pos):
                    tela_atual = 'menu'

            elif tela_atual == 'selecao':
                if botao_voltar.collidepoint(evento.pos):
                    tela_atual = 'menu'

                elif botao_jogar.collidepoint(evento.pos):
                    if len(personagens_selecionados) == 4:
                        # Cópias novas: a vida não "vaza" entre partidas
                        grupo = [
                            copy.deepcopy(todos_personagens[i])
                            for i in personagens_selecionados
                        ]
                        batalha = Batalha(grupo)
                        tela_atual = 'batalha'

                else:
                    for i, botao in enumerate(botoes_selecao):
                        if botao.collidepoint(evento.pos):

                            if i >= progresso.quantos_liberados():
                                break

                            if i in personagens_selecionados:
                                personagens_selecionados.remove(i)

                            elif len(personagens_selecionados) < 4:
                                personagens_selecionados.append(i)

                            break

    if tela_atual == 'menu':
        tela_menu(tela, mouse)

    elif tela_atual == 'opcao':
        tela_opcoes(tela, mouse)

    elif tela_atual == 'selecao':
        tela_selecao(tela, mouse, personagens_selecionados)

    elif tela_atual == 'batalha':
        batalha.atualizar()
        batalha.desenhar(tela, mouse)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
