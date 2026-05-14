"""Personagens e objetos da fase: o pug, os inimigos, os itens e as partículas."""

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
