"""Funções de interface (menus, textos, barras e painéis) usadas pelo jogo."""
import random
import sys

import pygame

LARGURA, ALTURA = 960, 640

BRANCO = (240, 240, 240)
CINZA = (150, 150, 160)
OURO = (235, 200, 90)
VERMELHO = (225, 80, 80)
VERDE = (100, 205, 120)
AZUL = (90, 160, 245)
ROXO = (170, 110, 230)

_fontes = {}
_fundo_cache = None


def sair():
    pygame.quit()
    sys.exit()


def fonte(tam, negrito=False):
    chave = (tam, negrito)
    if chave not in _fontes:
        _fontes[chave] = pygame.font.SysFont("arial,segoeui,dejavusans", tam, bold=negrito)
    return _fontes[chave]


def texto(tela, msg, x, y, tam=20, cor=BRANCO, negrito=False, alinhar="esq"):
    """Desenha um texto. alinhar: 'esq', 'centro' ou 'dir'."""
    img = fonte(tam, negrito).render(str(msg), True, cor)
    ret = img.get_rect()
    if alinhar == "centro":
        ret.midtop = (x, y)
    elif alinhar == "dir":
        ret.topright = (x, y)
    else:
        ret.topleft = (x, y)
    tela.blit(img, ret)
    return ret


def quebrar_texto(msg, tam, largura):
    """Quebra um texto em linhas que cabem na largura (em pixels)."""
    f = fonte(tam)
    linhas, atual = [], ""
    for palavra in str(msg).split():
        teste = (atual + " " + palavra).strip()
        if f.size(teste)[0] <= largura:
            atual = teste
        else:
            if atual:
                linhas.append(atual)
            atual = palavra
    if atual:
        linhas.append(atual)
    return linhas or [""]


def painel(tela, rect, cor=(20, 20, 32), borda=OURO, alpha=225):
    x, y, w, h = rect
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill((cor[0], cor[1], cor[2], alpha))
    tela.blit(s, (x, y))
    pygame.draw.rect(tela, borda, rect, 2, border_radius=6)


def barra(tela, x, y, w, h, valor, maximo, cor, rotulo=None):
    pygame.draw.rect(tela, (45, 45, 55), (x, y, w, h), border_radius=4)
    if maximo > 0 and valor > 0:
        largura = max(2, int(w * min(valor, maximo) / maximo))
        pygame.draw.rect(tela, cor, (x, y, largura, h), border_radius=4)
    pygame.draw.rect(tela, (225, 225, 230), (x, y, w, h), 1, border_radius=4)
    if rotulo:
        texto(tela, rotulo, x + w // 2, y + max(0, (h - 15) // 2), 13, BRANCO, True, "centro")


def fundo_reino(tela):
    """Fundo noturno com castelo, usado nos menus."""
    global _fundo_cache
    if _fundo_cache is None:
        s = pygame.Surface((LARGURA, ALTURA))
        for y in range(ALTURA):
            t = y / ALTURA
            pygame.draw.line(s, (int(15 + 60 * t), int(20 + 40 * t), int(50 + 70 * t)), (0, y), (LARGURA, y))
        rng = random.Random(5)
        for _ in range(90):
            c = rng.randint(150, 255)
            pygame.draw.circle(s, (c, c, c), (rng.randint(0, LARGURA), rng.randint(0, 330)), rng.choice((1, 1, 2)))
        pygame.draw.circle(s, (240, 235, 200), (800, 110), 38)
        pygame.draw.polygon(s, (30, 40, 70), [(0, 520), (140, 390), (260, 470), (400, 350), (560, 480),
                                              (700, 390), (860, 470), (960, 410), (960, 640), (0, 640)])
        cor = (16, 20, 38)
        pygame.draw.rect(s, cor, (420, 400, 120, 130))
        pygame.draw.rect(s, cor, (400, 350, 32, 180))
        pygame.draw.rect(s, cor, (528, 350, 32, 180))
        pygame.draw.rect(s, cor, (452, 320, 56, 210))
        for tx in (400, 528, 452):
            larg = 56 if tx == 452 else 32
            for i in range(0, larg, 12):
                pygame.draw.rect(s, cor, (tx + i, (320 if tx == 452 else 338), 7, 14))
        for jx, jy in ((470, 350), (486, 350), (410, 380), (538, 380), (470, 430), (500, 430)):
            pygame.draw.rect(s, (240, 200, 90), (jx, jy, 6, 12))
        pygame.draw.rect(s, (12, 26, 28), (0, 530, LARGURA, 110))
        _fundo_cache = s
    tela.blit(_fundo_cache, (0, 0))


def _tecla_enter(tecla):
    return tecla in (pygame.K_RETURN, pygame.K_KP_ENTER)


def menu_vertical(tela, titulo, opcoes, fundo=None, subtitulo=None, permitir_esc=True, rodape=None):
    """Mostra um menu. Retorna o índice escolhido (ou None se apertar ESC)."""
    relogio = pygame.time.Clock()
    sel = 0
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                sair()
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_UP, pygame.K_w):
                    sel = (sel - 1) % len(opcoes)
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    sel = (sel + 1) % len(opcoes)
                elif _tecla_enter(ev.key) or ev.key == pygame.K_SPACE:
                    return sel
                elif ev.key == pygame.K_ESCAPE and permitir_esc:
                    return None
                elif pygame.K_1 <= ev.key <= pygame.K_9:
                    idx = ev.key - pygame.K_1
                    if idx < len(opcoes):
                        return idx
        (fundo or fundo_reino)(tela)
        largura = 540
        altura = 110 + 46 * len(opcoes) + (28 if subtitulo else 0)
        x = (LARGURA - largura) // 2
        y = (ALTURA - altura) // 2
        painel(tela, (x, y, largura, altura))
        texto(tela, titulo, LARGURA // 2, y + 16, 32, OURO, True, "centro")
        yy = y + 68
        if subtitulo:
            texto(tela, subtitulo, LARGURA // 2, yy - 4, 18, CINZA, False, "centro")
            yy += 28
        for i, op in enumerate(opcoes):
            ativo = i == sel
            if ativo:
                pygame.draw.rect(tela, (70, 60, 110), (x + 20, yy - 4, largura - 40, 38), border_radius=6)
            texto(tela, f"{i + 1} - {op}", x + 40, yy, 24, OURO if ativo else BRANCO)
            yy += 46
        if rodape:
            texto(tela, rodape, LARGURA // 2, ALTURA - 36, 17, CINZA, False, "centro")
        pygame.display.flip()
        relogio.tick(60)


def entrada_texto(tela, pergunta, padrao="", limite=16):
    """Pede um texto digitado na própria janela."""
    relogio = pygame.time.Clock()
    valor = ""
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                sair()
            if ev.type == pygame.KEYDOWN:
                if _tecla_enter(ev.key):
                    return valor.strip() or padrao
                elif ev.key == pygame.K_BACKSPACE:
                    valor = valor[:-1]
                elif ev.unicode and ev.unicode.isprintable() and len(valor) < limite:
                    valor += ev.unicode
        fundo_reino(tela)
        painel(tela, (180, 210, 600, 220))
        texto(tela, "CRÔNICAS DE UM REINO", LARGURA // 2, 228, 34, OURO, True, "centro")
        texto(tela, pergunta, LARGURA // 2, 290, 21, BRANCO, False, "centro")
        pygame.draw.rect(tela, (10, 10, 20), (280, 332, 400, 44), border_radius=6)
        pygame.draw.rect(tela, OURO, (280, 332, 400, 44), 2, border_radius=6)
        cursor = "|" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
        texto(tela, valor + cursor, 294, 340, 26)
        texto(tela, f"ENTER para confirmar (padrão: {padrao})" if padrao else "ENTER para confirmar",
              LARGURA // 2, 392, 16, CINZA, False, "centro")
        pygame.display.flip()
        relogio.tick(60)


def mensagem(tela, titulo, linhas, fundo=None, cor_titulo=OURO):
    """Mostra uma caixa de texto e espera ENTER/ESPAÇO/ESC."""
    relogio = pygame.time.Clock()
    todas = []
    for linha in linhas:
        todas.extend(quebrar_texto(linha, 22, 540))
    altura = 120 + 28 * len(todas)
    pygame.event.clear(pygame.KEYDOWN)
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                sair()
            if ev.type == pygame.KEYDOWN and (_tecla_enter(ev.key) or ev.key in (pygame.K_SPACE, pygame.K_ESCAPE)):
                return
            if ev.type == pygame.MOUSEBUTTONDOWN:
                return
        (fundo or fundo_reino)(tela)
        x = (LARGURA - 620) // 2
        y = (ALTURA - altura) // 2
        painel(tela, (x, y, 620, altura))
        texto(tela, titulo, LARGURA // 2, y + 16, 30, cor_titulo, True, "centro")
        for i, linha in enumerate(todas):
            texto(tela, linha, LARGURA // 2, y + 66 + i * 28, 22, BRANCO, False, "centro")
        texto(tela, "ENTER para continuar", LARGURA // 2, y + altura - 32, 16, CINZA, False, "centro")
        pygame.display.flip()
        relogio.tick(60)
