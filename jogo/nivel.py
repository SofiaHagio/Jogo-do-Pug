"""Transforma o mapa em texto de uma fase em blocos, inimigos e itens."""

import pygame

from . import config as c
from .entidades import Checkpoint, Cuspidor, Osso, PlataformaMovel, Sombra

T = c.TILE


class Nivel:
    def __init__(self, dados):
        self.nome = dados["nome"]
        self.dica = dados["dica"]
        self.mapa = dados["mapa"]
        self.colunas = len(self.mapa[0])
        self.linhas = len(self.mapa)
        self.largura_px = self.colunas * T

        self.sombras, self.cuspidores, self.moveis = [], [], []
        self.ossos, self.checkpoints, self.espinhos, self.finas = [], [], [], []
        self.inicio = (0, 0)
        self.portal = (0, 0)

        for ty, linha in enumerate(self.mapa):
            for tx, simbolo in enumerate(linha):
                x, y = tx * T, ty * T
                if simbolo == "P":
                    self.inicio = (x + 3, y + T - 28)
                elif simbolo == "H":
                    self.portal = (x + T // 2, y + T - 32)
                elif simbolo == "W":
                    self.sombras.append(Sombra(x, y))
                elif simbolo == "S":
                    self.cuspidores.append(Cuspidor(x, y))
                elif simbolo == "M":
                    self.moveis.append(PlataformaMovel(x, y))
                elif simbolo in "oG":
                    self.ossos.append(Osso(x, y, dourado=simbolo == "G"))
                elif simbolo == "C":
                    self.checkpoints.append(Checkpoint(x, y))
                elif simbolo == "^":
                    self.espinhos.append(pygame.Rect(x + 4, y + T - 16, T - 8, 16))
                elif simbolo == "=":
                    self.finas.append(pygame.Rect(x, y, T, 14))

        self.total_ossos = sum(1 for o in self.ossos if not o.dourado)
        self.retorno = self.inicio  # muda quando o pug passa por um checkpoint

    # ---------- consultas de colisão

    def simbolo(self, tx, ty):
        if 0 <= ty < self.linhas and 0 <= tx < self.colunas:
            return self.mapa[ty][tx]
        return "."

    def solido(self, tx, ty):
        if tx < 0 or tx >= self.colunas:
            return True  # as bordas da fase funcionam como parede
        return self.simbolo(tx, ty) == "#"

    def pisavel(self, tx, ty):
        return self.simbolo(tx, ty) in "#="

    def blocos_perto(self, rect):
        """Retângulos dos blocos sólidos em volta de um retângulo."""
        blocos = []
        for ty in range(rect.top // T - 1, rect.bottom // T + 2):
            for tx in range(rect.left // T - 1, rect.right // T + 2):
                if 0 <= tx < self.colunas and self.simbolo(tx, ty) == "#":
                    blocos.append(pygame.Rect(tx * T, ty * T, T, T))
        return blocos

    def apoios(self):
        """Superfícies que só seguram quem cai de cima: plataformas finas e móveis."""
        for fina in self.finas:
            yield fina, None
        for movel in self.moveis:
            yield movel.rect, movel
