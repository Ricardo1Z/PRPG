# 💻 PRPG

Um **RPG de batalha por turnos com temática de programação**, inspirado em roguelikes e feito em Python com a biblioteca Pygame.

## 🎮 Sobre o projeto

No PRPG você monta um grupo de **4 heróis**, cada um inspirado em uma linguagem de programação, e enfrenta **15 fases** seguidas contra inimigos que representam bugs, vírus e outros problemas do desenvolvimento de software.

A vida e a mana do grupo passam de uma fase para a outra, com uma pequena recuperação entre as lutas. Os itens ganhos também continuam com você. Se o grupo inteiro cair, a partida acaba e você volta ao menu.

## 🕹️ Como jogar

1. No **menu**, clique em **JOGAR**.
2. Na **tela de seleção**, escolha 4 personagens e clique em confirmar.
3. Na batalha, quando for a vez de um dos seus personagens, escolha uma ação:
   - **Atacar**: ataque básico em um inimigo.
   - **Defender**: reduz o dano recebido.
   - **Habilidades**: golpes especiais que gastam mana.
   - **Itens**: poções e armas de uso único, que gastam o turno.
4. Vença todos os inimigos para passar para a próxima fase.

**Controles:** o jogo é todo no mouse. O **botão direito** ou **ESC** volta um passo nos menus da batalha. Na tela de opções dá para usar as setas (ou WASD) e arrastar as barras de volume com o mouse.

## ⚔️ Personagens

São 8 personagens jogáveis, cada um com 3 habilidades próprias:

| Linguagem | Classe | Habilidades |
|---|---|---|
| 🐍 Python | Guerreiro | Picada Mortal, Salto de Bits, Provocação Global |
| ☕ Java | Mago | Lançar Exceção, Cadeia de Códigos, Meteoro de Variável |
| 🌐 JavaScript | Ladino | Investida Assíncrona, Rajada de Scripts, Promessa Pendente |
| 🛡️ C# | Paladino | Escudo de Compilação, Código Divino, Restaurar Instância |
| 🔧 C++ | Engenheiro | Barreira de Ponteiros, Falha de Segmentação, Invocar Torreta |
| 🔱 Delphi | Lanceiro | Estocada em Cascata, Giro de Unidade, Lança Perfurante |
| 🏹 PHP | Arqueiro | Chuva de Requisições, Injeção de SQL, Flecha Depreciada |
| 💎 Ruby | Hexxer | Reiniciar Processo, Cura em Bloco, Monkey Patch |

Cada personagem tem vida, mana, ataque, defesa e velocidade próprios. A velocidade define a ordem dos turnos.

As habilidades vão além do dano: há provocação, intangibilidade, escudos, redução de defesa e ataque dos inimigos, cura, reviver aliados e até uma **Torreta** invocada que luta sozinha.

### 🔓 Desbloqueio

Os 4 primeiros personagens já vêm liberados. Cada vez que você **zera o jogo** (vence as 15 fases), um novo personagem é desbloqueado. O progresso fica salvo em `Jogo/save.json`.

> No momento o jogo está em **modo demonstração** (`MODO_DEMO = True` em [rpg/progresso.py](Jogo/rpg/progresso.py)), com todos os personagens liberados.

## 👾 Inimigos

| Inimigo | Comportamento |
|---|---|
| Slime de Código | Sempre ataca |
| Inseto Bugado | Se defende quando está com pouca vida |
| Aranha de Firewall | Pode fugir quando está quase derrotada |
| Goblin de Sintaxe | Pode fugir quando perde boa parte da vida |
| Golem de Erro de Compilação | Muita vida; passa a se defender quando está ferido |
| Plagiador de Código | Ataca, se defende ou foge quando está ferido |
| Vírus Corrompido | Agressivo enquanto tem vida alta |
| 🐉 Dragão do Infinito | Chefe da fase 5 |
| ⚙️ Compilador Supremo | Chefe da fase 10 |
| 🐛 Bug Original | Chefe final (fase 15) |

## 🧪 Itens

O grupo começa com alguns itens e ganha mais ao vencer as lutas. Quanto mais avançada a fase, maior a chance de cair item.

- **Poções de HP** (P, M, G): recuperam vida.
- **Poções de MP** (P, M, G): recuperam mana.
- **Poção de Reviver**: traz de volta um aliado derrotado.
- **Adaga**: causa dano em um inimigo.
- **Bomba**: causa dano em todos os inimigos.

## 🎵 Som e opções

- Músicas diferentes para o menu, para cada bloco de fases (1–5, 6–10, 11–14) e para a luta final.
- Efeitos sonoros de dano leve e pesado.
- Tela de **opções** com volume geral, de música e de efeitos. Os volumes ficam salvos em `Jogo/opcoes.json`.

## ▶️ Como executar

Requisitos: **Python 3** e **Pygame 2.6.1**.

```bash
pip install -r requeriments.txt
cd Jogo
python main.py
```

## 📁 Estrutura

```
PRPG/
├── requeriments.txt
└── Jogo/
    ├── main.py            # loop principal e troca de telas
    ├── assets/
    │   ├── audio/         # músicas e efeitos sonoros
    │   └── sprites/       # inimigos, personagens, telas e interface
    └── rpg/
        ├── batalha.py     # fases e interface da batalha
        ├── luta.py        # regras do combate por turnos
        ├── combatentes.py # classe base de todos os combatentes
        ├── personagens.py # personagens jogáveis e habilidades
        ├── inimigos.py    # inimigos e comportamentos
        ├── itens.py       # poções, armas e drops
        ├── progresso.py   # save e desbloqueio de personagens
        ├── musica.py      # músicas, efeitos e volumes
        ├── telas.py       # menu, seleção e opções
        ├── fonte_pixel.py # fonte pixel desenhada no código
        └── registro.py    # mensagens do log da batalha
```

## 🛠️ Tecnologias utilizadas

- **Python**: linguagem principal do projeto.
- **Pygame**: interface gráfica, áudio e lógica do jogo.

## 🎯 Objetivos do projeto

- Desenvolver um jogo com temática de programação.
- Aplicar conceitos de Programação Orientada a Objetos: classes, herança e polimorfismo.
- Desenvolver um sistema de combate por turnos.
- Implementar diferentes comportamentos para personagens e inimigos.
- Aprimorar conhecimentos em Python e Pygame.

## 🚧 Status do desenvolvimento

O projeto ainda está **em desenvolvimento**. As 15 fases, os 8 personagens, os itens, o som e o sistema de desbloqueio já funcionam, e novas mecânicas e ajustes de balanceamento podem chegar com o tempo.

## 📌 Sobre

Este projeto foi criado para praticar programação e desenvolver um jogo do zero, aplicando na prática o que aprendemos de Python e Pygame.

**Transformando o universo da programação em uma aventura!**
