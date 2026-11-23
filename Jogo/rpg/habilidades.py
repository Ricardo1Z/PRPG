from .registro import registrar

def picada_mortal(personagem, alvo):
    if personagem.vida <= 0:
        return False

    if alvo.vida <= 0:
        registrar("Esse inimigo já foi derrotado!")
        return False

    if not personagem.consumir_uso_habilidade("picada_mortal"):
        return False

    dano = 20
    alvo.vida = max(0, alvo.vida - dano)

    registrar(
        f"{personagem.nome} usou Picada Mortal "
        f"e causou {dano} de dano em {alvo.nome}!"
    )

    if alvo.defendendo:
        alvo.remover_defesa()

    return True

def salto_de_bits(personagem, alvo):
    if personagem.vida <= 0 or alvo.vida <= 0:
        return False

    if not personagem.consumir_uso_habilidade("salto_de_bits"):
        return False

    # Ignora 50% da defesa do inimigo
    defesa_aplicada = alvo.defesa // 2

    dano = max(1, 35 - defesa_aplicada)

    alvo.vida = max(0, alvo.vida - dano)

    registrar(
        f"{personagem.nome} usou Salto de Bits "
        f"e causou {dano} de dano em {alvo.nome}!"
    )

    if alvo.defendendo:
        alvo.remover_defesa()

    return True


def cadeia_de_codigos(personagem, grupo_inimigos):
    if personagem.vida <= 0:
        return False

    inimigos_vivos = [
        inimigo for inimigo in grupo_inimigos
        if inimigo.vida > 0
    ]

    if not inimigos_vivos:
        registrar("Não existem inimigos vivos!")
        return False

    if not personagem.consumir_uso_habilidade("cadeia_de_codigos"):
        return False

    registrar(f"{personagem.nome} lançou Cadeia de Códigos!")

    for inimigo in inimigos_vivos:
        dano = max(1, 25 - inimigo.defesa)

        inimigo.vida = max(0, inimigo.vida - dano)

        registrar(
            f"{inimigo.nome} recebeu {dano} de dano! "
            f"Vida restante: {inimigo.vida}"
        )

        if inimigo.defendendo:
            inimigo.remover_defesa()

    return True


def meteoro_de_variavel(personagem, grupo_inimigos):
    if personagem.vida <= 0:
        return False

    inimigos_vivos = [
        inimigo for inimigo in grupo_inimigos
        if inimigo.vida > 0
    ]

    if not inimigos_vivos:
        registrar("Não existem inimigos vivos!")
        return False

    if not personagem.consumir_uso_habilidade("meteoro_de_variavel"):
        return False

    registrar(f"{personagem.nome} lançou Meteoro de Variável!")

    for inimigo in inimigos_vivos:
        # Ignora 50% da defesa
        defesa_aplicada = inimigo.defesa // 2

        dano = max(1, 40 - defesa_aplicada)

        inimigo.vida = max(0, inimigo.vida - dano)

        registrar(
            f"{inimigo.nome} recebeu {dano} de dano! "
            f"Vida restante: {inimigo.vida}"
        )

        if inimigo.defendendo:
            inimigo.remover_defesa()

    return True


def investida_assincrona(personagem, alvo):
    if personagem.vida <= 0 or alvo.vida <= 0:
        return False

    if not personagem.consumir_uso_habilidade("investida_assincrona"):
        return False

    # Ignora 25% da defesa do inimigo
    defesa_aplicada = int(alvo.defesa * 0.75)

    dano = max(1, 30 - defesa_aplicada)

    alvo.vida = max(0, alvo.vida - dano)

    registrar(f"{personagem.nome} usou Investida Assíncrona!")
    registrar(f"{alvo.nome} recebeu {dano} de dano!")
    registrar(f"Vida restante: {alvo.vida}")

    if alvo.defendendo:
        alvo.remover_defesa()

    return True


def rajada_de_scripts(personagem, alvo):
    if personagem.vida <= 0 or alvo.vida <= 0:
        return False

    if not personagem.consumir_uso_habilidade("rajada_de_scripts"):
        return False

    registrar(f"{personagem.nome} usou Rajada de Scripts!")

    for golpe in range(3):
        if alvo.vida <= 0:
            break

        dano = max(1, 15 - alvo.defesa)
        alvo.vida = max(0, alvo.vida - dano)

        registrar(f"Golpe {golpe + 1}: {dano} de dano!")
        registrar(f"Vida restante de {alvo.nome}: {alvo.vida}")

        if alvo.defendendo:
            alvo.remover_defesa()

    return True

def escudo_de_compilacao(personagem):
    if personagem.vida <= 0:
        return False

    if not personagem.consumir_uso_habilidade("escudo_de_compilacao"):
        return False

    personagem.defesa += 20
    personagem.escudo_compilacao_ativo = True

    registrar(f"{personagem.nome} usou Escudo de Compilação!")
    registrar(f"Defesa aumentada em 20! Defesa atual: {personagem.defesa}")

    return True

def codigo_divino(personagem, alvo):
    if personagem.vida <= 0 or alvo.vida <= 0:
        return False

    if not personagem.consumir_uso_habilidade("codigo_divino"):
        return False

    # Ignora 50% da defesa do alvo
    defesa_aplicada = alvo.defesa // 2

    dano = max(1, 40 - defesa_aplicada)

    alvo.vida = max(0, alvo.vida - dano)

    registrar(f"{personagem.nome} usou Código Divino!")
    registrar(f"{alvo.nome} recebeu {dano} de dano!")
    registrar(f"Vida restante: {alvo.vida}")

    if alvo.defendendo:
        alvo.remover_defesa()

    return True