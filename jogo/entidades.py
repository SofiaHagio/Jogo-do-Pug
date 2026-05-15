"""Personagens e objetos da fase: o pug, os inimigos, os itens e as partículas."""

import math
import random

import pygame

from . import config as c

T = c.TILE


# ---------------------------------------------------------------- pug


class Pug:
    LARGURA, ALTURA = 30, 28

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, self.LARGURA, self.ALTURA)
        self.pos_x, self.pos_y = float(x), float(y)
        self.vx = self.vy = 0.0
        self.no_chao = False
        self.direcao = 1
        self.coyote = 0
        self.buffer_pulo = 0
        self.invencivel = 0
        self.tempo_anim = 0
        self.plataforma = None  # plataforma móvel em que está em cima
        self.pulou = False  # avisa o jogo para tocar o som e soltar poeira
        self.pousou = False

    def reposicionar(self, x, y):
        self.pos_x, self.pos_y = float(x), float(y)
        self.rect.topleft = (x, y)
        self.vx = self.vy = 0
        self.plataforma = None

    # -------- entrada

    def apertou_pulo(self):
        self.buffer_pulo = c.BUFFER_PULO

    def soltou_pulo(self):
        if self.vy < 0:
            self.vy *= c.CORTE_PULO

    # -------- física

    def atualizar(self, esquerda, direita, nivel):
        self.pulou = self.pousou = False
        self.tempo_anim += 1
        if self.invencivel:
            self.invencivel -= 1

        alvo = (direita - esquerda) * c.VELOCIDADE
        if alvo:
            self.direcao = 1 if alvo > 0 else -1
            self.vx += max(-c.ACELERACAO, min(c.ACELERACAO, alvo - self.vx))
        else:
            self.vx *= c.ATRITO
            if abs(self.vx) < 0.1:
                self.vx = 0

        # pulo com "coyote time" e "buffer": mais justo para quem joga
        self.coyote = c.COYOTE if self.no_chao else max(0, self.coyote - 1)
        if self.buffer_pulo:
            self.buffer_pulo -= 1
            if self.coyote:
                self.vy = -c.FORCA_PULO
                self.coyote = self.buffer_pulo = 0
                self.plataforma = None
                self.pulou = True

        self.vy = min(c.QUEDA_MAXIMA, self.vy + c.GRAVIDADE)

        # anda junto com a plataforma móvel
        if self.plataforma:
            self.pos_x += self.plataforma.dx

        self._mover_x(nivel)
        self._mover_y(nivel)

    def _mover_x(self, nivel):
        self.pos_x += self.vx
        self.pos_x = max(0, min(self.pos_x, nivel.largura_px - self.LARGURA))
        self.rect.x = round(self.pos_x)
        for bloco in nivel.blocos_perto(self.rect):
            if self.rect.colliderect(bloco):
                if self.rect.centerx < bloco.centerx:
                    self.rect.right = bloco.left
                else:
                    self.rect.left = bloco.right
                self.pos_x = self.rect.x
                self.vx = 0

    def _mover_y(self, nivel):
        estava_no_chao = self.no_chao
        base_antes = self.rect.bottom
        self.pos_y += self.vy
        self.rect.y = round(self.pos_y)
        self.no_chao = False
        self.plataforma = None

        for bloco in nivel.blocos_perto(self.rect):
            if self.rect.colliderect(bloco):
                if self.vy > 0:
                    self.rect.bottom = bloco.top
                    self.no_chao = True
                else:
                    self.rect.top = bloco.bottom
                self.vy = 0
                self.pos_y = self.rect.y

        # plataformas finas e móveis só seguram quem vem de cima
        if self.vy >= 0:
            for apoio, movel in nivel.apoios():
                if (
                    self.rect.right > apoio.left
                    and self.rect.left < apoio.right
                    and base_antes <= apoio.top + 2
                    and self.rect.bottom >= apoio.top
                ):
                    self.rect.bottom = apoio.top
                    self.pos_y = self.rect.y
                    self.vy = 0
                    self.no_chao = True
                    self.plataforma = movel
                    break

        if self.no_chao and not estava_no_chao:
            self.pousou = True

    def quicar(self):
        self.vy = -c.QUIQUE
        self.no_chao = False
        self.plataforma = None

    # -------- desenho

    def quadro(self, frames):
        lado = frames[self.direcao]
        if self.invencivel > c.INVENCIVEL - 20:
            return lado["dano"][0]
        if not self.no_chao:
            return lado["subindo" if self.vy < 0 else "caindo"][0]
        if abs(self.vx) > 0.5:
            lista = lado["correndo"]
            return lista[(self.tempo_anim // 6) % len(lista)]
        if self.tempo_anim % 180 > 172:
            return lado["piscar"][0]
        return lado["parado"][(self.tempo_anim // 30) % 2]

    def visivel(self):
        return not (self.invencivel and (self.invencivel // 4) % 2)


# ---------------------------------------------------------------- inimigos


class Sombra:
    """Anda e vira quando encontra parede ou beirada. Morre se o pug pular em cima."""

    def __init__(self, x, y):
        self.rect = pygame.Rect(x + 3, y + T - 24, 30, 24)
        self.pos_x = float(self.rect.x)
        self.vx = -1.1
        self.vivo = True
        self.tempo_morto = 0
        self.tempo = random.randint(0, 30)

    def atualizar(self, nivel):
        self.tempo += 1
        if not self.vivo:
            self.tempo_morto += 1
            return
        self.pos_x += self.vx
        self.rect.x = round(self.pos_x)
        frente = self.rect.right if self.vx > 0 else self.rect.left - 1
        parede = nivel.solido(frente // T, self.rect.centery // T)
        sem_chao = not nivel.pisavel(frente // T, (self.rect.bottom + 2) // T)
        if parede or sem_chao:
            self.vx *= -1

    @property
    def sumiu(self):
        return not self.vivo and self.tempo_morto > 40


class Cuspidor:
    """Fica parado e cospe bolas em arco na direção do pug. Encostar machuca."""

    ALCANCE = 430
    INTERVALO = 110

    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 2, y + T - 40, 40, 40)
        self.timer = random.randint(0, self.INTERVALO)
        self.abrindo = 0

    def atualizar(self, pug, orbes):
        self.timer += 1
        if self.abrindo:
            self.abrindo -= 1
        dx = pug.rect.centerx - self.rect.centerx
        if abs(dx) > self.ALCANCE or self.timer < self.INTERVALO:
            return False
        self.timer = 0
        self.abrindo = 16
        voo = 55  # quadros até chegar perto do pug
        dy = pug.rect.centery - self.rect.centery
        vx = max(-6, min(6, dx / voo))
        vy = max(-9, min(3, (dy - 0.5 * Orbe.GRAVIDADE * voo * voo) / voo))
        orbes.append(Orbe(self.rect.centerx, self.rect.top + 12, vx, vy))
        return True


class Orbe:
    GRAVIDADE = 0.15

    def __init__(self, x, y, vx, vy):
        self.x, self.y, self.vx, self.vy = float(x), float(y), vx, vy
        self.rect = pygame.Rect(0, 0, 12, 12)
        self.rect.center = (x, y)
        self.ativo = True

    def atualizar(self, nivel):
        self.x += self.vx
        self.vy += self.GRAVIDADE
        self.y += self.vy
        self.rect.center = (round(self.x), round(self.y))
        if self.y > c.ALTURA + 40 or nivel.solido(int(self.x) // T, int(self.y) // T):
            self.ativo = False


class PlataformaMovel:
    LARGURA_TILES = 3
    PERCURSO = 5 * T

    def __init__(self, x, y):
        self.inicio = x
        self.rect = pygame.Rect(x, y + 4, T * self.LARGURA_TILES, 16)
        self.t = 0.0
        self.dx = 0

    def atualizar(self):
        self.t += 0.012
        nova_x = self.inicio + (1 - math.cos(self.t)) / 2 * self.PERCURSO
        self.dx = round(nova_x) - self.rect.x
        self.rect.x = round(nova_x)


# ---------------------------------------------------------------- itens


class Osso:
    def __init__(self, x, y, dourado=False):
        self.rect = pygame.Rect(x + 5, y + 11, 26, 14)
        self.dourado = dourado
        self.fase = random.random() * math.tau
        self.coletado = False


class Checkpoint:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x + 4, y + T - 60, 28, 60)
        self.ativo = False
