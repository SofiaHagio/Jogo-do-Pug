"""Toda a arte do jogo, desenhada em código (sem imagens externas).

Cada função monta uma Surface uma única vez; o jogo só reaproveita as imagens prontas.
"""

import math
import random

import pygame

from . import config as c

# ---------------------------------------------------------------- utilidades


def superficie(largura, altura):
    return pygame.Surface((largura, altura), pygame.SRCALPHA)


def gradiente_vertical(largura, altura, topo, base):
    s = pygame.Surface((largura, altura))
    for y in range(altura):
        t = y / max(1, altura - 1)
        cor = [int(topo[i] + (base[i] - topo[i]) * t) for i in range(3)]
        pygame.draw.line(s, cor, (0, y), (largura, y))
    return s


def brilho(raio, cor, intensidade=90):
    """Um círculo de luz suave, usado na lua, no portal e nos ossos dourados."""
    s = superficie(raio * 2, raio * 2)
    for r in range(raio, 0, -2):
        alfa = int(intensidade * (1 - r / raio) ** 2)
        pygame.draw.circle(s, (*cor, alfa), (raio, raio), r)
    return s


def fonte(tamanho):
    return pygame.font.Font(None, tamanho)


# ---------------------------------------------------------------- pug


PELO = (226, 186, 134)
PELO_SOMBRA = (196, 150, 102)
MASCARA = (46, 34, 36)
OLHO = (24, 16, 20)
LINGUA = (236, 110, 128)


def _pug(perna_a, perna_b, corpo_dy=0, rabo=0.0, olhos_fechados=False, boca_aberta=False):
    """Desenha um pug virado para a direita numa Surface 44x36."""
    s = superficie(44, 36)
    y = 4 + corpo_dy

    # patas de trás e da frente (deslocamento muda com a animação)
    for px, desloc in ((10, perna_a), (16, perna_b), (26, perna_b), (32, perna_a)):
        pygame.draw.rect(s, PELO_SOMBRA, (px + desloc, y + 22, 5, 9 - abs(desloc) // 2), border_radius=2)
        pygame.draw.rect(s, MASCARA, (px + desloc, y + 28 - abs(desloc) // 2, 5, 3), border_radius=1)

    # rabinho enrolado
    cx, cy = 8, y + 10 + rabo
    pygame.draw.circle(s, PELO_SOMBRA, (cx, int(cy)), 5, 3)

    # corpo
    pygame.draw.ellipse(s, PELO, (6, y + 8, 28, 20))
    pygame.draw.ellipse(s, PELO_SOMBRA, (8, y + 18, 24, 9))

    # cabeça
    pygame.draw.circle(s, PELO, (31, y + 11), 11)
    pygame.draw.ellipse(s, MASCARA, (21, y - 1, 7, 9))  # orelha de trás
    pygame.draw.ellipse(s, MASCARA, (34, y - 1, 7, 9))  # orelha da frente
    pygame.draw.ellipse(s, MASCARA, (29, y + 10, 14, 10))  # focinho preto
    pygame.draw.line(s, PELO_SOMBRA, (27, y + 6), (35, y + 6), 1)  # rugas
    pygame.draw.line(s, PELO_SOMBRA, (28, y + 8), (34, y + 8), 1)
    pygame.draw.ellipse(s, (20, 12, 14), (37, y + 11, 6, 4))  # nariz

    # olhos grandes de pug
    for ox in (28, 37):
        if olhos_fechados:
            pygame.draw.line(s, OLHO, (ox - 3, y + 9), (ox + 2, y + 9), 2)
        else:
            pygame.draw.circle(s, OLHO, (ox, y + 8), 3)
            pygame.draw.circle(s, c.BRANCO, (ox + 1, y + 7), 1)

    if boca_aberta:
        pygame.draw.ellipse(s, LINGUA, (34, y + 17, 6, 6))
    return s


def frames_pug():
    """Quadros de animação do pug, para direita e esquerda."""
    passos = [(-3, 3), (0, 0), (3, -3), (0, 0)]
    direita = {
        "parado": [_pug(0, 0, 0, 0), _pug(0, 0, 1, 1)],
        "piscar": [_pug(0, 0, 0, 0, olhos_fechados=True)],
        "correndo": [_pug(a, b, 1 if a == 0 else 0, a * 0.6, boca_aberta=True) for a, b in passos],
        "subindo": [_pug(-3, 3, -1, -2, boca_aberta=True)],
        "caindo": [_pug(3, -3, 0, 2)],
        "dano": [_pug(0, 0, 0, 0, olhos_fechados=True, boca_aberta=True)],
    }
    esquerda = {k: [pygame.transform.flip(f, True, False) for f in v] for k, v in direita.items()}
    return {1: direita, -1: esquerda}


# ---------------------------------------------------------------- cenário


def ceu():
    """Céu com gradiente, estrelas e a lua vermelha (camada que não se move)."""
    s = gradiente_vertical(c.LARGURA, c.ALTURA, c.CEU_TOPO, c.CEU_HORIZONTE)
    rnd = random.Random(7)
    for _ in range(110):
        x, y = rnd.randrange(c.LARGURA), rnd.randrange(int(c.ALTURA * 0.65))
        tom = rnd.randint(120, 230)
        s.set_at((x, y), (tom, tom, min(255, tom + 20)))
        if rnd.random() < 0.15:
            pygame.draw.circle(s, (tom, tom, 255), (x, y), 1)

    lx, ly, raio = 720, 120, 62
    luz = brilho(raio * 3, c.LUA_BRILHO, 70)
    s.blit(luz, (lx - raio * 3, ly - raio * 3))
    pygame.draw.circle(s, c.LUA, (lx, ly), raio)
    for dx, dy, r in ((-18, -14, 11), (20, 8, 15), (-6, 26, 8), (26, -24, 6)):
        pygame.draw.circle(s, (170, 24, 34), (lx + dx, ly + dy), r)
    pygame.draw.circle(s, c.LUA_BRILHO, (lx, ly), raio, 2)
    return s


def montanhas(cor, altura_base, variacao, semente, largura=c.LARGURA * 2):
    """Uma faixa de montanhas que se repete sem emenda, para o efeito de parallax."""
    rnd = random.Random(semente)
    s = superficie(largura, c.ALTURA)
    picos = []
    x = 0
    while x <= largura:
        picos.append((x, c.ALTURA - altura_base - rnd.randint(0, variacao)))
        x += rnd.randint(60, 140)
    picos[-1] = (largura, picos[0][1])  # mesma altura nas pontas para emendar
    pygame.draw.polygon(s, cor, [(0, c.ALTURA)] + picos + [(largura, c.ALTURA)])
    return s


def nevoa():
    s = superficie(c.LARGURA, 160)
    for y in range(160):
        alfa = int(70 * (y / 160) ** 1.5)
        pygame.draw.line(s, (90, 30, 70, alfa), (0, y), (c.LARGURA, y))
    return s


# ---------------------------------------------------------------- blocos


def bloco_terra(com_grama):
    t = c.TILE
    s = pygame.Surface((t, t))
    s.fill(c.TERRA)
    rnd = random.Random(3 if com_grama else 4)
    for _ in range(6):
        pygame.draw.circle(s, c.TERRA_ESCURA, (rnd.randrange(t), rnd.randrange(t)), rnd.randint(2, 4))
    if com_grama:
        pygame.draw.rect(s, c.GRAMA, (0, 0, t, 8))
        pygame.draw.line(s, c.GRAMA_CLARA, (0, 0), (t, 0), 2)
        for x in range(2, t, 6):
            pygame.draw.line(s, c.GRAMA, (x, 8), (x + 2, 12), 2)
    return s


def plataforma():
    t = c.TILE
    s = superficie(t, 14)
    pygame.draw.rect(s, (74, 50, 92), (0, 0, t, 14), border_radius=3)
    pygame.draw.rect(s, c.GRAMA_CLARA, (0, 0, t, 4), border_radius=2)
    pygame.draw.line(s, (54, 36, 70), (t // 2, 5), (t // 2, 13), 2)
    return s


def plataforma_movel(largura_tiles=3):
    t = c.TILE
    s = superficie(t * largura_tiles, 16)
    pygame.draw.rect(s, (60, 46, 90), s.get_rect(), border_radius=5)
    pygame.draw.rect(s, (150, 120, 220), (0, 0, s.get_width(), 4), border_radius=3)
    for x in range(10, s.get_width() - 4, 18):
        pygame.draw.circle(s, (190, 160, 255), (x, 10), 2)
    return s


def espinhos():
    t = c.TILE
    s = superficie(t, t)
    for i in range(4):
        x = i * t // 4
        pygame.draw.polygon(s, (176, 176, 196), [(x, t), (x + t // 8, t - 20), (x + t // 4, t)])
        pygame.draw.line(s, (230, 230, 245), (x + t // 8, t - 20), (x + t // 8, t - 12), 1)
    return s


# ---------------------------------------------------------------- itens


def osso(dourado=False):
    s = superficie(26, 14)
    cor = c.OURO if dourado else c.OSSO
    contorno = (200, 140, 30) if dourado else (176, 160, 140)
    pygame.draw.rect(s, cor, (6, 4, 14, 6))
    for x, y in ((5, 4), (5, 9), (21, 4), (21, 9)):
        pygame.draw.circle(s, cor, (x, y), 4)
    pygame.draw.rect(s, contorno, (6, 4, 14, 6), 1)
    return s


def coracao(cheio=True):
    s = superficie(22, 20)
    cor = c.VERMELHO if cheio else (70, 40, 70)
    pygame.draw.circle(s, cor, (6, 7), 6)
    pygame.draw.circle(s, cor, (15, 7), 6)
    pygame.draw.polygon(s, cor, [(1, 9), (21, 9), (11, 19)])
    if cheio:
        pygame.draw.circle(s, (255, 160, 170), (5, 5), 2)
    return s


def bandeira(ativa):
    s = superficie(28, 60)
    pygame.draw.rect(s, (120, 110, 140), (3, 4, 4, 56))
    cor = (120, 230, 150) if ativa else (90, 80, 110)
    pygame.draw.polygon(s, cor, [(7, 6), (27, 14), (7, 24)])
    if ativa:
        pygame.draw.circle(s, (210, 255, 220), (12, 14), 3)
    return s


# ---------------------------------------------------------------- inimigos


def sombra(fase):
    """Criatura que anda de um lado para o outro. Dá para pular em cima."""
    s = superficie(34, 28)
    achata = 2 if fase else 0
    pygame.draw.ellipse(s, (150, 70, 170), (0, 3 + achata, 34, 26 - achata))
    pygame.draw.ellipse(s, (30, 10, 36), (2, 5 + achata, 30, 22 - achata))
    pygame.draw.ellipse(s, (70, 26, 80), (6, 7 + achata, 22, 9))
    for ox in (11, 22):
        pygame.draw.circle(s, (255, 60, 70), (ox, 14 + achata), 4)
        pygame.draw.circle(s, (255, 210, 210), (ox + 1, 13 + achata), 1)
    pygame.draw.polygon(s, (26, 10, 30), [(4, 24), (8, 28), (12, 24)])
    pygame.draw.polygon(s, (26, 10, 30), [(22, 24), (26, 28), (30, 24)])
    return s


def sombra_esmagada():
    s = superficie(34, 28)
    pygame.draw.ellipse(s, (26, 10, 30), (0, 20, 34, 8))
    return s


def cuspidor(abrindo):
    """Monstro roxo cheio de espinhos que cospe bolas. Não dá para pular em cima."""
    s = superficie(48, 48)
    cx, cy = 24, 26
    for i in range(10):
        ang = math.radians(36 * i - 90)
        base1 = (cx + math.cos(ang - 0.18) * 16, cy + math.sin(ang - 0.18) * 16)
        base2 = (cx + math.cos(ang + 0.18) * 16, cy + math.sin(ang + 0.18) * 16)
        ponta = (cx + math.cos(ang) * 24, cy + math.sin(ang) * 24)
        pygame.draw.polygon(s, (130, 40, 190), [base1, base2, ponta])
    pygame.draw.circle(s, (70, 16, 104), (cx, cy), 17)
    pygame.draw.circle(s, c.ROXO, (cx, cy), 17, 2)
    for ox in (-7, 7):
        pygame.draw.circle(s, c.OURO, (cx + ox, cy - 5), 5)
        pygame.draw.circle(s, c.PRETO, (cx + ox, cy - 5), 2)
    boca = 9 if abrindo else 4
    pygame.draw.ellipse(s, c.PRETO, (cx - 7, cy + 4, 14, boca))
    return s


def orbe():
    s = superficie(20, 20)
    s.blit(brilho(10, c.ROXO, 140), (0, 0))
    pygame.draw.circle(s, (200, 110, 255), (10, 10), 6)
    pygame.draw.circle(s, (240, 210, 255), (8, 8), 2)
    return s


# ---------------------------------------------------------------- portal e casa


def desenhar_portal(destino, x, y, tempo):
    """Portal giratório que leva o pug para casa (desenhado a cada quadro)."""
    destino.blit(brilho(56, c.ROXO, 80), (x - 56, y - 56))
    for i in range(6):
        ang = tempo * 0.05 + i * math.pi / 3
        r = 26 + 4 * math.sin(tempo * 0.08 + i)
        px, py = x + math.cos(ang) * r * 0.7, y + math.sin(ang) * r
        pygame.draw.circle(destino, (220, 170, 255), (int(px), int(py)), 3)
    pygame.draw.ellipse(destino, (40, 10, 70), (x - 20, y - 32, 40, 64))
    pygame.draw.ellipse(destino, c.ROXO, (x - 20, y - 32, 40, 64), 3)
    pygame.draw.ellipse(destino, (120, 60, 200), (x - 12, y - 22, 24, 44), 2)


def cena_casa():
    """Cena final: o amanhecer, a casa e o dono esperando na porta."""
    s = gradiente_vertical(c.LARGURA, c.ALTURA, (255, 170, 120), (255, 226, 170))
    s.blit(brilho(160, (255, 240, 180), 120), (480 - 160, 330 - 160))
    pygame.draw.circle(s, (255, 236, 160), (480, 330), 70)
    for cor, base, var, semente in (((214, 140, 130), 170, 60, 11), ((170, 110, 120), 120, 40, 12)):
        s.blit(montanhas(cor, base, var, semente, c.LARGURA), (0, 0))
    pygame.draw.rect(s, (110, 160, 90), (0, 430, c.LARGURA, 110))
    pygame.draw.rect(s, (90, 140, 74), (0, 430, c.LARGURA, 6))

    # casa
    hx, hy = 560, 270
    pygame.draw.rect(s, (238, 214, 180), (hx, hy, 220, 160))
    pygame.draw.polygon(s, (170, 70, 60), [(hx - 20, hy), (hx + 110, hy - 90), (hx + 240, hy)])
    pygame.draw.rect(s, (120, 80, 50), (hx + 30, hy + 60, 60, 100), border_radius=4)
    pygame.draw.circle(s, (230, 190, 90), (hx + 80, hy + 112), 4)
    pygame.draw.rect(s, (255, 230, 150), (hx + 130, hy + 50, 60, 50))
    pygame.draw.rect(s, (150, 110, 80), (hx + 130, hy + 50, 60, 50), 4)
    pygame.draw.line(s, (150, 110, 80), (hx + 160, hy + 50), (hx + 160, hy + 100), 3)

    # dono, de braços abertos na porta
    dx, dy = hx + 60, hy + 70
    pygame.draw.rect(s, (60, 80, 140), (dx - 12, dy + 52, 10, 38))
    pygame.draw.rect(s, (60, 80, 140), (dx + 2, dy + 52, 10, 38))
    pygame.draw.rect(s, (220, 90, 80), (dx - 14, dy + 10, 28, 44), border_radius=6)
    pygame.draw.line(s, (220, 90, 80), (dx - 12, dy + 16), (dx - 34, dy + 2), 8)
    pygame.draw.line(s, (220, 90, 80), (dx + 12, dy + 16), (dx + 34, dy + 2), 8)
    for hx2 in (dx - 36, dx + 36):
        pygame.draw.circle(s, (230, 186, 150), (hx2, dy), 6)
    pygame.draw.circle(s, (230, 186, 150), (dx, dy - 4), 14)
    pygame.draw.arc(s, (70, 40, 30), (dx - 15, dy - 20, 30, 22), 0, math.pi, 7)
    pygame.draw.arc(s, (90, 50, 40), (dx - 6, dy - 2, 12, 8), math.pi, 2 * math.pi, 2)
    return s
