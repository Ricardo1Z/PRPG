"""Registro de mensagens da batalha (aparece na tela e no terminal)."""

mensagens = []


def registrar(texto):
    print(texto)
    mensagens.append(texto)
    del mensagens[:-50]  # guarda só as últimas 50


def limpar():
    mensagens.clear()
