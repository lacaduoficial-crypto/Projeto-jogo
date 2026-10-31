"""Mapa 2D da floresta: exploração, inimigos visíveis, baús, itens e fonte de cura."""
import math
import random

import pygame

from inimigos.inimigos import SIMBOLOS, criar_inimigo
from sistemas import graficos, itens, personagem, salvar, ui
from sistemas.combate import combate, tela_vitoria

TAM = 32                      # tamanho de cada quadrado
FLARG, FALT = 48, 36          # tamanho da floresta (canto superior esquerdo)
LARG, ALT = 96, 72            # tamanho do mundo inteiro, em quadrados
COLUNAS, LINHAS = 30, 18      # área visível (960 x 576)
ESC_MINI = 2                  # tamanho de cada quadrado no minimapa
PASSAVEIS = {"grama", "caminho", "areia", "flor", "ponte", "pedrachao",
             "savana", "capim", "deserto", "duna", "ossos"}
FONTE = (24, 20)              # fonte de cura da vila (praça central)
FONTES = {                    # todos os pontos de cura do mundo
    FONTE: "Fonte da vila",
    (66, 24): "Poço da savana",
    (32, 52): "Oásis do deserto",
    (58, 50): "Oásis perdido",
}
SPAWN = (24, 22)              # onde o personagem começa / acorda após perder
CEMITERIO = (9, 8)            # centro do cemitério
DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))
NOMES_BIOMA = {"floresta": "Floresta", "savana": "Savana", "deserto": "Deserto"}

TEMPO_FONTE = 25000           # ms até a fonte encher de novo
TEMPO_BAU = 180000            # ms até um baú reaparecer fechado
TEMPO_RESPAWN = 45000         # ms até um inimigo derrotado reaparecer


def _dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _sinal(n):
    return (n > 0) - (n < 0)


# ------------------------------------------------------------- GERAÇÃO
def _gerar_floresta(semente=2024):
    """Monta a grade do mapa (lista de listas de nomes de tiles)."""
    rng = random.Random(semente)
    g = [["grama"] * FLARG for _ in range(FALT)]

    def lago(cx, cy, rx, ry):
        for y in range(FALT):
            for x in range(FLARG):
                d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
                if d <= 1:
                    g[y][x] = "agua"
                elif d <= 1.5:
                    g[y][x] = "areia"

    def trilha(x1, y1, x2, y2):
        x, y = x1, y1
        pontos = []
        while x != x2:
            pontos.append((x, y))
            x += _sinal(x2 - x)
        while y != y2:
            pontos.append((x, y))
            y += _sinal(y2 - y)
        pontos.append((x2, y2))
        for px, py in pontos:
            if g[py][px] in ("grama", "arvore", "pedra", "flor", "areia"):
                g[py][px] = "caminho"

    def casa(x, y):
        for i in range(4):
            g[y][x + i] = "telhado"
            g[y + 1][x + i] = "telhado"
            g[y + 2][x + i] = "parede"
        g[y + 2][x + 1] = "porta"

    # lago com ponte e lagoa
    lago(37, 10, 5.5, 4.0)
    lago(9, 27, 3.0, 2.5)
    # praça central com a fonte
    for dy in range(-3, 4):
        for dx in range(-4, 5):
            g[FONTE[1] + dy][FONTE[0] + dx] = "pedrachao"
    g[FONTE[1]][FONTE[0]] = "fonte"
    # estradas
    trilha(3, 20, 44, 20)
    trilha(24, 4, 24, 31)
    trilha(24, 10, 31, 10)
    trilha(24, 28, 14, 28)
    trilha(24, 6, 12, 6)
    trilha(24, 32, 40, 32)
    for x in range(30, 45):
        if g[10][x] == "agua":
            g[10][x] = "ponte"
    # casas da vila
    for pos in ((14, 15), (30, 15), (14, 23), (30, 23)):
        casa(*pos)
    # cemitério
    for y in range(4, 11):
        for x in range(5, 14):
            if g[y][x] == "grama" and rng.random() < 0.28:
                g[y][x] = "lapide"
    # decoração aleatória (mais árvores quanto mais longe da vila)
    for y in range(FALT):
        for x in range(FLARG):
            if g[y][x] != "grama":
                continue
            dist_praca = abs(x - FONTE[0]) + abs(y - FONTE[1])
            if dist_praca <= 8:
                if rng.random() < 0.06:
                    g[y][x] = "flor"
                continue
            r = rng.random()
            dens = 0.07 + min(dist_praca, 40) / 40 * 0.12
            if r < dens:
                g[y][x] = "arvore"
            elif r < dens + 0.03:
                g[y][x] = "pedra"
            elif r < dens + 0.10:
                g[y][x] = "flor"
    # borda de árvores
    for y in range(FALT):
        for x in range(FLARG):
            d = min(x, y, FLARG - 1 - x, FALT - 1 - y)
            if d <= 1 or (d == 2 and rng.random() < 0.6):
                g[y][x] = "arvore"
    return g


def bioma_em(x, y):
    """Qual bioma fica em um quadrado."""
    if y >= FALT:
        return "deserto"
    return "savana" if x >= FLARG else "floresta"


_SUBSTITUIVEIS = {"grama", "arvore", "pedra", "flor", "areia", "savana", "capim", "acacia", "deserto",
                  "duna", "cacto", "rochadeserto", "ossos"}


def gerar_mapa(semente=2024):
    """Monta o mundo inteiro: floresta (noroeste), savana (nordeste) e deserto (sul)."""
    rng = random.Random(semente + 1)
    g = [["deserto"] * LARG for _ in range(ALT)]
    floresta = _gerar_floresta(semente)
    for y in range(ALT):
        for x in range(LARG):
            if y < FALT and x < FLARG:
                g[y][x] = floresta[y][x]
            elif y < FALT:
                g[y][x] = "savana"

    def lago(cx, cy, rx, ry):
        for y in range(ALT):
            for x in range(LARG):
                d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
                if d <= 1:
                    g[y][x] = "agua"
                elif d <= 1.5:
                    g[y][x] = "areia"

    def trilha(x1, y1, x2, y2):
        x, y = x1, y1
        pontos = []
        while x != x2:
            pontos.append((x, y))
            x += _sinal(x2 - x)
        while y != y2:
            pontos.append((x, y))
            y += _sinal(y2 - y)
        pontos.append((x2, y2))
        for px, py in pontos:
            if g[py][px] in _SUBSTITUIVEIS:
                g[py][px] = "caminho"

    def praca(cx, cy):
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                g[cy + dy][cx + dx] = "pedrachao"
        g[cy][cx] = "fonte"

    # lagos: poço de água da savana e dois oásis
    lago(72, 12, 5.0, 3.5)
    lago(18, 56, 3.5, 3.0)
    lago(70, 52, 5.0, 3.5)
    # decoração da savana e do deserto
    for y in range(ALT):
        for x in range(LARG):
            zona = bioma_em(x, y)
            if zona == "floresta" or g[y][x] not in ("savana", "deserto"):
                continue
            r = rng.random()
            if zona == "savana":
                if r < 0.045:
                    g[y][x] = "acacia"
                elif r < 0.065:
                    g[y][x] = "rochadeserto"
                elif r < 0.225:
                    g[y][x] = "capim"
            else:
                if r < 0.035:
                    g[y][x] = "cacto"
                elif r < 0.060:
                    g[y][x] = "rochadeserto"
                elif r < 0.072:
                    g[y][x] = "ossos"
                elif r < 0.212:
                    g[y][x] = "duna"
    # transição suave entre savana e deserto
    for y in range(31, 41):
        for x in range(FLARG, LARG):
            if g[y][x] in ("savana", "capim", "deserto", "duna"):
                if y < FALT and rng.random() < (y - 30) / 6 * 0.5:
                    g[y][x] = "deserto"
                elif y >= FALT and rng.random() < (41 - y) / 6 * 0.5:
                    g[y][x] = "savana"
    # estradas
    trilha(44, 20, 88, 20)        # da vila para o leste
    trilha(62, 20, 62, 5)
    trilha(66, 20, 66, 24)        # até o poço
    trilha(80, 20, 80, 44)        # liga a savana ao deserto
    trilha(24, 31, 24, 62)        # da vila para o sul
    trilha(24, 44, 88, 44)
    trilha(24, 62, 88, 62)
    trilha(32, 44, 32, 52)        # até o primeiro oásis
    trilha(58, 44, 58, 50)        # até o segundo oásis
    for cx, cy in FONTES:
        if cx != FONTE[0] or cy != FONTE[1]:
            praca(cx, cy)
    # borda externa do mundo
    for y in range(ALT):
        for x in range(LARG):
            if min(x, y, LARG - 1 - x, ALT - 1 - y) <= 1:
                zona = bioma_em(x, y)
                g[y][x] = {"floresta": "arvore", "savana": "acacia", "deserto": "rochadeserto"}[zona]
    # portões na muralha de árvores da floresta (leste e sul)
    for y in range(19, 22):
        for x in range(43, 52):
            g[y][x] = "caminho"
    for x in range(23, 26):
        for y in range(30, 40):
            g[y][x] = "caminho"
    return g


def alcancaveis(g, inicio):
    """Quadrados que o personagem consegue alcançar andando a partir de 'inicio'."""
    vistos = {inicio}
    fila = [inicio]
    while fila:
        x, y = fila.pop()
        for dx, dy in DIRS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < LARG and 0 <= ny < ALT and (nx, ny) not in vistos and g[ny][nx] in PASSAVEIS:
                vistos.add((nx, ny))
                fila.append((nx, ny))
    return vistos


class Mundo:
    """Estado do mapa: grade, inimigos, baús e itens no chão (persiste entre visitas)."""

    def __init__(self):
        rng = random.Random()
        self.grid = gerar_mapa()
        livres = alcancaveis(self.grid, SPAWN)
        abertos = [c for c in livres
                   if sum(1 for dx, dy in DIRS if self.grid[c[1] + dy][c[0] + dx] in PASSAVEIS) >= 3]
        ocupados = [SPAWN]

        def escolher(n, dist_min, sep, regiao=None):
            melhor = []
            for reg in ((regiao, None) if regiao else (None,)):
                for s in (sep, 3, 1):
                    cand = [c for c in abertos if _dist(c, SPAWN) >= dist_min and c not in ocupados
                            and (reg is None or reg(c))]
                    rng.shuffle(cand)
                    res = []
                    for c in cand:
                        if all(_dist(c, o) >= s for o in ocupados + res):
                            res.append(c)
                            if len(res) == n:
                                break
                    if len(res) > len(melhor):
                        melhor = res
                    if len(melhor) == n:
                        ocupados.extend(melhor)
                        return melhor
            ocupados.extend(melhor)
            return melhor

        no_cemiterio = lambda c: _dist(c, CEMITERIO) <= 8
        fora_cemiterio = lambda c: _dist(c, CEMITERIO) > 12
        em_floresta = lambda c: bioma_em(*c) == "floresta"
        em_savana = lambda c: bioma_em(*c) == "savana"
        em_deserto = lambda c: bioma_em(*c) == "deserto"
        savana_leste = lambda c: bioma_em(*c) == "savana" and c[0] >= 72
        deserto_norte = lambda c: em_deserto(c) and c[1] <= 52
        deserto_fundo = lambda c: em_deserto(c) and c[1] >= 50
        deserto_extremo = lambda c: em_deserto(c) and c[1] >= 56
        ocupados.extend(p for p in FONTES if p not in ocupados)

        self.baus = []
        self.itens_chao = []
        # (região, baús, itens no chão, tier mínimo, tier máximo)
        for regiao, n_baus, n_itens, t_min, t_max in (
                (em_floresta, 6, 8, 1, 1), (em_savana, 5, 6, 1, 2), (em_deserto, 6, 6, 2, 3)):
            for x, y in escolher(n_baus, 6, 8, regiao):
                self.baus.append({"x": x, "y": y, "aberto_em": None, "tier_min": t_min, "tier_max": t_max})
            for x, y in escolher(n_itens, 3, 4, regiao):
                self.itens_chao.append({"x": x, "y": y, "nome": itens.sortear_consumivel(t_max, t_min)})

        self.inimigos = []
        posicoes = (
            [("goblin", p) for p in escolher(2, 10, 8, lambda c: em_floresta(c) and fora_cemiterio(c))]
            + [("esqueleto", p) for p in escolher(2, 10, 5, no_cemiterio)]
            + [("zumbi", p) for p in escolher(2, 10, 5, no_cemiterio)]
            + [("cobra", p) for p in escolher(3, 12, 7, em_savana)]
            + [("gorila", p) for p in escolher(2, 12, 10, savana_leste)]
            + [("escorpiao", p) for p in escolher(3, 12, 7, deserto_norte)]
            + [("mumia", p) for p in escolher(3, 12, 7, deserto_fundo)]
            + [("demonio", p) for p in escolher(2, 12, 10, deserto_extremo)]
        )
        for tipo, (x, y) in posicoes:
            self.inimigos.append({
                "tipo": tipo, "x": x, "y": y, "vx": float(x), "vy": float(y), "origem": (x, y),
                "vivo": True, "morto_em": 0, "prox_mov": 0, "imune_ate": 0,
            })
        self.fontes_livres = {pos: 0 for pos in FONTES}

    def bau_em(self, x, y):
        for b in self.baus:
            if b["x"] == x and b["y"] == y:
                return b
        return None

    def inimigo_em(self, x, y):
        for i in self.inimigos:
            if i["vivo"] and i["x"] == x and i["y"] == y:
                return i
        return None

    def bloqueado(self, x, y, jogador=None):
        if not (0 <= x < LARG and 0 <= y < ALT):
            return True
        if self.grid[y][x] not in PASSAVEIS or jogador == (x, y):
            return True
        if self.bau_em(x, y):
            return True
        return self.inimigo_em(x, y) is not None

    def livre_perto(self, pos):
        """Quadrado livre mais próximo de 'pos' (para renascer sem cair em cima de algo)."""
        for raio in range(0, 6):
            for dy in range(-raio, raio + 1):
                for dx in range(-raio, raio + 1):
                    if not self.bloqueado(pos[0] + dx, pos[1] + dy):
                        return (pos[0] + dx, pos[1] + dy)
        return pos


def _construir_minimapa(grid):
    esc = ESC_MINI
    s = pygame.Surface((LARG * esc, ALT * esc))
    for y in range(ALT):
        for x in range(LARG):
            pygame.draw.rect(s, graficos.COR_MINIMAPA[grid[y][x]], (x * esc, y * esc, esc, esc))
    return s


# ---------------------------------------------------------- EXPLORAÇÃO
class Exploracao:
    def __init__(self, tela, jogador, mundo):
        self.tela = tela
        self.j = jogador
        self.mundo = mundo
        if jogador.get("x") is None:
            jogador["x"], jogador["y"] = mundo.livre_perto(SPAWN)
        self.vx, self.vy = float(jogador["x"]), float(jogador["y"])
        self.avisos = []
        self.mostrar_mini = True
        self.mini = _construir_minimapa(mundo.grid)
        self.ultimo_passo = 0
        self.bioma_atual = bioma_em(jogador["x"], jogador["y"])
        self.ultimo_save = pygame.time.get_ticks()
        self.ultima_regen = pygame.time.get_ticks()
        for ini in mundo.inimigos:
            ini["vx"], ini["vy"] = float(ini["x"]), float(ini["y"])
        self.aviso("WASD move | E interage | H cura | I inventário | M minimapa | ESC menu")

    # ---- utilidades
    def aviso(self, msg):
        self.avisos.append([msg, pygame.time.get_ticks() + 4500])
        self.avisos = self.avisos[-5:]

    def _camera(self):
        cx = int(self.vx * TAM + TAM / 2 - COLUNAS * TAM / 2)
        cy = int(self.vy * TAM + TAM / 2 - LINHAS * TAM / 2)
        cx = max(0, min(cx, LARG * TAM - COLUNAS * TAM))
        cy = max(0, min(cy, ALT * TAM - LINHAS * TAM))
        return cx, cy

    def _vizinhos_interacao(self):
        j = self.j
        return [(j["x"] + dx, j["y"] + dy) for dx, dy in ((0, 0),) + DIRS]

    def dica(self):
        for x, y in self._vizinhos_interacao():
            b = self.mundo.bau_em(x, y)
            if b and b["aberto_em"] is None:
                return "[E] Abrir baú"
            if (x, y) in FONTES:
                return "[E] Beber da fonte"
        return None

    # ---- mecânicas
    def interagir(self):
        for x, y in self._vizinhos_interacao():
            b = self.mundo.bau_em(x, y)
            if b and b["aberto_em"] is None:
                self.abrir_bau(b)
                return
            if (x, y) in FONTES:
                self.usar_fonte((x, y))
                return
        self.aviso("Não há nada para interagir aqui.")

    def abrir_bau(self, b):
        b["aberto_em"] = pygame.time.get_ticks()
        achados = [itens.sortear_item(b.get("tier_max", 3), b.get("tier_min", 1)) for _ in range(random.choice((1, 1, 2)))]
        for nome in achados:
            itens.adicionar_item(self.j, nome)
        self.aviso("Você abriu o baú e encontrou: " + ", ".join(achados) + "!")

    def usar_fonte(self, pos):
        j, m = self.j, self.mundo
        agora = pygame.time.get_ticks()
        livre = m.fontes_livres.get(pos, 0)
        nome = FONTES.get(pos, "fonte")
        if agora < livre:
            self.aviso(f"{nome}: ainda está se enchendo ({(livre - agora) // 1000 + 1}s).")
        elif j["vida"] >= j["vida_maxima"] and j["energia"] >= j["energia_maxima"]:
            self.aviso("Você já está revigorado.")
        else:
            j["vida"], j["energia"] = j["vida_maxima"], j["energia_maxima"]
            m.fontes_livres[pos] = agora + TEMPO_FONTE
            self.aviso(f"{nome}: a água restaura toda a sua vida e energia!")

    def cura_rapida(self):
        j = self.j
        if j["vida"] >= j["vida_maxima"]:
            self.aviso("Sua vida já está cheia.")
            return
        nome = itens.melhor_cura(j)
        if nome is None:
            self.aviso("Você não tem itens de cura.")
            return
        ok, msg = itens.usar_item(j, nome)
        self.aviso(("Usou " + msg) if ok else msg)

    def mover_jogador(self, agora):
        if agora - self.ultimo_passo < 115:
            return
        t = pygame.key.get_pressed()
        dx = dy = 0
        if t[pygame.K_a] or t[pygame.K_LEFT]:
            dx = -1
        elif t[pygame.K_d] or t[pygame.K_RIGHT]:
            dx = 1
        elif t[pygame.K_w] or t[pygame.K_UP]:
            dy = -1
        elif t[pygame.K_s] or t[pygame.K_DOWN]:
            dy = 1
        if not (dx or dy):
            return
        self.ultimo_passo = agora
        nx, ny = self.j["x"] + dx, self.j["y"] + dy
        if not self.mundo.bloqueado(nx, ny):
            self.j["x"], self.j["y"] = nx, ny
            self.ao_pisar(nx, ny)
            self.checar_bioma()

    def checar_bioma(self):
        atual = bioma_em(self.j["x"], self.j["y"])
        if atual != self.bioma_atual:
            self.bioma_atual = atual
            avisos = {"floresta": "Você voltou para a Floresta.",
                      "savana": "Você entrou na Savana. Cobras e gorilas mutantes rondam por aqui!",
                      "deserto": "Você entrou no Deserto. Escorpiões, múmias e demônios vivem aqui!"}
            self.aviso(avisos[atual])

    def ao_pisar(self, x, y):
        for it in list(self.mundo.itens_chao):
            if it["x"] == x and it["y"] == y:
                itens.adicionar_item(self.j, it["nome"])
                self.mundo.itens_chao.remove(it)
                self.aviso(f'Você pegou: {it["nome"]}')
        self.verificar_combate()

    def atualizar_inimigos(self, agora):
        m, j = self.mundo, self.j
        pos_j = (j["x"], j["y"])
        for ini in m.inimigos:
            if not ini["vivo"]:
                ox, oy = ini["origem"]
                if agora - ini["morto_em"] > TEMPO_RESPAWN and _dist(pos_j, (ox, oy)) > 10 \
                        and not m.bloqueado(ox, oy):
                    ini.update(vivo=True, x=ox, y=oy, vx=float(ox), vy=float(oy), imune_ate=agora + 1000)
                continue
            if agora < ini["prox_mov"]:
                continue
            d = _dist((ini["x"], ini["y"]), pos_j)
            if d <= 6 and agora >= ini["imune_ate"]:
                ini["prox_mov"] = agora + 420
                dx, dy = j["x"] - ini["x"], j["y"] - ini["y"]
                if abs(dx) >= abs(dy):
                    tentativas = [(_sinal(dx), 0), (0, _sinal(dy))]
                else:
                    tentativas = [(0, _sinal(dy)), (_sinal(dx), 0)]
                for tx, ty in tentativas:
                    if (tx, ty) == (0, 0):
                        continue
                    nx, ny = ini["x"] + tx, ini["y"] + ty
                    if not m.bloqueado(nx, ny, pos_j):
                        ini["x"], ini["y"] = nx, ny
                        break
            else:
                ini["prox_mov"] = agora + random.randint(500, 1200)
                if random.random() < 0.6:
                    dx, dy = random.choice(DIRS)
                    nx, ny = ini["x"] + dx, ini["y"] + dy
                    if _dist((nx, ny), ini["origem"]) <= 5 and not m.bloqueado(nx, ny, pos_j):
                        ini["x"], ini["y"] = nx, ny

    def verificar_combate(self):
        agora = pygame.time.get_ticks()
        for ini in self.mundo.inimigos:
            if ini["vivo"] and agora >= ini["imune_ate"] \
                    and _dist((ini["x"], ini["y"]), (self.j["x"], self.j["y"])) == 1:
                self.lutar(ini)
                return

    def lutar(self, ini):
        j = self.j
        inimigo = criar_inimigo(ini["tipo"], j["nivel"])
        resultado = combate(self.tela, j, inimigo)
        agora = pygame.time.get_ticks()
        if resultado == "vitoria":
            ini["vivo"] = False
            ini["morto_em"] = agora
            linhas = tela_vitoria(self.tela, j, inimigo, fundo=self.desenhar)
            for linha in linhas[1:]:
                self.aviso(linha)
        elif resultado == "fuga":
            ini["imune_ate"] = agora + 4000
            self.aviso("Você escapou!")
        else:
            msg = personagem.desmaiar(j)
            j["x"], j["y"] = self.mundo.livre_perto(SPAWN)
            self.vx, self.vy = float(j["x"]), float(j["y"])
            for outro in self.mundo.inimigos:
                outro["imune_ate"] = agora + 3000
            ui.mensagem(self.tela, "VOCÊ FOI DERROTADO", [msg], fundo=self.desenhar, cor_titulo=ui.VERMELHO)
        self.ultimo_passo = pygame.time.get_ticks()
        pygame.event.clear(pygame.KEYDOWN)
        salvar.salvar(j)

    # ---- desenho
    def desenhar(self, tela=None):
        tela = tela or self.tela
        j, m = self.j, self.mundo
        agora = pygame.time.get_ticks()
        cam_x, cam_y = self._camera()
        tela.fill((20, 40, 30))
        c0, l0 = cam_x // TAM, cam_y // TAM
        frame = (agora // 450) % 2
        for ly in range(l0, min(ALT, l0 + LINHAS + 2)):
            for lx in range(c0, min(LARG, c0 + COLUNAS + 2)):
                nome = m.grid[ly][lx]
                var = (frame + lx + ly) % 2 if nome == "agua" else (lx * 7 + ly * 13) % 4
                tela.blit(graficos.obter_tile(nome, var), (lx * TAM - cam_x, ly * TAM - cam_y))

        ents = []   # (ordem, sprite, x, y, sombra)
        crachas = []
        for b in m.baus:
            spr = graficos.obter_sprite("bau" if b["aberto_em"] is None else "bau_aberto")
            ents.append((b["y"] * TAM, spr, b["x"] * TAM - cam_x, b["y"] * TAM - cam_y, False))
        for it in m.itens_chao:
            info = itens.ITENS[it["nome"]]
            spr = graficos.obter_sprite(info.get("icone", "pocao"), TAM, info["cor"])
            bob = int(math.sin(agora / 300 + it["x"]) * 2)
            ents.append((it["y"] * TAM - 1, spr, it["x"] * TAM - cam_x, it["y"] * TAM - cam_y + bob, True))
        for ini in m.inimigos:
            if not ini["vivo"]:
                continue
            px, py = ini["vx"] * TAM - cam_x, ini["vy"] * TAM - cam_y
            ents.append((ini["vy"] * TAM, graficos.obter_sprite(ini["tipo"]), px, py, True))
            crachas.append((SIMBOLOS[ini["tipo"]], px, py))
        ents.append((self.vy * TAM, graficos.obter_sprite("heroi"), self.vx * TAM - cam_x, self.vy * TAM - cam_y, True))

        for _, spr, px, py, sombra in sorted(ents, key=lambda e: e[0]):
            if px < -TAM or py < -TAM or px > ui.LARGURA or py > LINHAS * TAM + TAM:
                continue
            if sombra:
                pygame.draw.ellipse(tela, (25, 55, 30), (int(px) + 5, int(py) + 26, 22, 8))
            tela.blit(spr, (int(px), int(py)))
        for letra, px, py in crachas:
            pygame.draw.rect(tela, (150, 30, 30), (int(px) + 10, int(py) - 12, 13, 14), border_radius=3)
            ui.texto(tela, letra, int(px) + 16, int(py) - 12, 13, ui.BRANCO, True, "centro")
        ui.texto(tela, j["nome"], int(self.vx * TAM - cam_x) + 16, int(self.vy * TAM - cam_y) - 16, 13,
                 ui.OURO, True, "centro")

        # dica de interação
        dica = self.dica()
        if dica:
            ui.painel(tela, (380, 536, 200, 30))
            ui.texto(tela, dica, 480, 541, 18, ui.BRANCO, True, "centro")

        # avisos
        for i, (msg, _) in enumerate(self.avisos):
            ui.painel(tela, (10, 10 + i * 30, 640, 26), alpha=190)
            ui.texto(tela, msg, 18, 13 + i * 30, 16)

        if self.mostrar_mini:
            self._desenhar_minimapa(tela, cam_x, cam_y, agora)
        self._desenhar_hud(tela)

    def _desenhar_minimapa(self, tela, cam_x, cam_y, agora):
        esc = ESC_MINI
        mx, my = ui.LARGURA - LARG * esc - 12, 12
        tela.blit(self.mini, (mx, my))
        pygame.draw.rect(tela, ui.OURO, (mx - 2, my - 2, LARG * esc + 4, ALT * esc + 4), 2)
        pygame.draw.rect(tela, (255, 255, 255), (mx + cam_x * esc // TAM, my + cam_y * esc // TAM,
                                                  COLUNAS * esc, LINHAS * esc), 1)
        for fx, fy in FONTES:
            pygame.draw.rect(tela, (120, 230, 255), (mx + fx * esc - 1, my + fy * esc - 1, 4, 4))
        for b in self.mundo.baus:
            if b["aberto_em"] is None:
                pygame.draw.rect(tela, (255, 215, 60), (mx + b["x"] * esc, my + b["y"] * esc, 3, 3))
        for ini in self.mundo.inimigos:
            if ini["vivo"]:
                pygame.draw.rect(tela, (230, 50, 50), (mx + ini["x"] * esc - 1, my + ini["y"] * esc - 1, 4, 4))
        if (agora // 300) % 2 == 0:
            pygame.draw.rect(tela, (255, 255, 255), (mx + self.j["x"] * esc - 1, my + self.j["y"] * esc - 1, 5, 5))

    def _desenhar_hud(self, tela):
        j = self.j
        ui.painel(tela, (0, 576, ui.LARGURA, 64), cor=(18, 18, 28), alpha=255)
        ui.texto(tela, f'{j["nome"]}  |  Nv {j["nivel"]}', 12, 580, 18, ui.OURO, True)
        ui.barra(tela, 12, 604, 220, 18, j["vida"], j["vida_maxima"], (200, 60, 60),
                 f'PV {j["vida"]}/{j["vida_maxima"]}')
        ui.barra(tela, 244, 604, 150, 18, j["energia"], j["energia_maxima"], (70, 130, 230),
                 f'PE {j["energia"]}/{j["energia_maxima"]}')
        ui.barra(tela, 406, 604, 150, 18, j["experiencia"], personagem.xp_para_proximo(j), (230, 190, 70),
                 f'XP {j["experiencia"]}/{personagem.xp_para_proximo(j)}')
        ui.texto(tela, f"Itens de cura: {itens.total_cura(j)}   |   {NOMES_BIOMA[bioma_em(j['x'], j['y'])]}",
                 580, 580, 16, ui.VERDE, True)
        ui.texto(tela, "WASD mover | E interagir | H curar | I inventário", 580, 600, 14, ui.CINZA)
        ui.texto(tela, "C ficha | B itens | M minimapa | ESC menu", 580, 618, 14, ui.CINZA)

    # ---- laço principal
    def rodar(self):
        relogio = pygame.time.Clock()
        pygame.event.clear(pygame.KEYDOWN)
        while True:
            dt = min(0.1, relogio.tick(60) / 1000.0)
            agora = pygame.time.get_ticks()
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    ui.sair()
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        salvar.salvar(self.j)
                        return
                    elif ev.key == pygame.K_e:
                        self.interagir()
                    elif ev.key == pygame.K_h:
                        self.cura_rapida()
                    elif ev.key == pygame.K_m:
                        self.mostrar_mini = not self.mostrar_mini
                    elif ev.key == pygame.K_i:
                        itens.tela_inventario(self.tela, self.j, fundo=self.desenhar)
                    elif ev.key == pygame.K_c:
                        personagem.tela_ficha(self.tela, self.j, fundo=self.desenhar)
                    elif ev.key == pygame.K_b:
                        itens.tela_catalogo(self.tela, self.j, fundo=self.desenhar)

            self.mover_jogador(agora)
            self.atualizar_inimigos(agora)
            self.verificar_combate()

            # regeneração lenta fora de combate
            j = self.j
            if agora - self.ultima_regen >= 4000:
                self.ultima_regen = agora
                if j["vida"] < j["vida_maxima"]:
                    j["vida"] = min(j["vida_maxima"], j["vida"] + 1 + j["nivel"] // 3)
            # baús reaparecem
            for b in self.mundo.baus:
                if b["aberto_em"] is not None and agora - b["aberto_em"] > TEMPO_BAU:
                    b["aberto_em"] = None
            # salvamento automático a cada 30 segundos
            if agora - self.ultimo_save >= 30000:
                self.ultimo_save = agora
                salvar.salvar(j)
            # avisos expiram
            self.avisos = [a for a in self.avisos if a[1] > agora]

            # animação suave dos movimentos
            k = min(1.0, dt * 16)
            self.vx += (j["x"] - self.vx) * k
            self.vy += (j["y"] - self.vy) * k
            for ini in self.mundo.inimigos:
                ki = min(1.0, dt * 9)
                ini["vx"] += (ini["x"] - ini["vx"]) * ki
                ini["vy"] += (ini["y"] - ini["vy"]) * ki

            self.desenhar()
            pygame.display.flip()


def iniciar_mapa(tela, jogador, mundo):
    """Entra no mapa da floresta. ESC volta ao menu."""
    Exploracao(tela, jogador, mundo).rodar()
