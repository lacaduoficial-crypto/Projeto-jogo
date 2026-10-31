"""Combate por turnos (contra inimigos e duelo entre dois jogadores)."""
import random

import pygame

from sistemas import graficos, itens, personagem, ui

CUSTO_ESPECIAL = 10
_fundo_cache = None


# ------------------------------------------------------------ REGRAS DE DANO
def calcular_dano(a, d, mult=1.0, ignora_defesa=False, forcar_critico=False):
    forca = itens.forca_total(a)
    defesa = 0 if ignora_defesa else itens.defesa_total(d)
    dano = forca * random.uniform(0.85, 1.15) * mult - defesa * 0.5
    critico = forcar_critico or random.random() < 0.10
    if critico:
        dano *= 1.5
    if d.get("defendendo"):
        dano *= 0.5
    return max(1, int(round(dano))), critico


def acao_atacar(a, d):
    dano, crit = calcular_dano(a, d)
    d["vida"] = max(0, d["vida"] - dano)
    msg = f'{a["nome"]} ataca {d["nome"]} e causa {dano} de dano.'
    if crit:
        msg += " Acerto crítico!"
    return msg, dano


def acao_especial(a, d):
    """Habilidade especial (custa 10 PE). Cada tipo de inimigo tem a sua."""
    a["energia"] -= CUSTO_ESPECIAL
    tipo = a.get("especial_tipo", "poderoso")
    nome = a.get("especial", "Golpe Poderoso")
    cura = 0
    if tipo == "critico":
        dano, crit = calcular_dano(a, d, 1.3, forcar_critico=random.random() < 0.5)
    elif tipo == "perfurante":
        dano, crit = calcular_dano(a, d, 1.2, ignora_defesa=True)
    elif tipo == "vampirico":
        dano, crit = calcular_dano(a, d, 1.2)
    else:
        dano, crit = calcular_dano(a, d, a.get("especial_mult", 1.8))
    d["vida"] = max(0, d["vida"] - dano)
    msg = f'{a["nome"]} usa {nome} e causa {dano} de dano.'
    if crit:
        msg += " Acerto crítico!"
    if tipo == "vampirico":
        cura = min(dano // 2, a["vida_maxima"] - a["vida"])
        a["vida"] += cura
        if cura:
            msg += f" Recupera {cura} de vida."
    return msg, dano


def acao_defender(a):
    a["defendendo"] = True
    rec = min(3, a["energia_maxima"] - a["energia"])
    a["energia"] += rec
    msg = f'{a["nome"]} assume postura defensiva'
    return msg + (f" e recupera {rec} PE." if rec else ".")


# ------------------------------------------------------------------- CENA
def _fundo_batalha():
    global _fundo_cache
    if _fundo_cache is None:
        s = pygame.Surface((ui.LARGURA, ui.ALTURA))
        for y in range(330):
            t = y / 330
            pygame.draw.line(s, (int(90 + 100 * t), int(150 + 75 * t), int(220 + 20 * t)), (0, y), (ui.LARGURA, y))
        rng = random.Random(3)
        for x in range(-20, ui.LARGURA, 46):
            h = rng.randint(50, 90)
            pygame.draw.rect(s, (80, 55, 30), (x + 18, 330 - h // 3, 8, h // 3))
            pygame.draw.circle(s, (35, 100, 50), (x + 22, 330 - h // 2), h // 2)
        for y in range(330, 400):
            t = (y - 330) / 70
            pygame.draw.line(s, (int(90 - 30 * t), int(170 - 40 * t), int(80 - 20 * t)), (0, y), (ui.LARGURA, y))
        pygame.draw.rect(s, (25, 25, 35), (0, 400, ui.LARGURA, ui.ALTURA - 400))
        _fundo_cache = s
    return _fundo_cache


class Cena:
    """Tela de batalha: desenha os lutadores, caixas de status, log e menu."""

    def __init__(self, tela, esq, dir_, spr_esq, spr_dir):
        self.tela = tela
        self.esq = esq
        self.dir = dir_
        self.spr_esq = spr_esq
        self.spr_dir = pygame.transform.flip(spr_dir, True, False)
        self.log = []
        self.ativo = None
        self.tremer = None
        self.tremer_ate = 0
        self.flutuante = None

    def registrar(self, msg):
        self.log.append(msg)
        self.log = self.log[-5:]

    def lado(self, f):
        return "esq" if f is self.esq else "dir"

    def _caixa(self, tela, f, x, y):
        ativo = f is self.ativo
        ui.painel(tela, (x, y, 300, 88), borda=ui.OURO if ativo else (110, 100, 140))
        ui.texto(tela, f["nome"], x + 12, y + 8, 20, ui.BRANCO, True)
        if "nivel" in f:
            ui.texto(tela, f'Nv {f["nivel"]}', x + 288, y + 10, 16, ui.OURO, False, "dir")
        ui.barra(tela, x + 12, y + 38, 276, 16, f["vida"], f["vida_maxima"], (200, 60, 60),
                 f'PV {f["vida"]}/{f["vida_maxima"]}')
        ui.barra(tela, x + 12, y + 62, 276, 14, f["energia"], f["energia_maxima"], (70, 130, 230),
                 f'PE {f["energia"]}/{f["energia_maxima"]}')

    def desenhar(self, tela=None, menu=None, sel=0, titulo=""):
        tela = tela or self.tela
        tela.blit(_fundo_batalha(), (0, 0))
        agora = pygame.time.get_ticks()
        for lado, spr, bx in (("esq", self.spr_esq, 150), ("dir", self.spr_dir, 650)):
            ox = 0
            if self.tremer == lado and agora < self.tremer_ate:
                ox = random.randint(-8, 8)
            pygame.draw.ellipse(tela, (35, 80, 40), (bx + 10, 352, 140, 26))
            tela.blit(spr, (bx + ox, 205))
        self._caixa(tela, self.esq, 20, 20)
        self._caixa(tela, self.dir, 640, 20)

        if self.flutuante and agora < self.flutuante[3]:
            lado, txt, cor, ate = self.flutuante
            progresso = 1 - (ate - agora) / 900
            ui.texto(tela, txt, 230 if lado == "esq" else 730, 185 - int(progresso * 45), 38, cor, True, "centro")

        # log
        ui.painel(tela, (10, 410, 520, 220))
        linhas = []
        for msg in self.log:
            linhas.extend(ui.quebrar_texto(msg, 19, 490))
        for i, linha in enumerate(linhas[-7:]):
            ui.texto(tela, linha, 24, 424 + i * 28, 19)

        # menu
        ui.painel(tela, (540, 410, 410, 220))
        if titulo:
            ui.texto(tela, titulo, 560, 420, 20, ui.OURO, True)
        if menu:
            for i, (rotulo, ativo) in enumerate(menu):
                yy = 454 + i * 34
                if i == sel:
                    pygame.draw.rect(tela, (70, 60, 110), (554, yy - 3, 382, 31), border_radius=6)
                cor = (ui.OURO if i == sel else ui.BRANCO) if ativo else (100, 100, 110)
                ui.texto(tela, f"{i + 1} - {rotulo}", 570, yy, 20, cor)

    def desenhar_fundo(self, tela):
        self.desenhar(tela)

    def pausa(self, ms):
        fim = pygame.time.get_ticks() + ms
        relogio = pygame.time.Clock()
        while pygame.time.get_ticks() < fim:
            for _ in pygame.event.get(pygame.QUIT):
                ui.sair()
            self.desenhar()
            pygame.display.flip()
            relogio.tick(60)
        pygame.event.clear(pygame.KEYDOWN)

    def impacto(self, lado, txt, cor):
        agora = pygame.time.get_ticks()
        self.tremer = lado
        self.tremer_ate = agora + 400
        self.flutuante = (lado, txt, cor, agora + 900)
        self.pausa(900)

    def escolher(self, opcoes, titulo):
        """Mostra o menu de ações e retorna o índice escolhido."""
        sel = 0
        relogio = pygame.time.Clock()
        pygame.event.clear(pygame.KEYDOWN)
        while True:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    ui.sair()
                if ev.type == pygame.KEYDOWN:
                    if ev.key in (pygame.K_UP, pygame.K_w):
                        sel = (sel - 1) % len(opcoes)
                    elif ev.key in (pygame.K_DOWN, pygame.K_s):
                        sel = (sel + 1) % len(opcoes)
                    elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                        return sel
                    elif pygame.K_1 <= ev.key <= pygame.K_9 and ev.key - pygame.K_1 < len(opcoes):
                        return ev.key - pygame.K_1
            self.desenhar(menu=opcoes, sel=sel, titulo=titulo)
            pygame.display.flip()
            relogio.tick(60)


# ------------------------------------------------------------------ TURNOS
def executar_acao(cena, a, d, acao):
    if acao == "atacar":
        msg, dano = acao_atacar(a, d)
    elif acao == "especial":
        msg, dano = acao_especial(a, d)
    else:
        msg, dano = acao_defender(a), 0
    cena.registrar(msg)
    if dano > 0:
        cena.impacto(cena.lado(d), f"-{dano}", ui.VERMELHO)
    else:
        cena.pausa(800)


def turno_humano(cena, a, d, pode_fugir=True):
    """Turno de um jogador. Retorna 'ok' ou 'fuga'."""
    cena.ativo = a
    a["defendendo"] = False
    a["energia"] = min(a["energia_maxima"], a["energia"] + 2)
    while True:
        nome_esp = a.get("especial", "Golpe Poderoso")
        chaves = ["atacar", "especial", "defender", "item"]
        opcoes = [
            ("Ataque normal", True),
            (f"{nome_esp} ({CUSTO_ESPECIAL} PE)", a["energia"] >= CUSTO_ESPECIAL),
            ("Defender (+3 PE)", True),
            ("Usar item", bool(itens.consumiveis(a))),
        ]
        if pode_fugir:
            chaves.append("fugir")
            opcoes.append(("Fugir", True))
        idx = cena.escolher(opcoes, f'Turno de {a["nome"]}')
        chave, ativo = chaves[idx], opcoes[idx][1]
        if not ativo:
            cena.registrar("Energia insuficiente!" if chave == "especial" else "Você não tem itens de cura.")
            continue
        if chave in ("atacar", "especial", "defender"):
            executar_acao(cena, a, d, chave)
            return "ok"
        if chave == "item":
            msg = itens.tela_inventario(cena.tela, a, fundo=cena.desenhar_fundo, apenas_consumiveis=True)
            if msg is None:
                continue
            cena.registrar(f'{a["nome"]} usou {msg}.')
            cena.pausa(900)
            return "ok"
        if random.random() < 0.6:
            cena.registrar(f'{a["nome"]} conseguiu fugir!')
            cena.pausa(900)
            return "fuga"
        cena.registrar("Não conseguiu fugir!")
        cena.pausa(900)
        return "ok"


def turno_ia(cena, ia, alvo):
    cena.ativo = ia
    ia["defendendo"] = False
    ia["energia"] = min(ia["energia_maxima"], ia["energia"] + 2)
    r = random.random()
    if ia["vida"] < ia["vida_maxima"] * 0.3 and r < 0.25:
        acao = "defender"
    elif ia["energia"] >= CUSTO_ESPECIAL and r < 0.35:
        acao = "especial"
    else:
        acao = "atacar"
    cena.pausa(500)
    executar_acao(cena, ia, alvo, acao)


# ----------------------------------------------------------------- COMBATES
def combate(tela, jogador, inimigo, pode_fugir=True):
    """Luta contra um inimigo. Retorna 'vitoria', 'derrota' ou 'fuga'."""
    cena = Cena(tela, jogador, inimigo,
                graficos.obter_sprite("heroi", 160), graficos.obter_sprite(inimigo["tipo"], 160))
    jogador["defendendo"] = False
    cena.registrar(f'Um {inimigo["nome"]} apareceu!')
    cena.pausa(900)
    try:
        while True:
            if turno_humano(cena, jogador, inimigo, pode_fugir) == "fuga":
                return "fuga"
            if inimigo["vida"] <= 0:
                cena.registrar(f'{inimigo["nome"]} foi derrotado!')
                cena.pausa(1000)
                return "vitoria"
            turno_ia(cena, inimigo, jogador)
            if jogador["vida"] <= 0:
                cena.registrar(f'{jogador["nome"]} caiu em combate...')
                cena.pausa(1200)
                return "derrota"
    finally:
        jogador["defendendo"] = False


def _copia_duelista(j):
    c = dict(j)
    c["inventario"] = dict(j["inventario"])
    c["equipamento"] = dict(j["equipamento"])
    c["vida"], c["energia"] = c["vida_maxima"], c["energia_maxima"]
    c["defendendo"] = False
    return c


def duelo(tela, j1, j2):
    """Duelo amistoso entre dois jogadores no mesmo teclado (turnos alternados).
    Usa cópias dos personagens: ninguém perde vida, itens ou XP. Retorna o vencedor."""
    a, b = _copia_duelista(j1), _copia_duelista(j2)
    cena = Cena(tela, a, b, graficos.obter_sprite("heroi", 160, (60, 110, 200)),
                graficos.obter_sprite("heroi", 160, (190, 60, 60)))
    cena.registrar(f'Duelo: {a["nome"]} contra {b["nome"]}!')
    cena.pausa(1000)
    while True:
        turno_humano(cena, a, b, pode_fugir=False)
        if b["vida"] <= 0:
            cena.registrar(f'{a["nome"]} venceu!')
            cena.pausa(1200)
            return j1
        turno_humano(cena, b, a, pode_fugir=False)
        if a["vida"] <= 0:
            cena.registrar(f'{b["nome"]} venceu!')
            cena.pausa(1200)
            return j2


def tela_vitoria(tela, jogador, inimigo, fundo=None):
    """Concede XP e possível drop. Retorna as linhas mostradas."""
    xp = inimigo["experiencia"]
    linhas = [f'{jogador["nome"]} derrotou {inimigo["nome"]}!', f"Você recebeu {xp} XP!"]
    linhas += personagem.ganhar_xp(jogador, xp)
    if random.random() < 0.5:
        tier = inimigo.get("tier", 1)
        item = itens.sortear_consumivel(tier_max=tier, tier_min=1 if tier < 3 else 2)
        itens.adicionar_item(jogador, item)
        linhas.append(f"O inimigo deixou cair: {item}!")
    ui.mensagem(tela, "VITÓRIA!", linhas, fundo=fundo, cor_titulo=ui.VERDE)
    return linhas
