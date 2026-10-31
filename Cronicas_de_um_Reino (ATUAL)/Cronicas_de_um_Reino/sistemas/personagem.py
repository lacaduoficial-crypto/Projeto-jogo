"""Criação do personagem, XP, subida de nível e ficha."""
import pygame

from sistemas import graficos, itens, ui


def novo_personagem(nome, nivel=1):
    j = {
        "nome": nome or "Aventureiro",
        "nivel": 1,
        "vida": 100,
        "vida_maxima": 100,
        "energia": 30,
        "energia_maxima": 30,
        "forca": 15,
        "defesa": 10,
        "experiencia": 0,
        "x": None,
        "y": None,
        "inventario": {"Poção de Vida": 2, "Poção de Energia": 1},
        "equipamento": {"arma": None, "escudo": None, "armadura": None},
    }
    for _ in range(nivel - 1):
        _subir_nivel(j)
    j["vida"] = j["vida_maxima"]
    j["energia"] = j["energia_maxima"]
    itens.garantir_equipamento(j)
    return j


def garantir_campos(j):
    """Completa e corrige um personagem vindo de um save antigo ou incompleto,
    para que nada (como o escudo) quebre por falta de um campo."""
    padrao = novo_personagem(j.get("nome") or "Aventureiro")
    for chave in ("nivel", "vida_maxima", "energia_maxima", "forca", "defesa", "experiencia"):
        valor = j.get(chave)
        if not isinstance(valor, (int, float)) or isinstance(valor, bool):
            j[chave] = padrao[chave]
        else:
            j[chave] = int(valor)
    j["nivel"] = max(1, j["nivel"])
    j["nome"] = j.get("nome") or padrao["nome"]
    j["vida"] = max(1, min(int(j.get("vida", j["vida_maxima"])), j["vida_maxima"]))
    j["energia"] = max(0, min(int(j.get("energia", j["energia_maxima"])), j["energia_maxima"]))
    j.setdefault("x", None)
    j.setdefault("y", None)
    itens.garantir_equipamento(j)
    j["defendendo"] = False
    return j


def xp_para_proximo(j):
    return 50 * j["nivel"]


def _subir_nivel(j):
    j["nivel"] += 1
    j["vida_maxima"] += 10
    j["energia_maxima"] += 5
    j["forca"] += 2
    j["defesa"] += 1


def ganhar_xp(j, xp):
    """Soma XP e sobe de nível quando possível. Retorna lista de mensagens."""
    j["experiencia"] += xp
    msgs = []
    while j["experiencia"] >= xp_para_proximo(j):
        j["experiencia"] -= xp_para_proximo(j)
        _subir_nivel(j)
        j["vida"] = j["vida_maxima"]
        j["energia"] = j["energia_maxima"]
        msgs.append(f'Subiu para o nível {j["nivel"]}! Vida e energia restauradas.')
    return msgs


def desmaiar(j):
    """Consequência de perder uma luta: metade da vida e perda de 20% do XP atual."""
    perda = int(j["experiencia"] * 0.2)
    j["experiencia"] -= perda
    j["vida"] = max(1, j["vida_maxima"] // 2)
    j["energia"] = j["energia_maxima"] // 2
    return f'{j["nome"]} desmaiou, acordou com metade da vida e perdeu {perda} XP.'


def tela_ficha(tela, j, fundo=None):
    relogio = pygame.time.Clock()
    pygame.event.clear(pygame.KEYDOWN)
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                ui.sair()
            if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER,
                                                         pygame.K_SPACE, pygame.K_c):
                return
        (fundo or ui.fundo_reino)(tela)
        ui.painel(tela, (170, 90, 620, 460))
        ui.texto(tela, "FICHA DO PERSONAGEM", 480, 106, 30, ui.OURO, True, "centro")
        tela.blit(graficos.obter_sprite("heroi", 160), (210, 170))
        x = 410
        ui.texto(tela, j["nome"], x, 160, 28, ui.BRANCO, True)
        ui.texto(tela, f'Nível {j["nivel"]}', x, 196, 20, ui.OURO)
        ui.texto(tela, "Vida", x, 238, 18)
        ui.barra(tela, x + 90, 240, 250, 16, j["vida"], j["vida_maxima"], (200, 60, 60),
                 f'{j["vida"]}/{j["vida_maxima"]}')
        ui.texto(tela, "Energia", x, 266, 18)
        ui.barra(tela, x + 90, 268, 250, 16, j["energia"], j["energia_maxima"], (70, 130, 230),
                 f'{j["energia"]}/{j["energia_maxima"]}')
        ui.texto(tela, "XP", x, 294, 18)
        ui.barra(tela, x + 90, 296, 250, 16, j["experiencia"], xp_para_proximo(j), (230, 190, 70),
                 f'{j["experiencia"]}/{xp_para_proximo(j)}')
        ui.texto(tela, f'Força: {itens.forca_total(j)}  (base {j["forca"]} + {itens.bonus(j, "arma")})', x, 336, 20)
        ui.texto(tela, f'Defesa: {itens.defesa_total(j)}  (base {j["defesa"]} + {itens.bonus(j, "escudo")} escudo '
                       f'+ {itens.bonus(j, "armadura")} armadura)', x, 366, 18)
        ui.texto(tela, f'Arma: {j["equipamento"].get("arma") or "nenhuma"}', x, 404, 18, ui.CINZA)
        ui.texto(tela, f'Escudo: {j["equipamento"].get("escudo") or "nenhum"}', x, 428, 18, ui.CINZA)
        ui.texto(tela, f'Armadura: {j["equipamento"].get("armadura") or "nenhuma"}', x, 452, 18, ui.CINZA)
        ui.texto(tela, "ENTER ou ESC para voltar", 480, 512, 16, ui.CINZA, False, "centro")
        pygame.display.flip()
        relogio.tick(60)
