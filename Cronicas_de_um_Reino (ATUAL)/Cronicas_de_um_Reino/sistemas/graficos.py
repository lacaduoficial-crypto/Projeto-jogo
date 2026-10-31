"""Sprites e tiles 2D desenhados por código (não precisa de arquivos de imagem)."""
import random

import pygame

T = 32  # tamanho base de um quadrado (pixels)

_cache_sprites = {}
_cache_tiles = {}


def _r(s, cor, x, y, w, h):
    pygame.draw.rect(s, cor, (x, y, w, h))


def _escurecer(cor, n=40):
    return tuple(max(0, c - n) for c in cor)


# ----------------------------------------------------------------- SPRITES
def _heroi(s, cor):
    cor = cor or (60, 110, 200)
    pele = (240, 200, 160)
    _r(s, (60, 45, 35), 11, 25, 4, 6)
    _r(s, (60, 45, 35), 17, 25, 4, 6)
    _r(s, _escurecer(cor), 7, 15, 3, 9)
    _r(s, _escurecer(cor), 22, 15, 3, 9)
    _r(s, cor, 10, 14, 12, 11)
    _r(s, (90, 60, 30), 10, 21, 12, 2)
    _r(s, (230, 200, 80), 15, 21, 2, 2)
    _r(s, pele, 7, 23, 3, 2)
    _r(s, pele, 22, 23, 3, 2)
    _r(s, pele, 11, 5, 10, 9)
    _r(s, (95, 55, 25), 11, 3, 10, 4)
    _r(s, (95, 55, 25), 10, 4, 2, 6)
    _r(s, (30, 30, 40), 13, 9, 2, 2)
    _r(s, (30, 30, 40), 18, 9, 2, 2)
    _r(s, (210, 210, 225), 26, 6, 2, 16)
    _r(s, (230, 190, 60), 24, 21, 6, 2)
    _r(s, (110, 70, 30), 26, 23, 2, 3)
    _r(s, (150, 100, 50), 2, 15, 6, 9)
    _r(s, (230, 190, 60), 4, 17, 2, 5)


def _goblin(s, cor):
    pele = (90, 170, 70)
    _r(s, (70, 50, 30), 11, 25, 4, 6)
    _r(s, (70, 50, 30), 17, 25, 4, 6)
    _r(s, pele, 7, 17, 3, 7)
    _r(s, pele, 22, 17, 3, 7)
    _r(s, (110, 75, 40), 10, 16, 12, 9)
    _r(s, pele, 9, 6, 14, 10)
    pygame.draw.polygon(s, pele, [(9, 9), (2, 6), (9, 13)])
    pygame.draw.polygon(s, pele, [(23, 9), (30, 6), (23, 13)])
    _r(s, (230, 40, 40), 12, 9, 3, 3)
    _r(s, (230, 40, 40), 18, 9, 3, 3)
    _r(s, (40, 20, 20), 13, 13, 6, 2)
    _r(s, (240, 240, 230), 14, 13, 1, 1)
    _r(s, (240, 240, 230), 17, 13, 1, 1)
    _r(s, (120, 80, 40), 26, 10, 3, 14)
    _r(s, (100, 65, 30), 25, 7, 5, 5)


def _esqueleto(s, cor):
    osso = (235, 235, 220)
    _r(s, osso, 12, 24, 3, 7)
    _r(s, osso, 17, 24, 3, 7)
    _r(s, (40, 40, 50), 11, 14, 10, 10)
    for yy in (15, 18, 21):
        _r(s, osso, 11, yy, 10, 2)
    _r(s, osso, 15, 13, 2, 11)
    _r(s, osso, 8, 14, 2, 10)
    _r(s, osso, 22, 14, 2, 10)
    _r(s, osso, 10, 3, 12, 10)
    _r(s, osso, 12, 13, 8, 3)
    _r(s, (20, 20, 25), 12, 7, 3, 3)
    _r(s, (20, 20, 25), 17, 7, 3, 3)
    _r(s, (20, 20, 25), 15, 10, 2, 2)
    for xx in (13, 15, 17):
        _r(s, (30, 30, 35), xx, 14, 1, 2)
    _r(s, (170, 170, 185), 26, 10, 2, 13)
    _r(s, (120, 80, 40), 25, 22, 4, 2)


def _zumbi(s, cor):
    pele = (120, 150, 110)
    _r(s, (60, 60, 90), 11, 25, 4, 6)
    _r(s, (60, 60, 90), 17, 25, 4, 6)
    _r(s, (110, 70, 110), 10, 15, 12, 10)
    _r(s, pele, 14, 21, 3, 4)
    _r(s, pele, 2, 15, 9, 3)
    _r(s, pele, 21, 15, 9, 3)
    _r(s, pele, 11, 5, 10, 10)
    _r(s, (60, 70, 50), 12, 3, 4, 3)
    _r(s, (230, 230, 100), 13, 9, 2, 2)
    _r(s, (230, 230, 100), 18, 8, 3, 3)
    _r(s, (60, 20, 20), 14, 13, 5, 2)


def _bau(s, cor):
    _r(s, (140, 90, 40), 5, 14, 22, 13)
    _r(s, (170, 110, 50), 5, 9, 22, 7)
    _r(s, (210, 170, 60), 5, 17, 22, 2)
    _r(s, (235, 205, 80), 14, 16, 4, 5)
    pygame.draw.rect(s, (60, 40, 20), (5, 9, 22, 18), 1)


def _bau_aberto(s, cor):
    _r(s, (140, 90, 40), 5, 14, 22, 13)
    _r(s, (40, 25, 15), 6, 14, 20, 4)
    _r(s, (110, 70, 30), 5, 6, 22, 6)
    _r(s, (210, 170, 60), 5, 20, 22, 2)
    pygame.draw.rect(s, (60, 40, 20), (5, 6, 22, 21), 1)


def _pocao(s, cor):
    cor = cor or (220, 50, 70)
    _r(s, (150, 100, 60), 14, 5, 4, 3)
    _r(s, (200, 220, 235), 13, 8, 6, 6)
    pygame.draw.circle(s, cor, (16, 21), 8)
    pygame.draw.circle(s, (60, 60, 70), (16, 21), 8, 1)
    pygame.draw.circle(s, (255, 255, 255), (13, 18), 2)


def _erva(s, cor):
    pygame.draw.line(s, (50, 130, 60), (16, 28), (16, 14), 2)
    pygame.draw.ellipse(s, (70, 180, 80), (8, 10, 10, 6))
    pygame.draw.ellipse(s, (70, 180, 80), (15, 8, 10, 6))
    pygame.draw.ellipse(s, (100, 210, 100), (9, 17, 9, 5))
    pygame.draw.ellipse(s, (100, 210, 100), (15, 16, 9, 5))


def _cobra(s, cor):
    verde, claro = (70, 150, 60), (150, 200, 90)
    pygame.draw.ellipse(s, verde, (3, 22, 14, 7))
    pygame.draw.ellipse(s, verde, (12, 18, 16, 7))
    pygame.draw.ellipse(s, verde, (5, 13, 14, 7))
    _r(s, verde, 14, 5, 7, 11)
    _r(s, claro, 15, 17, 6, 2)
    _r(s, claro, 8, 24, 5, 2)
    _r(s, verde, 12, 3, 11, 6)
    _r(s, (240, 220, 40), 14, 5, 2, 2)
    _r(s, (240, 220, 40), 19, 5, 2, 2)
    _r(s, (20, 20, 20), 15, 5, 1, 2)
    _r(s, (20, 20, 20), 20, 5, 1, 2)
    _r(s, (220, 40, 50), 17, 9, 1, 4)
    _r(s, (220, 40, 50), 16, 12, 1, 2)
    _r(s, (220, 40, 50), 18, 12, 1, 2)


def _escorpiao(s, cor):
    corpo, escuro = (190, 120, 50), (130, 75, 30)
    for xx, yy in ((5, 17), (5, 21), (5, 25), (25, 17), (25, 21), (25, 25)):
        _r(s, escuro, xx, yy, 3, 2)
    pygame.draw.ellipse(s, corpo, (8, 15, 16, 14))
    pygame.draw.ellipse(s, escuro, (8, 15, 16, 14), 1)
    _r(s, escuro, 12, 18, 8, 1)
    _r(s, escuro, 12, 22, 8, 1)
    pygame.draw.ellipse(s, corpo, (1, 8, 8, 7))
    pygame.draw.ellipse(s, corpo, (23, 8, 8, 7))
    _r(s, escuro, 3, 9, 4, 2)
    _r(s, escuro, 25, 9, 4, 2)
    _r(s, corpo, 14, 9, 4, 7)
    _r(s, corpo, 12, 4, 7, 6)
    _r(s, corpo, 18, 1, 5, 5)
    _r(s, (220, 40, 40), 21, 1, 3, 3)
    _r(s, (20, 20, 20), 14, 11, 2, 2)
    _r(s, (20, 20, 20), 17, 11, 2, 2)


def _mumia(s, cor):
    faixa, sombra = (225, 215, 180), (170, 160, 125)
    _r(s, faixa, 11, 25, 4, 6)
    _r(s, faixa, 17, 25, 4, 6)
    _r(s, faixa, 10, 14, 12, 12)
    _r(s, faixa, 3, 15, 8, 3)
    _r(s, faixa, 21, 15, 8, 3)
    _r(s, faixa, 10, 3, 12, 11)
    for yy in (16, 19, 22):
        _r(s, sombra, 10, yy, 12, 1)
    for yy in (5, 8, 12):
        _r(s, sombra, 10, yy, 12, 1)
    _r(s, (20, 20, 20), 12, 7, 8, 3)
    _r(s, (230, 60, 50), 13, 8, 2, 1)
    _r(s, (230, 60, 50), 17, 8, 2, 1)
    _r(s, sombra, 6, 17, 1, 6)
    _r(s, sombra, 25, 18, 1, 5)


def _demonio(s, cor):
    pele, escuro = (190, 40, 40), (120, 20, 30)
    pygame.draw.polygon(s, escuro, [(8, 16), (0, 5), (12, 12)])
    pygame.draw.polygon(s, escuro, [(24, 16), (32, 5), (20, 12)])
    _r(s, escuro, 11, 25, 4, 6)
    _r(s, escuro, 17, 25, 4, 6)
    _r(s, pele, 9, 14, 14, 12)
    _r(s, pele, 4, 15, 6, 4)
    _r(s, pele, 22, 15, 6, 4)
    _r(s, pele, 10, 4, 12, 10)
    pygame.draw.polygon(s, (235, 225, 200), [(10, 5), (8, 0), (13, 4)])
    pygame.draw.polygon(s, (235, 225, 200), [(22, 5), (24, 0), (19, 4)])
    _r(s, (255, 230, 60), 12, 8, 3, 3)
    _r(s, (255, 230, 60), 18, 8, 3, 3)
    _r(s, (20, 10, 10), 13, 9, 1, 2)
    _r(s, (20, 10, 10), 19, 9, 1, 2)
    _r(s, (30, 10, 10), 13, 12, 7, 2)
    _r(s, (240, 240, 230), 14, 12, 1, 2)
    _r(s, (240, 240, 230), 18, 12, 1, 2)
    pygame.draw.line(s, (255, 150, 30), (3, 22), (3, 14), 2)
    pygame.draw.circle(s, (255, 190, 40), (3, 13), 3)


def _gorila(s, cor):
    pelo, claro = (50, 45, 55), (85, 75, 90)
    _r(s, pelo, 9, 25, 6, 6)
    _r(s, pelo, 17, 25, 6, 6)
    _r(s, pelo, 7, 13, 18, 13)
    _r(s, claro, 12, 16, 8, 8)
    _r(s, pelo, 1, 12, 7, 15)
    _r(s, pelo, 24, 12, 7, 15)
    _r(s, claro, 1, 25, 7, 4)
    _r(s, claro, 24, 25, 7, 4)
    _r(s, pelo, 9, 3, 14, 12)
    _r(s, pelo, 12, 1, 8, 3)
    _r(s, claro, 11, 7, 10, 8)
    _r(s, (230, 40, 40), 12, 8, 3, 2)
    _r(s, (230, 40, 40), 18, 8, 3, 2)
    _r(s, (20, 20, 25), 15, 11, 2, 2)
    _r(s, (240, 240, 230), 13, 13, 1, 2)
    _r(s, (240, 240, 230), 18, 13, 1, 2)
    _r(s, (80, 255, 90), 8, 14, 2, 2)      # mutação (brilho verde)
    _r(s, (80, 255, 90), 22, 18, 2, 2)
    _r(s, (80, 255, 90), 12, 27, 2, 2)


_DESENHOS = {
    "heroi": _heroi, "goblin": _goblin, "esqueleto": _esqueleto, "zumbi": _zumbi,
    "cobra": _cobra, "escorpiao": _escorpiao, "mumia": _mumia, "demonio": _demonio, "gorila": _gorila,
    "bau": _bau, "bau_aberto": _bau_aberto, "pocao": _pocao, "erva": _erva,
}


def obter_sprite(nome, tam=T, cor=None):
    """Retorna o sprite pronto (em cache). 'cor' muda a cor da túnica/poção."""
    chave = (nome, tam, cor)
    if chave not in _cache_sprites:
        s = pygame.Surface((T, T), pygame.SRCALPHA)
        _DESENHOS[nome](s, cor)
        if tam != T:
            s = pygame.transform.scale(s, (tam, tam))
        _cache_sprites[chave] = s
    return _cache_sprites[chave]


# ------------------------------------------------------------------- TILES
def _t_grama(s, v):
    s.fill((86, 160, 72))
    rng = random.Random(v * 31 + 7)
    for _ in range(8):
        cor = rng.choice(((70, 140, 60), (105, 178, 88), (95, 170, 80)))
        _r(s, cor, rng.randint(0, 29), rng.randint(0, 29), 2, 2)


def _t_caminho(s, v):
    s.fill((194, 160, 110))
    rng = random.Random(v * 17 + 3)
    for _ in range(8):
        _r(s, rng.choice(((170, 135, 90), (210, 178, 128))), rng.randint(0, 29), rng.randint(0, 29), 3, 2)


def _t_areia(s, v):
    s.fill((225, 205, 150))
    rng = random.Random(v * 13 + 1)
    for _ in range(6):
        _r(s, (205, 185, 130), rng.randint(0, 29), rng.randint(0, 29), 2, 2)


def _t_agua(s, v):
    s.fill((48, 108, 198))
    desloc = (v % 2) * 5
    for x, y in ((4, 6), (18, 12), (8, 20), (20, 26)):
        _r(s, (100, 160, 235), (x + desloc) % 24, y, 8, 2)


def _t_arvore(s, v):
    _t_grama(s, v)
    pygame.draw.ellipse(s, (60, 120, 55), (6, 24, 22, 7))
    _r(s, (100, 65, 35), 14, 17, 5, 13)
    pygame.draw.circle(s, (40, 110, 50), (16, 12), 11)
    pygame.draw.circle(s, (40, 110, 50), (9, 16), 7)
    pygame.draw.circle(s, (40, 110, 50), (23, 16), 7)
    pygame.draw.circle(s, (62, 142, 66), (13, 9), 5)


def _t_pedra(s, v):
    _t_grama(s, v)
    pts = [(5, 26), (8, 13), (17, 8), (27, 14), (28, 26)]
    pygame.draw.polygon(s, (130, 130, 140), pts)
    pygame.draw.polygon(s, (170, 170, 180), [(8, 13), (17, 8), (20, 12), (11, 17)])
    pygame.draw.polygon(s, (80, 80, 90), pts, 2)


def _t_pedrachao(s, v):
    s.fill((152, 152, 162))
    pygame.draw.rect(s, (125, 125, 138), (0, 0, T, T), 1)
    pygame.draw.line(s, (125, 125, 138), (16, 0), (16, 16))
    pygame.draw.line(s, (125, 125, 138), (0, 16), (T, 16))
    pygame.draw.line(s, (125, 125, 138), (8, 16), (8, T))
    pygame.draw.line(s, (125, 125, 138), (24, 16), (24, T))


def _t_fonte(s, v):
    _t_pedrachao(s, v)
    pygame.draw.ellipse(s, (110, 115, 132), (2, 9, 28, 20))
    pygame.draw.ellipse(s, (90, 165, 235), (5, 12, 22, 13))
    _r(s, (200, 200, 212), 14, 3, 4, 14)
    for x, y in ((11, 5), (20, 5), (15, 1), (9, 9), (22, 9)):
        pygame.draw.circle(s, (170, 220, 255), (x, y), 2)


def _t_telhado(s, v):
    s.fill((170, 60, 50))
    for y in range(0, T, 8):
        pygame.draw.line(s, (130, 40, 35), (0, y), (T, y), 2)
        off = 8 if (y // 8) % 2 else 0
        for x in range(off, T, 16):
            pygame.draw.line(s, (130, 40, 35), (x, y), (x, y + 8))


def _t_parede(s, v):
    s.fill((212, 192, 152))
    pygame.draw.line(s, (180, 160, 120), (0, T - 1), (T, T - 1), 2)
    _r(s, (80, 140, 195), 9, 7, 14, 12)
    pygame.draw.rect(s, (110, 75, 40), (9, 7, 14, 12), 2)
    pygame.draw.line(s, (110, 75, 40), (16, 7), (16, 19), 2)


def _t_porta(s, v):
    s.fill((212, 192, 152))
    _r(s, (110, 70, 35), 8, 4, 16, 28)
    pygame.draw.rect(s, (70, 45, 20), (8, 4, 16, 28), 2)
    pygame.draw.circle(s, (235, 200, 80), (21, 19), 2)


def _t_flor(s, v):
    _t_grama(s, v)
    rng = random.Random(v * 5 + 11)
    for _ in range(4):
        x, y = rng.randint(3, 27), rng.randint(3, 27)
        cor = rng.choice(((235, 80, 90), (245, 215, 70), (245, 245, 245), (190, 110, 235)))
        pygame.draw.circle(s, cor, (x, y), 2)
        _r(s, (240, 200, 60), x, y, 1, 1)


def _t_ponte(s, v):
    s.fill((150, 105, 55))
    for x in range(0, T, 8):
        pygame.draw.line(s, (105, 70, 35), (x, 0), (x, T))
    _r(s, (95, 65, 32), 0, 0, T, 3)
    _r(s, (95, 65, 32), 0, T - 3, T, 3)


def _t_lapide(s, v):
    _t_grama(s, v)
    pygame.draw.ellipse(s, (60, 120, 55), (7, 25, 20, 6))
    _r(s, (165, 165, 175), 10, 11, 12, 17)
    pygame.draw.circle(s, (165, 165, 175), (16, 11), 6)
    pygame.draw.rect(s, (105, 105, 118), (10, 11, 12, 17), 1)
    _r(s, (110, 110, 122), 15, 10, 2, 9)
    _r(s, (110, 110, 122), 12, 13, 8, 2)


def _t_savana(s, v):
    s.fill((190, 170, 90))
    rng = random.Random(v * 29 + 5)
    for _ in range(9):
        cor = rng.choice(((170, 150, 75), (205, 185, 105), (180, 160, 80)))
        _r(s, cor, rng.randint(0, 29), rng.randint(0, 29), 2, 2)


def _t_capim(s, v):
    _t_savana(s, v)
    rng = random.Random(v * 7 + 2)
    for _ in range(4):
        x, y = rng.randint(4, 26), rng.randint(10, 28)
        pygame.draw.line(s, (120, 140, 50), (x, y), (x - 2, y - 7), 1)
        pygame.draw.line(s, (140, 160, 60), (x, y), (x + 1, y - 8), 1)
        pygame.draw.line(s, (120, 140, 50), (x, y), (x + 3, y - 6), 1)


def _t_acacia(s, v):
    _t_savana(s, v)
    pygame.draw.ellipse(s, (160, 140, 70), (8, 26, 18, 5))
    _r(s, (95, 65, 40), 15, 12, 3, 17)
    pygame.draw.line(s, (95, 65, 40), (16, 18), (9, 12), 2)
    pygame.draw.line(s, (95, 65, 40), (17, 16), (24, 11), 2)
    pygame.draw.ellipse(s, (70, 130, 55), (1, 3, 30, 10))
    pygame.draw.ellipse(s, (95, 160, 70), (6, 3, 14, 5))


def _t_deserto(s, v):
    s.fill((230, 200, 130))
    rng = random.Random(v * 19 + 9)
    for _ in range(7):
        _r(s, rng.choice(((215, 185, 115), (240, 215, 150))), rng.randint(0, 28), rng.randint(0, 29), 3, 1)


def _t_duna(s, v):
    _t_deserto(s, v)
    pygame.draw.ellipse(s, (240, 215, 150), (2, 10, 28, 16))
    pygame.draw.arc(s, (205, 175, 105), (2, 10, 28, 16), 3.6, 6.1, 2)


def _t_cacto(s, v):
    _t_deserto(s, v)
    pygame.draw.ellipse(s, (205, 175, 105), (7, 26, 18, 5))
    _r(s, (60, 140, 70), 13, 6, 6, 22)
    _r(s, (60, 140, 70), 6, 12, 8, 4)
    _r(s, (60, 140, 70), 6, 8, 4, 6)
    _r(s, (60, 140, 70), 18, 15, 8, 4)
    _r(s, (60, 140, 70), 22, 10, 4, 7)
    _r(s, (90, 175, 95), 15, 8, 2, 18)
    for x, y in ((13, 10), (18, 14), (13, 20), (18, 22)):
        _r(s, (240, 240, 200), x, y, 1, 1)


def _t_rochadeserto(s, v):
    _t_deserto(s, v)
    pts = [(3, 27), (6, 12), (16, 5), (27, 11), (30, 27)]
    pygame.draw.polygon(s, (160, 110, 75), pts)
    pygame.draw.polygon(s, (200, 150, 105), [(6, 12), (16, 5), (20, 10), (10, 16)])
    pygame.draw.polygon(s, (105, 65, 40), pts, 2)


def _t_ossos(s, v):
    _t_deserto(s, v)
    osso = (240, 235, 215)
    pygame.draw.line(s, osso, (8, 22), (22, 16), 3)
    pygame.draw.circle(s, osso, (7, 22), 2)
    pygame.draw.circle(s, osso, (23, 16), 2)
    pygame.draw.circle(s, osso, (21, 24), 4)
    _r(s, (60, 50, 40), 19, 23, 2, 2)
    _r(s, (60, 50, 40), 23, 23, 2, 2)


_TILES = {
    "grama": _t_grama, "caminho": _t_caminho, "areia": _t_areia, "agua": _t_agua,
    "arvore": _t_arvore, "pedra": _t_pedra, "pedrachao": _t_pedrachao, "fonte": _t_fonte,
    "telhado": _t_telhado, "parede": _t_parede, "porta": _t_porta, "flor": _t_flor,
    "ponte": _t_ponte, "lapide": _t_lapide,
    "savana": _t_savana, "capim": _t_capim, "acacia": _t_acacia, "deserto": _t_deserto,
    "duna": _t_duna, "cacto": _t_cacto, "rochadeserto": _t_rochadeserto, "ossos": _t_ossos,
}

# cor usada no minimapa
COR_MINIMAPA = {
    "grama": (86, 160, 72), "caminho": (194, 160, 110), "areia": (225, 205, 150), "agua": (48, 108, 198),
    "arvore": (40, 110, 50), "pedra": (130, 130, 140), "pedrachao": (152, 152, 162), "fonte": (90, 165, 235),
    "telhado": (170, 60, 50), "parede": (212, 192, 152), "porta": (110, 70, 35), "flor": (150, 190, 90),
    "ponte": (150, 105, 55), "lapide": (150, 150, 160),
    "savana": (190, 170, 90), "capim": (170, 160, 70), "acacia": (70, 130, 55), "deserto": (230, 200, 130),
    "duna": (240, 215, 150), "cacto": (60, 140, 70), "rochadeserto": (160, 110, 75), "ossos": (235, 225, 200),
}


def obter_tile(nome, variante=0):
    chave = (nome, variante)
    if chave not in _cache_tiles:
        s = pygame.Surface((T, T))
        _TILES[nome](s, variante)
        _cache_tiles[chave] = s
    return _cache_tiles[chave]
