"""Fichas e criação dos inimigos."""
import random

import pygame

from sistemas import graficos, ui

INIMIGOS = {
    "goblin": {
        "nome": "Goblin", "vida_maxima": 45, "energia_maxima": 20, "forca": 10, "defesa": 4,
        "experiencia": 25, "tier": 1, "especial": "Golpe Sujo", "especial_tipo": "critico",
        "descricao": "Pequeno e traiçoeiro. Seu golpe sujo tem grande chance de ser crítico.",
    },
    "esqueleto": {
        "nome": "Esqueleto", "vida_maxima": 60, "energia_maxima": 20, "forca": 13, "defesa": 6,
        "experiencia": 40, "tier": 1, "especial": "Flecha Óssea", "especial_tipo": "perfurante",
        "descricao": "Guardião do cemitério. A flecha óssea ignora a sua defesa.",
    },
    "zumbi": {
        "nome": "Zumbi", "vida_maxima": 90, "energia_maxima": 20, "forca": 12, "defesa": 3,
        "experiencia": 55, "tier": 1, "especial": "Mordida Podre", "especial_tipo": "vampirico",
        "descricao": "Lento e resistente. A mordida podre recupera a vida do zumbi.",
    },
    # ---- savana e deserto (do mais fraco ao mais forte: cobra < escorpião < múmia < demônio < gorila)
    "cobra": {
        "nome": "Cobra", "vida_maxima": 55, "energia_maxima": 20, "forca": 15, "defesa": 5,
        "experiencia": 50, "tier": 2, "especial": "Presa Venenosa", "especial_tipo": "perfurante",
        "descricao": "Rápida e silenciosa. A presa venenosa ignora a sua defesa.",
    },
    "escorpiao": {
        "nome": "Escorpião", "vida_maxima": 75, "energia_maxima": 20, "forca": 17, "defesa": 8,
        "experiencia": 70, "tier": 2, "especial": "Ferrão Letal", "especial_tipo": "critico",
        "descricao": "Couraça dura do deserto. O ferrão letal tem grande chance de ser crítico.",
    },
    "mumia": {
        "nome": "Múmia", "vida_maxima": 120, "energia_maxima": 25, "forca": 19, "defesa": 9,
        "experiencia": 95, "tier": 3, "especial": "Maldição Antiga", "especial_tipo": "vampirico",
        "descricao": "Guardiã de tumbas esquecidas. A maldição antiga rouba a sua vida.",
    },
    "demonio": {
        "nome": "Demônio", "vida_maxima": 160, "energia_maxima": 30, "forca": 24, "defesa": 12,
        "experiencia": 140, "tier": 3, "especial": "Chama Infernal", "especial_tipo": "poderoso",
        "especial_mult": 1.8,
        "descricao": "Surgiu das dunas em chamas. A chama infernal causa dano devastador.",
    },
    "gorila": {
        "nome": "Gorila Mutante", "vida_maxima": 240, "energia_maxima": 30, "forca": 30, "defesa": 16,
        "experiencia": 220, "tier": 3, "especial": "Soco Esmagador", "especial_tipo": "poderoso",
        "especial_mult": 2.0,
        "descricao": "O mais temível de todos. O soco esmagador pode acabar a luta em poucos golpes.",
    },
}

SIMBOLOS = {"goblin": "G", "esqueleto": "E", "zumbi": "Z",
            "cobra": "C", "escorpiao": "S", "mumia": "M", "demonio": "D", "gorila": "K"}


def criar_inimigo(tipo, nivel=1):
    """Cria um inimigo. Os atributos crescem 12% por nível do jogador acima do 1."""
    base = INIMIGOS[tipo]
    fator = 1 + 0.12 * (nivel - 1)
    inimigo = dict(base)
    for chave in ("vida_maxima", "forca", "defesa", "experiencia"):
        inimigo[chave] = int(round(base[chave] * fator))
    inimigo["tipo"] = tipo
    inimigo["nivel"] = nivel
    inimigo["vida"] = inimigo["vida_maxima"]
    inimigo["energia"] = inimigo["energia_maxima"]
    return inimigo


def inimigo_aleatorio(nivel=1):
    return criar_inimigo(random.choice(list(INIMIGOS)), nivel)


def tela_bestiario(tela):
    """Mostra as fichas dos inimigos, 3 por página (setas esquerda/direita mudam de página)."""
    relogio = pygame.time.Clock()
    por_pagina = 3
    tipos = list(INIMIGOS)
    paginas = (len(tipos) + por_pagina - 1) // por_pagina
    pagina = 0
    pygame.event.clear(pygame.KEYDOWN)
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                ui.sair()
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER):
                    return
                elif ev.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_SPACE):
                    pagina = (pagina + 1) % paginas
                elif ev.key in (pygame.K_LEFT, pygame.K_a):
                    pagina = (pagina - 1) % paginas
        ui.fundo_reino(tela)
        ui.texto(tela, f"BESTIÁRIO  ({pagina + 1}/{paginas})", 480, 30, 34, ui.OURO, True, "centro")
        for i, tipo in enumerate(tipos[pagina * por_pagina:(pagina + 1) * por_pagina]):
            ini = criar_inimigo(tipo)
            x = 25 + i * 310
            ui.painel(tela, (x, 90, 290, 470))
            tela.blit(graficos.obter_sprite(tipo, 128), (x + 81, 105))
            ui.texto(tela, f'{ini["nome"]}  ({SIMBOLOS[tipo]})', x + 145, 240, 24, ui.OURO, True, "centro")
            stats = (f'Vida: {ini["vida_maxima"]}', f'Energia: {ini["energia_maxima"]}',
                     f'Força: {ini["forca"]}', f'Defesa: {ini["defesa"]}', f'XP ao vencer: {ini["experiencia"]}')
            for k, linha in enumerate(stats):
                ui.texto(tela, linha, x + 24, 284 + k * 26, 20)
            ui.texto(tela, f'Habilidade: {ini["especial"]}', x + 24, 422, 18, ui.ROXO, True)
            for k, linha in enumerate(ui.quebrar_texto(ini["descricao"], 17, 245)):
                ui.texto(tela, linha, x + 24, 450 + k * 22, 17, ui.CINZA)
        ui.texto(tela, "← → trocar de página     ENTER ou ESC para voltar", 480, 590, 17, ui.CINZA, False, "centro")
        pygame.display.flip()
        relogio.tick(60)
