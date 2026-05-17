"""Efeitos sonoros gerados por código (ondas simples), sem arquivos de áudio.

Se o computador não tiver saída de som, o jogo continua funcionando em silêncio.
"""

import array
import math
import random

import pygame

TAXA = 22050


def _onda(notas, forma="quadrada", volume=0.25, ruido=0.0):
    """Monta um som a partir de uma lista de (frequência_inicial, frequência_final, duração)."""
    amostras = array.array("h")
    fase = 0.0
    rnd = random.Random(1)
    for f_ini, f_fim, duracao in notas:
        total = int(TAXA * duracao)
        for i in range(total):
            t = i / total
            freq = f_ini + (f_fim - f_ini) * t
            fase += 2 * math.pi * freq / TAXA
            if forma == "quadrada":
                valor = 1.0 if math.sin(fase) >= 0 else -1.0
            elif forma == "triangulo":
                valor = 2 / math.pi * math.asin(math.sin(fase))
            else:
                valor = math.sin(fase)
            if ruido:
                valor = valor * (1 - ruido) + rnd.uniform(-1, 1) * ruido
            envelope = min(1.0, i / 200) * (1 - t) ** 1.5
            amostras.append(int(valor * envelope * volume * 32767))
    return amostras


class Sons:
    def __init__(self):
        self.ativo = False
        self.efeitos = {}
        try:
            pygame.mixer.init(TAXA, -16, 1, 512)
            self.ativo = pygame.mixer.get_init() is not None
        except pygame.error:
            return
        if not self.ativo:
            return
        receitas = {
            "pulo": _onda([(320, 640, 0.12)], "quadrada", 0.12),
            "osso": _onda([(880, 880, 0.06), (1320, 1320, 0.10)], "triangulo", 0.3),
            "dourado": _onda([(660, 660, 0.07), (880, 880, 0.07), (1320, 1760, 0.18)], "triangulo", 0.3),
            "esmagar": _onda([(220, 80, 0.14)], "quadrada", 0.18, ruido=0.3),
            "dano": _onda([(300, 90, 0.3)], "quadrada", 0.2, ruido=0.4),
            "cuspe": _onda([(500, 200, 0.12)], "seno", 0.25),
            "checkpoint": _onda([(523, 523, 0.08), (659, 659, 0.08), (784, 784, 0.16)], "triangulo", 0.28),
            "portal": _onda([(392, 784, 0.25), (523, 1046, 0.35)], "seno", 0.3),
            "menu": _onda([(660, 660, 0.05)], "triangulo", 0.2),
        }
        for nome, amostras in receitas.items():
            self.efeitos[nome] = pygame.mixer.Sound(buffer=amostras.tobytes())

    def tocar(self, nome):
        if self.ativo and nome in self.efeitos:
            self.efeitos[nome].play()
