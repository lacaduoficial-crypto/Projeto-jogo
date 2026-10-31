"""Itens, equipamentos, cura e tela de inventário."""
import random

import pygame

from sistemas import salvar, ui

SLOTS = ("arma", "escudo", "armadura")
# slot -> (rótulo na tela, atributo que o bônus aumenta)
ROTULO_SLOT = {"arma": "Arma", "escudo": "Escudo", "armadura": "Armadura"}


def _cura(vida, energia, cor, icone, desc, raridade, tier):
    return {"tipo": "consumivel", "vida": vida, "energia": energia, "cor": cor, "icone": icone,
            "desc": desc, "raridade": raridade, "tier": tier}


def _equip(slot, bonus, cor, desc, raridade, tier):
    return {"tipo": "equipamento", "slot": slot, "bonus": bonus, "cor": cor, "icone": "pocao",
            "desc": desc, "raridade": raridade, "tier": tier}


# tier 1 = floresta, tier 2 = savana, tier 3 = deserto
ITENS = {
    # ---- cura
    "Bandagem": _cura(12, 0, (235, 230, 210), "erva", "Restaura 12 de vida.", 8, 1),
    "Erva Curativa": _cura(20, 0, (80, 190, 90), "erva", "Restaura 20 de vida.", 6, 1),
    "Poção de Vida": _cura(40, 0, (220, 50, 70), "pocao", "Restaura 40 de vida.", 5, 1),
    "Poção de Energia": _cura(0, 15, (60, 140, 240), "pocao", "Restaura 15 de energia (PE).", 4, 1),
    "Elixir Real": _cura(35, 15, (200, 90, 220), "pocao", "Restaura 35 de vida e 15 de energia.", 2, 2),
    "Fruta do Oásis": _cura(30, 10, (240, 160, 60), "erva", "Restaura 30 de vida e 10 de energia.", 3, 2),
    "Poção Maior de Vida": _cura(70, 0, (235, 30, 80), "pocao", "Restaura 70 de vida.", 3, 2),
    "Poção Maior de Energia": _cura(0, 30, (40, 110, 255), "pocao", "Restaura 30 de energia (PE).", 3, 2),
    "Poção Suprema": _cura(120, 30, (255, 215, 90), "pocao", "Restaura 120 de vida e 30 de energia.", 1, 3),
    # ---- armas (força)
    "Adaga Afiada": _equip("arma", 3, (200, 200, 210), "Arma. +3 de força.", 4, 1),
    "Espada de Ferro": _equip("arma", 5, (190, 190, 205), "Arma. +5 de força.", 3, 1),
    "Machado de Guerra": _equip("arma", 7, (170, 130, 100), "Arma. +7 de força.", 2, 2),
    "Espada de Aço": _equip("arma", 9, (150, 190, 230), "Arma. +9 de força.", 2, 2),
    "Cimitarra do Deserto": _equip("arma", 12, (240, 210, 120), "Arma. +12 de força.", 2, 3),
    "Lança Sagrada": _equip("arma", 14, (255, 240, 170), "Arma. +14 de força.", 1, 3),
    "Lâmina Infernal": _equip("arma", 17, (230, 70, 40), "Arma. +17 de força.", 1, 3),
    # ---- escudos (defesa)
    "Escudo de Madeira": _equip("escudo", 4, (150, 100, 50), "Escudo. +4 de defesa.", 4, 1),
    "Escudo de Ferro": _equip("escudo", 7, (160, 165, 180), "Escudo. +7 de defesa.", 3, 1),
    "Escudo de Aço": _equip("escudo", 10, (150, 190, 230), "Escudo. +10 de defesa.", 2, 2),
    "Escudo Sagrado": _equip("escudo", 13, (255, 235, 150), "Escudo. +13 de defesa.", 1, 3),
    # ---- armaduras (defesa)
    "Túnica de Couro": _equip("armadura", 3, (160, 110, 70), "Armadura. +3 de defesa.", 4, 1),
    "Cota de Malha": _equip("armadura", 6, (170, 175, 190), "Armadura. +6 de defesa.", 3, 1),
    "Armadura de Escamas": _equip("armadura", 8, (90, 170, 120), "Armadura. +8 de defesa.", 2, 2),
    "Armadura de Placas": _equip("armadura", 11, (190, 200, 220), "Armadura. +11 de defesa.", 2, 3),
    "Armadura Sagrada": _equip("armadura", 15, (255, 235, 150), "Armadura. +15 de defesa.", 1, 3),
}


def _sortear(nomes):
    if not nomes:
        return "Bandagem"
    return random.choices(nomes, weights=[ITENS[n]["raridade"] for n in nomes])[0]


def sortear_item(tier_max=3, tier_min=1):
    """Item qualquer (usado nos baús)."""
    return _sortear([n for n, i in ITENS.items() if tier_min <= i["tier"] <= tier_max])


def sortear_consumivel(tier_max=3, tier_min=1):
    """Somente consumíveis (itens do chão e drops de inimigos)."""
    return _sortear([n for n, i in ITENS.items()
                     if i["tipo"] == "consumivel" and tier_min <= i["tier"] <= tier_max])


# ----------------------------------------------------------- INVENTÁRIO
def garantir_equipamento(j):
    """Garante que o personagem tenha todos os campos de equipamento válidos.
    Corrige personagens antigos (sem escudo/armadura) e itens que não existem mais."""
    eq = j.get("equipamento")
    if not isinstance(eq, dict):
        eq = {}
    j["equipamento"] = eq
    for slot in SLOTS:
        nome = eq.get(slot)
        info = ITENS.get(nome) if nome else None
        if info is None or info.get("tipo") != "equipamento" or info.get("slot") != slot:
            eq[slot] = None
    for slot in [s for s in eq if s not in SLOTS]:
        del eq[slot]
    inv = j.get("inventario")
    if not isinstance(inv, dict):
        inv = {}
    j["inventario"] = {n: int(q) for n, q in inv.items() if n in ITENS and isinstance(q, (int, float)) and q > 0}
    # catálogo de itens descobertos (tudo que já está na mochila ou equipado conta como descoberto)
    desc = j.get("descobertos")
    desc = set(desc) if isinstance(desc, list) else set()
    desc |= set(j["inventario"]) | {n for n in eq.values() if n}
    j["descobertos"] = sorted(n for n in desc if n in ITENS)
    return j


def adicionar_item(jogador, nome, qtd=1):
    inv = jogador.setdefault("inventario", {})
    inv[nome] = inv.get(nome, 0) + qtd
    desc = jogador.setdefault("descobertos", [])
    if nome in ITENS and nome not in desc:
        desc.append(nome)


def remover_item(jogador, nome, qtd=1):
    inv = jogador.setdefault("inventario", {})
    inv[nome] = inv.get(nome, 0) - qtd
    if inv[nome] <= 0:
        del inv[nome]


def consumiveis(jogador):
    """Lista de consumíveis que o personagem possui."""
    return sorted(n for n, q in jogador.get("inventario", {}).items()
                  if q > 0 and n in ITENS and ITENS[n]["tipo"] == "consumivel")


def total_cura(jogador):
    """Quantidade de itens que restauram vida."""
    return sum(q for n, q in jogador.get("inventario", {}).items()
               if n in ITENS and ITENS[n]["tipo"] == "consumivel" and ITENS[n]["vida"] > 0)


def melhor_cura(jogador):
    """Escolhe o item de vida que melhor se encaixa no que falta (evita desperdício)."""
    falta = jogador["vida_maxima"] - jogador["vida"]
    opcoes = [(ITENS[n]["vida"], n) for n in consumiveis(jogador) if ITENS[n]["vida"] > 0]
    if not opcoes or falta <= 0:
        return None
    suficientes = sorted(o for o in opcoes if o[0] >= falta)
    return suficientes[0][1] if suficientes else max(opcoes)[1]


def bonus(f, slot):
    nome = (f.get("equipamento") or {}).get(slot)
    info = ITENS.get(nome) if nome else None
    return info["bonus"] if info else 0


def forca_total(f):
    return f["forca"] + bonus(f, "arma")


def defesa_total(f):
    return f["defesa"] + bonus(f, "escudo") + bonus(f, "armadura")


def usar_item(jogador, nome):
    """Usa um consumível ou equipa um equipamento. Retorna (sucesso, mensagem)."""
    garantir_equipamento(jogador)
    if jogador["inventario"].get(nome, 0) <= 0:
        return False, "Você não tem esse item."
    item = ITENS.get(nome)
    if item is None:
        return False, "Esse item não existe mais."

    if item["tipo"] == "consumivel":
        ganho_vida, ganho_en = item["vida"], item["energia"]
        falta_vida = jogador["vida_maxima"] - jogador["vida"]
        falta_en = jogador["energia_maxima"] - jogador["energia"]
        util_vida = ganho_vida > 0 and falta_vida > 0
        util_en = ganho_en > 0 and falta_en > 0
        if not (util_vida or util_en):
            return False, "Não é necessário usar isso agora."
        curado = min(ganho_vida, falta_vida) if ganho_vida else 0
        recuperado = min(ganho_en, falta_en) if ganho_en else 0
        jogador["vida"] += curado
        jogador["energia"] += recuperado
        remover_item(jogador, nome)
        partes = []
        if ganho_vida:
            partes.append(f"+{curado} vida")
        if ganho_en:
            partes.append(f"+{recuperado} PE")
        return True, f'{nome} ({", ".join(partes)})'

    # equipamento: o item antigo volta para a mochila
    slot = item["slot"]
    atual = jogador["equipamento"].get(slot)
    remover_item(jogador, nome)
    if atual and atual in ITENS:
        adicionar_item(jogador, atual)
    jogador["equipamento"][slot] = nome
    return True, f"Equipou {nome}"


def tela_inventario(tela, jogador, fundo=None, apenas_consumiveis=False):
    """Tela de inventário. Com apenas_consumiveis=True (usada no combate), fecha ao usar
    um item e retorna a mensagem; ESC cancela e retorna None."""
    garantir_equipamento(jogador)
    relogio = pygame.time.Clock()
    sel = 0
    aviso = ""
    pygame.event.clear(pygame.KEYDOWN)
    def listar():
        return sorted(n for n, q in jogador["inventario"].items()
                      if q > 0 and n in ITENS and (not apenas_consumiveis or ITENS[n]["tipo"] == "consumivel"))

    while True:
        nomes = listar()
        sel = max(0, min(sel, len(nomes) - 1))
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                ui.sair()
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_ESCAPE, pygame.K_i):
                    return None
                elif nomes and ev.key in (pygame.K_UP, pygame.K_w):
                    sel = (sel - 1) % len(nomes)
                elif nomes and ev.key in (pygame.K_DOWN, pygame.K_s):
                    sel = (sel + 1) % len(nomes)
                elif nomes and ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    ok, msg = usar_item(jogador, nomes[sel])
                    aviso = msg
                    if ok:
                        salvar.salvar(jogador)
                    if ok and apenas_consumiveis:
                        return msg
                    # o item usado pode ter acabado: refaz a lista antes de desenhar
                    nomes = listar()
                    sel = max(0, min(sel, len(nomes) - 1))

        (fundo or ui.fundo_reino)(tela)
        ui.painel(tela, (110, 60, 740, 520))
        ui.texto(tela, "INVENTÁRIO", 480, 74, 30, ui.OURO, True, "centro")

        # lista (esquerda)
        topo = max(0, min(sel - 4, len(nomes) - 9))
        y = 130
        if not nomes:
            ui.texto(tela, "Nenhum item.", 140, y, 22, ui.CINZA)
        for i in range(topo, min(len(nomes), topo + 9)):
            nome = nomes[i]
            item = ITENS[nome]
            if i == sel:
                pygame.draw.rect(tela, (70, 60, 110), (130, y - 4, 330, 36), border_radius=6)
            pygame.draw.rect(tela, item["cor"], (140, y + 2, 22, 22), border_radius=4)
            pygame.draw.rect(tela, (230, 230, 230), (140, y + 2, 22, 22), 1, border_radius=4)
            ui.texto(tela, nome, 172, y, 20, ui.OURO if i == sel else ui.BRANCO)
            ui.texto(tela, f'x{jogador["inventario"].get(nome, 0)}', 450, y, 20, ui.CINZA, False, "dir")
            y += 40

        # detalhes (direita)
        ui.texto(tela, "Equipado", 490, 118, 20, ui.OURO, True)
        for k, slot in enumerate(SLOTS):
            ui.texto(tela, f'{ROTULO_SLOT[slot]}: {jogador["equipamento"].get(slot) or "nenhum"}',
                     490, 144 + k * 22, 17)
        ui.texto(tela, f'Vida: {jogador["vida"]}/{jogador["vida_maxima"]}', 490, 222, 18, ui.VERMELHO)
        ui.texto(tela, f'Energia: {jogador["energia"]}/{jogador["energia_maxima"]}', 490, 244, 18, ui.AZUL)
        ui.texto(tela, f"Força: {forca_total(jogador)}   Defesa: {defesa_total(jogador)}", 490, 266, 18)
        if nomes:
            item = ITENS[nomes[sel]]
            ui.texto(tela, nomes[sel], 490, 310, 22, item["cor"], True)
            for k, linha in enumerate(ui.quebrar_texto(item["desc"], 18, 330)):
                ui.texto(tela, linha, 490, 342 + k * 24, 18)
            acao = "usar" if item["tipo"] == "consumivel" else "equipar"
            ui.texto(tela, f"ENTER para {acao}", 490, 410, 17, ui.CINZA)
        if aviso:
            for k, linha in enumerate(ui.quebrar_texto(aviso, 18, 340)):
                ui.texto(tela, linha, 490, 450 + k * 22, 18, ui.VERDE)
        ui.texto(tela, "W/S escolher   ENTER confirmar   ESC voltar", 480, 548, 16, ui.CINZA, False, "centro")
        pygame.display.flip()
        relogio.tick(60)


# ------------------------------------------------------ CATÁLOGO DE ITENS
# peso de sorteio -> (nome da raridade, cor)
RARIDADES = {
    8: ("Comum", (190, 190, 190)), 6: ("Comum", (190, 190, 190)),
    5: ("Incomum", (110, 210, 120)), 4: ("Incomum", (110, 210, 120)),
    3: ("Raro", (90, 160, 245)),
    2: ("Épico", (190, 110, 235)),
    1: ("Lendário", (255, 190, 60)),
}
ONDE_TIER = {1: "Floresta, Savana e Deserto", 2: "Savana e Deserto", 3: "Somente no Deserto"}
CATEGORIAS = (
    ("Armas", lambda i: i["tipo"] == "equipamento" and i["slot"] == "arma"),
    ("Armaduras", lambda i: i["tipo"] == "equipamento" and i["slot"] == "armadura"),
    ("Escudos", lambda i: i["tipo"] == "equipamento" and i["slot"] == "escudo"),
    ("Poções e curas", lambda i: i["tipo"] == "consumivel"),
)


def raridade(nome):
    return RARIDADES.get(ITENS[nome]["raridade"], ("Comum", (190, 190, 190)))


def tela_catalogo(tela, jogador, fundo=None):
    """Bestiário de itens: só mostra os detalhes dos itens já descobertos."""
    garantir_equipamento(jogador)
    relogio = pygame.time.Clock()
    cat, sel = 0, 0
    pygame.event.clear(pygame.KEYDOWN)

    def itens_da(c):
        teste = CATEGORIAS[c][1]
        # ordena do mais comum para o mais raro
        return sorted((n for n, i in ITENS.items() if teste(i)), key=lambda n: (-ITENS[n]["raridade"], ITENS[n]["tier"], n))

    while True:
        lista = itens_da(cat)
        sel = max(0, min(sel, len(lista) - 1))
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                ui.sair()
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_b):
                    return
                elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                    cat, sel = (cat + 1) % len(CATEGORIAS), 0
                elif ev.key in (pygame.K_LEFT, pygame.K_a):
                    cat, sel = (cat - 1) % len(CATEGORIAS), 0
                elif ev.key in (pygame.K_UP, pygame.K_w):
                    sel = (sel - 1) % len(lista)
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    sel = (sel + 1) % len(lista)
        lista = itens_da(cat)
        sel = max(0, min(sel, len(lista) - 1))
        achados = set(jogador.get("descobertos", []))

        (fundo or ui.fundo_reino)(tela)
        ui.painel(tela, (60, 30, 840, 580))
        ui.texto(tela, "BESTIÁRIO DE ITENS", 480, 42, 30, ui.OURO, True, "centro")
        total = sum(1 for n in ITENS if n in achados)
        ui.texto(tela, f"Descobertos: {total}/{len(ITENS)}", 880, 50, 17, ui.CINZA, False, "dir")

        # abas
        x = 90
        for c, (rotulo, _) in enumerate(CATEGORIAS):
            ativo = c == cat
            larg = 180
            pygame.draw.rect(tela, (70, 60, 110) if ativo else (35, 35, 55), (x, 90, larg, 32), border_radius=6)
            ui.texto(tela, rotulo, x + larg // 2, 96, 18, ui.OURO if ativo else ui.CINZA, ativo, "centro")
            x += larg + 12

        # lista (esquerda)
        y = 140
        for i, nome in enumerate(lista):
            achou = nome in achados
            if i == sel:
                pygame.draw.rect(tela, (70, 60, 110), (80, y - 4, 400, 36), border_radius=6)
            cor_item = ITENS[nome]["cor"] if achou else (60, 60, 70)
            pygame.draw.rect(tela, cor_item, (92, y + 2, 22, 22), border_radius=4)
            pygame.draw.rect(tela, (230, 230, 230) if achou else (90, 90, 100), (92, y + 2, 22, 22), 1, border_radius=4)
            if achou:
                ui.texto(tela, nome, 126, y, 20, ui.OURO if i == sel else ui.BRANCO)
                rar, cor_rar = raridade(nome)
                ui.texto(tela, rar, 468, y + 2, 16, cor_rar, True, "dir")
            else:
                ui.texto(tela, "???", 126, y, 20, ui.CINZA)
            y += 40
        found_cat = sum(1 for n in lista if n in achados)
        ui.texto(tela, f"{CATEGORIAS[cat][0]}: {found_cat}/{len(lista)}", 90, 540, 17, ui.CINZA)

        # detalhes (direita)
        nome = lista[sel]
        info = ITENS[nome]
        pygame.draw.rect(tela, (45, 45, 65), (510, 140, 370, 380), border_radius=8)
        if nome in achados:
            rar, cor_rar = raridade(nome)
            pygame.draw.rect(tela, info["cor"], (530, 160, 56, 56), border_radius=8)
            pygame.draw.rect(tela, (230, 230, 230), (530, 160, 56, 56), 2, border_radius=8)
            ui.texto(tela, nome, 602, 162, 22, ui.OURO, True)
            ui.texto(tela, rar, 602, 192, 19, cor_rar, True)
            for k, linha in enumerate(ui.quebrar_texto(info["desc"], 18, 330)):
                ui.texto(tela, linha, 530, 240 + k * 24, 18)
            peso = info["raridade"]
            ui.texto(tela, f"Raridade de loot: {rar}", 530, 306, 18, cor_rar)
            ui.texto(tela, f"Peso de sorteio: {peso} (quanto menor, mais raro)", 530, 332, 16, ui.CINZA)
            ui.texto(tela, "Aparece em baús e drops de:", 530, 372, 17, ui.BRANCO)
            ui.texto(tela, ONDE_TIER[info["tier"]], 530, 396, 18, ui.VERDE, True)
            if info["tipo"] == "equipamento":
                ui.texto(tela, "Equipamento" , 530, 442, 17, ui.CINZA)
            else:
                ui.texto(tela, "Consumível", 530, 442, 17, ui.CINZA)
        else:
            pygame.draw.rect(tela, (60, 60, 70), (530, 160, 56, 56), border_radius=8)
            ui.texto(tela, "???", 602, 162, 22, ui.CINZA, True)
            ui.texto(tela, "Item ainda não descoberto", 530, 240, 18, ui.CINZA)
            ui.texto(tela, "Encontre-o em baús, no chão", 530, 270, 17, ui.CINZA)
            ui.texto(tela, "ou como drop de inimigos.", 530, 292, 17, ui.CINZA)
        ui.texto(tela, "← → trocar de categoria     W/S escolher     ESC voltar", 480, 578, 16, ui.CINZA, False, "centro")
        pygame.display.flip()
        relogio.tick(60)
