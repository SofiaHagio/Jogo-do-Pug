"""Laço principal: estados do jogo, regras da fase e desenho de cada quadro."""

import math
import random
import sys

import pygame

from . import arte, recorde
from . import config as c
from .entidades import Particulas, Pug
from .fases import FASES
from .nivel import Nivel
from .som import Sons

T = c.TILE

MENU, INTRO, JOGANDO, PAUSA, FASE_COMPLETA, GAME_OVER, VITORIA = range(7)
TECLAS_PULO = (pygame.K_SPACE, pygame.K_UP, pygame.K_w)


class Jogo:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(c.TITULO)
        self.tela = pygame.display.set_mode((c.LARGURA, c.ALTURA))
        self.mundo = pygame.Surface((c.LARGURA, c.ALTURA))
        self.relogio = pygame.time.Clock()
        self.sons = Sons()
        self._carregar_arte()

        self.estado = MENU
        self.tempo_global = 0
        self.recorde = recorde.carregar()
        self.fase_atual = 0
        self.pontos = 0
        self.nivel = None
        self.camera_x = 0.0

    # ================================================================ preparação

    def _carregar_arte(self):
        self.f_titulo = arte.fonte(110)
        self.f_grande = arte.fonte(64)
        self.f_media = arte.fonte(36)
        self.f_pequena = arte.fonte(26)

        self.frames_pug = arte.frames_pug()
        self.img_ceu = arte.ceu()
        self.camadas = [
            (arte.montanhas(c.MONTANHAS[0], 150, 140, 1), 0.10),
            (arte.montanhas(c.MONTANHAS[1], 90, 110, 2), 0.25),
            (arte.montanhas(c.MONTANHAS[2], 40, 70, 3), 0.45),
        ]
        self.img_nevoa = arte.nevoa()
        self.img_terra = arte.bloco_terra(False)
        self.img_grama = arte.bloco_terra(True)
        self.img_fina = arte.plataforma()
        self.img_movel = arte.plataforma_movel()
        self.img_espinho = arte.espinhos()
        self.img_osso = arte.osso()
        self.img_osso_dourado = arte.osso(dourado=True)
        self.img_brilho_ouro = arte.brilho(26, c.OURO, 90)
        self.img_coracao = arte.coracao(True)
        self.img_coracao_vazio = arte.coracao(False)
        self.img_bandeira = {False: arte.bandeira(False), True: arte.bandeira(True)}
        self.img_sombra = [arte.sombra(0), arte.sombra(1)]
        self.img_sombra_morta = arte.sombra_esmagada()
        self.img_cuspidor = {False: arte.cuspidor(False), True: arte.cuspidor(True)}
        self.img_orbe = arte.orbe()
        self.img_casa = None  # montada só quando o jogador chega ao fim

    # ================================================================ fases

    def iniciar_fase(self, indice, pontos_iniciais):
        self.fase_atual = indice
        self.pontos = self.pontos_inicio_fase = pontos_iniciais
        self.nivel = Nivel(FASES[indice])
        self.pug = Pug(*self.nivel.inicio)
        self.vidas = c.VIDAS
        self.orbes = []
        self.particulas = Particulas()
        self.ossos_pegos = 0
        self.pegou_dourado = False
        self.quadros_fase = 0
        self.tremor = 0
        self.camera_x = max(0, self.pug.rect.centerx - c.LARGURA * 0.4)
        self.timer_estado = 0
        self.estado = INTRO

    def concluir_fase(self):
        segundos = self.quadros_fase // c.FPS
        self.bonus_tempo = max(0, c.BONUS_TEMPO_MAX - segundos * 2)
        self.pontos += self.bonus_tempo
        self.segundos_fase = segundos
        self.sons.tocar("portal")
        self.particulas.emitir(*self.nivel.portal, c.ROXO, 40, 4, 60)
        self.timer_estado = 0
        self.estado = FASE_COMPLETA

    def proxima_fase(self):
        if self.fase_atual + 1 < len(FASES):
            self.iniciar_fase(self.fase_atual + 1, self.pontos)
        else:
            self.novo_recorde = recorde.salvar(self.pontos)
            self.recorde = recorde.carregar()
            if self.img_casa is None:
                self.img_casa = arte.cena_casa()
            self.timer_estado = 0
            self.estado = VITORIA

    # ================================================================ laço principal

    def rodar(self):
        while True:
            self.tratar_eventos()
            self.atualizar()
            self.desenhar()
            pygame.display.flip()
            self.relogio.tick(c.FPS)

    def sair(self):
        pygame.quit()
        sys.exit()

    def tratar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.sair()
            if evento.type == pygame.KEYDOWN:
                self.tecla(evento.key)
            if evento.type == pygame.KEYUP and evento.key in TECLAS_PULO and self.estado == JOGANDO:
                self.pug.soltou_pulo()

    def tecla(self, k):
        confirmar = k in (pygame.K_RETURN, pygame.K_KP_ENTER)
        if self.estado == MENU:
            if confirmar or k == pygame.K_SPACE:
                self.sons.tocar("menu")
                self.iniciar_fase(0, 0)
            elif k in (pygame.K_ESCAPE, pygame.K_q):
                self.sair()
        elif self.estado == INTRO:
            if confirmar or k in TECLAS_PULO:
                self.estado = JOGANDO
        elif self.estado == JOGANDO:
            if k in TECLAS_PULO:
                self.pug.apertou_pulo()
            elif k in (pygame.K_p, pygame.K_ESCAPE):
                self.estado = PAUSA
        elif self.estado == PAUSA:
            if k in (pygame.K_p, pygame.K_ESCAPE) or confirmar:
                self.estado = JOGANDO
            elif k == pygame.K_q:
                self.estado = MENU
        elif self.estado == FASE_COMPLETA:
            if confirmar and self.timer_estado > 30:
                self.proxima_fase()
        elif self.estado == GAME_OVER:
            if k == pygame.K_r or confirmar:
                self.iniciar_fase(self.fase_atual, self.pontos_inicio_fase)
            elif k in (pygame.K_q, pygame.K_ESCAPE):
                self.estado = MENU
        elif self.estado == VITORIA:
            if confirmar and self.timer_estado > 60:
                self.estado = MENU

    # ================================================================ regras

    def atualizar(self):
        self.tempo_global += 1
        self.timer_estado = getattr(self, "timer_estado", 0) + 1
        if self.estado == INTRO and self.timer_estado > 150:
            self.estado = JOGANDO
        if self.estado == JOGANDO:
            self.atualizar_fase()
        elif self.estado in (FASE_COMPLETA, GAME_OVER) and self.nivel:
            self.particulas.atualizar()

    def atualizar_fase(self):
        nivel, pug = self.nivel, self.pug
        self.quadros_fase += 1
        if self.tremor:
            self.tremor -= 1

        for movel in nivel.moveis:
            movel.atualizar()

        teclas = pygame.key.get_pressed()
        esquerda = teclas[pygame.K_LEFT] or teclas[pygame.K_a]
        direita = teclas[pygame.K_RIGHT] or teclas[pygame.K_d]
        pug.atualizar(esquerda, direita, nivel)
        if pug.pulou:
            self.sons.tocar("pulo")
            self.particulas.poeira(pug.rect.centerx, pug.rect.bottom)
        if pug.pousou:
            self.particulas.poeira(pug.rect.centerx, pug.rect.bottom)

        for sombra in nivel.sombras:
            sombra.atualizar(nivel)
        nivel.sombras = [s for s in nivel.sombras if not s.sumiu]
        for cusp in nivel.cuspidores:
            if cusp.atualizar(pug, self.orbes) and self._na_tela(cusp.rect):
                self.sons.tocar("cuspe")
        for orbe in self.orbes:
            orbe.atualizar(nivel)
        self.orbes = [o for o in self.orbes if o.ativo]
        self.particulas.atualizar()

        self.checar_coletas()
        self.checar_perigos()

        px, py = nivel.portal
        if math.hypot(pug.rect.centerx - px, pug.rect.centery - py) < 30:
            self.concluir_fase()

        alvo = pug.rect.centerx - c.LARGURA * 0.4
        self.camera_x += (alvo - self.camera_x) * 0.12
        self.camera_x = max(0, min(self.camera_x, nivel.largura_px - c.LARGURA))

    def checar_coletas(self):
        pug = self.pug
        for osso in self.nivel.ossos:
            if not osso.coletado and pug.rect.colliderect(osso.rect):
                osso.coletado = True
                if osso.dourado:
                    self.pegou_dourado = True
                    self.pontos += c.PONTOS_OSSO_DOURADO
                    self.sons.tocar("dourado")
                    self.particulas.emitir(*osso.rect.center, c.OURO, 24, 3.5, 45)
                else:
                    self.ossos_pegos += 1
                    self.pontos += c.PONTOS_OSSO
                    self.sons.tocar("osso")
                    self.particulas.emitir(*osso.rect.center, c.OSSO, 8, 2, 25, 2)

        for cp in self.nivel.checkpoints:
            if not cp.ativo and pug.rect.colliderect(cp.rect):
                cp.ativo = True
                self.nivel.retorno = (cp.rect.x, cp.rect.bottom - pug.ALTURA)
                self.sons.tocar("checkpoint")
                self.particulas.emitir(cp.rect.centerx, cp.rect.top + 14, (120, 230, 150), 16, 2.5, 40)

    def checar_perigos(self):
        pug, nivel = self.pug, self.nivel
        if pug.rect.top > c.ALTURA:
            self.levar_dano(caiu=True)
            return

        for sombra in nivel.sombras:
            if sombra.vivo and pug.rect.colliderect(sombra.rect):
                if pug.vy > 0 and pug.rect.bottom - sombra.rect.top < 16:
                    sombra.vivo = False
                    pug.quicar()
                    self.pontos += c.PONTOS_INIMIGO
                    self.sons.tocar("esmagar")
                    self.particulas.emitir(sombra.rect.centerx, sombra.rect.centery, (90, 30, 100), 14, 3, 30)
                else:
                    self.levar_dano()
                    return

        perigos = [cusp.rect.inflate(-10, -10) for cusp in nivel.cuspidores] + nivel.espinhos
        for orbe in self.orbes:
            if pug.rect.colliderect(orbe.rect) and not pug.invencivel:
                orbe.ativo = False
                self.levar_dano()
                return
        if any(pug.rect.colliderect(p) for p in perigos):
            self.levar_dano()

    def levar_dano(self, caiu=False):
        pug = self.pug
        if pug.invencivel and not caiu:
            return
        self.vidas -= 1
        self.tremor = 14
        self.sons.tocar("dano")
        self.particulas.emitir(pug.rect.centerx, pug.rect.centery, c.VERMELHO, 12, 3, 30)
        pug.invencivel = c.INVENCIVEL
        if caiu:
            pug.reposicionar(*self.nivel.retorno)
            self.camera_x = max(0, min(pug.rect.centerx - c.LARGURA * 0.4, self.nivel.largura_px - c.LARGURA))
        else:
            pug.vy = -6
            pug.vx = -pug.direcao * 4
        if self.vidas <= 0:
            self.novo_recorde = recorde.salvar(self.pontos)
            self.recorde = recorde.carregar()
            self.timer_estado = 0
            self.estado = GAME_OVER

    def _na_tela(self, rect):
        return -60 < rect.x - self.camera_x < c.LARGURA + 60

    # ================================================================ desenho

    def desenhar(self):
        if self.estado == MENU:
            self.desenhar_menu()
        elif self.estado == VITORIA:
            self.desenhar_vitoria()
        else:
            self.desenhar_mundo()
            dx = random.randint(-4, 4) if self.tremor else 0
            dy = random.randint(-3, 3) if self.tremor else 0
            self.tela.fill(c.PRETO)
            self.tela.blit(self.mundo, (dx, dy))
            self.desenhar_hud()
            if self.estado == INTRO:
                self.desenhar_intro()
            elif self.estado == PAUSA:
                self.painel("PAUSA", ["P ou Enter para continuar", "Q para voltar ao menu"])
            elif self.estado == FASE_COMPLETA:
                self.desenhar_fase_completa()
            elif self.estado == GAME_OVER:
                self.desenhar_game_over()

    # ---------- cenário

    def desenhar_fundo(self, destino, camera_x):
        destino.blit(self.img_ceu, (0, 0))
        for camada, fator in self.camadas:
            largura = camada.get_width()
            x = -(camera_x * fator) % largura
            destino.blit(camada, (x - largura, 0))
            destino.blit(camada, (x, 0))
        destino.blit(self.img_nevoa, (0, c.ALTURA - self.img_nevoa.get_height()))

    def desenhar_mundo(self):
        m, nivel, cam = self.mundo, self.nivel, int(self.camera_x)
        self.desenhar_fundo(m, cam)

        inicio = max(0, cam // T - 1)
        fim = min(nivel.colunas, (cam + c.LARGURA) // T + 2)
        for ty, linha in enumerate(nivel.mapa):
            for tx in range(inicio, fim):
                simbolo = linha[tx]
                x, y = tx * T - cam, ty * T
                if simbolo == "#":
                    topo = ty == 0 or nivel.mapa[ty - 1][tx] != "#"
                    m.blit(self.img_grama if topo else self.img_terra, (x, y))
                elif simbolo == "=":
                    m.blit(self.img_fina, (x, y))
                elif simbolo == "^":
                    m.blit(self.img_espinho, (x, y))

        for movel in nivel.moveis:
            m.blit(self.img_movel, (movel.rect.x - cam, movel.rect.y))
        for cp in nivel.checkpoints:
            m.blit(self.img_bandeira[cp.ativo], (cp.rect.x - cam, cp.rect.y))

        t = self.tempo_global
        for osso in nivel.ossos:
            if osso.coletado or not self._na_tela(osso.rect):
                continue
            bob = math.sin(t * 0.08 + osso.fase) * 3
            if osso.dourado:
                m.blit(self.img_brilho_ouro, (osso.rect.centerx - 26 - cam, osso.rect.centery - 26 + bob))
            img = self.img_osso_dourado if osso.dourado else self.img_osso
            m.blit(img, (osso.rect.x - cam, osso.rect.y + bob))

        arte.desenhar_portal(m, nivel.portal[0] - cam, nivel.portal[1], t)

        for sombra in nivel.sombras:
            if sombra.vivo:
                img = self.img_sombra[(sombra.tempo // 15) % 2]
                if sombra.vx > 0:
                    img = pygame.transform.flip(img, True, False)
            else:
                img = self.img_sombra_morta.copy()
                img.set_alpha(max(0, 255 - sombra.tempo_morto * 6))
            m.blit(img, (sombra.rect.x - 2 - cam, sombra.rect.bottom - 28))
        for cusp in nivel.cuspidores:
            m.blit(self.img_cuspidor[cusp.abrindo > 0], (cusp.rect.x - 4 - cam, cusp.rect.y - 6))
        for orbe in self.orbes:
            m.blit(self.img_orbe, (orbe.rect.centerx - 10 - cam, orbe.rect.centery - 10))

        if self.pug.visivel():
            m.blit(self.pug.quadro(self.frames_pug), (self.pug.rect.centerx - 22 - cam, self.pug.rect.bottom - 35))
        self.particulas.desenhar(m, cam)

    # ---------- interface

    def texto(self, fonte, msg, cor, centro=None, topo_esq=None, sombra=True):
        img = fonte.render(msg, True, cor)
        rect = img.get_rect()
        if centro:
            rect.center = centro
        else:
            rect.topleft = topo_esq
        if sombra:
            self.tela.blit(fonte.render(msg, True, c.PRETO), rect.move(2, 2))
        self.tela.blit(img, rect)
        return rect

    def desenhar_hud(self):
        for i in range(c.VIDAS):
            self.tela.blit(self.img_coracao if i < self.vidas else self.img_coracao_vazio, (16 + i * 28, 16))
        self.tela.blit(self.img_osso, (110, 19))
        self.texto(self.f_pequena, f"{self.ossos_pegos}/{self.nivel.total_ossos}", c.TEXTO, topo_esq=(142, 18))
        if self.pegou_dourado:
            self.tela.blit(self.img_osso_dourado, (200, 19))
        self.texto(self.f_pequena, f"Fase {self.fase_atual + 1} · {self.nivel.nome}", c.TEXTO_FRACO, centro=(c.LARGURA // 2, 26))
        self.texto(self.f_media, f"{self.pontos:05d}", c.OURO, topo_esq=(c.LARGURA - 110, 14))

    def escurecer(self, alfa=150):
        veu = pygame.Surface((c.LARGURA, c.ALTURA), pygame.SRCALPHA)
        veu.fill((8, 4, 14, alfa))
        self.tela.blit(veu, (0, 0))

    def painel(self, titulo, linhas, cor_titulo=c.TEXTO):
        self.escurecer()
        caixa = pygame.Rect(0, 0, 520, 110 + 40 * len(linhas))
        caixa.center = (c.LARGURA // 2, c.ALTURA // 2)
        pygame.draw.rect(self.tela, (26, 14, 40), caixa, border_radius=16)
        pygame.draw.rect(self.tela, (96, 60, 140), caixa, 2, border_radius=16)
        self.texto(self.f_grande, titulo, cor_titulo, centro=(caixa.centerx, caixa.top + 52))
        for i, linha in enumerate(linhas):
            self.texto(self.f_pequena, linha, c.TEXTO, centro=(caixa.centerx, caixa.top + 112 + i * 40), sombra=False)

    def desenhar_intro(self):
        alfa = 1 if self.timer_estado < 110 else max(0, 1 - (self.timer_estado - 110) / 40)
        faixa = pygame.Surface((c.LARGURA, 150), pygame.SRCALPHA)
        faixa.fill((8, 4, 14, int(180 * alfa)))
        self.tela.blit(faixa, (0, c.ALTURA // 2 - 75))
        if alfa > 0.05:
            self.texto(self.f_pequena, f"FASE {self.fase_atual + 1}", c.OURO, centro=(c.LARGURA // 2, c.ALTURA // 2 - 40))
            self.texto(self.f_grande, self.nivel.nome, c.TEXTO, centro=(c.LARGURA // 2, c.ALTURA // 2 + 2))
            self.texto(self.f_pequena, self.nivel.dica, c.TEXTO_FRACO, centro=(c.LARGURA // 2, c.ALTURA // 2 + 44))

    def desenhar_fase_completa(self):
        linhas = [
            f"Ossos: {self.ossos_pegos} de {self.nivel.total_ossos}",
            "Osso dourado: " + ("encontrado!" if self.pegou_dourado else "ficou para trás"),
            f"Tempo: {self.segundos_fase // 60}:{self.segundos_fase % 60:02d}   (bônus +{self.bonus_tempo})",
            f"Pontuação: {self.pontos}",
            "Enter para continuar",
        ]
        self.painel("Fase concluída!", linhas, c.OURO)

    def desenhar_game_over(self):
        linhas = [f"Pontuação: {self.pontos}", f"Recorde: {self.recorde}", "R para tentar de novo", "Q para voltar ao menu"]
        self.painel("O pug se perdeu...", linhas, c.VERMELHO)

    def desenhar_menu(self):
        t = self.tempo_global
        self.desenhar_fundo(self.tela, t * 1.5)
        chao_y = c.ALTURA - 70
        for x in range(-T, c.LARGURA + T, T):
            self.tela.blit(self.img_grama, (x - int(t * 1.5) % T, chao_y))
            self.tela.blit(self.img_terra, (x - int(t * 1.5) % T, chao_y + T))

        quadros = self.frames_pug[1]["correndo"]
        pug = pygame.transform.scale_by(quadros[(t // 6) % len(quadros)], 2)
        self.tela.blit(pug, (c.LARGURA // 2 - 44, chao_y - 70 + abs(math.sin(t * 0.17)) * -4))

        self.texto(self.f_titulo, "PUG", c.OURO, centro=(c.LARGURA // 2, 110))
        self.texto(self.f_grande, "e a Lua Vermelha", c.TEXTO, centro=(c.LARGURA // 2, 178))
        if (t // 30) % 2 == 0:
            self.texto(self.f_media, "Pressione Enter para começar", c.TEXTO, centro=(c.LARGURA // 2, 262))
        self.texto(
            self.f_pequena,
            "Setas ou A/D: andar   ·   Espaço ou W: pular   ·   P: pausa",
            c.TEXTO_FRACO,
            centro=(c.LARGURA // 2, 310),
        )
        if self.recorde:
            self.texto(self.f_pequena, f"Recorde: {self.recorde}", c.OURO, centro=(c.LARGURA // 2, 345))

    def desenhar_vitoria(self):
        t = self.timer_estado
        self.tela.blit(self.img_casa, (0, 0))
        quadros = self.frames_pug[1]
        x = min(470, 40 + t * 3)
        img = quadros["correndo"][(t // 6) % 4] if x < 470 else quadros["parado"][(t // 30) % 2]
        self.tela.blit(pygame.transform.scale_by(img, 2), (x, 430 - 70))
        if x >= 470:
            for i in range(3):
                fase = (t * 0.8 + i * 40) % 120
                coracao = self.img_coracao.copy()
                coracao.set_alpha(int(255 * (1 - fase / 120)))
                self.tela.blit(coracao, (540 + i * 22, 340 - fase))

        self.texto(self.f_grande, "O pug chegou em casa!", (120, 50, 60), centro=(c.LARGURA // 2, 70), sombra=False)
        self.texto(self.f_media, f"Pontuação final: {self.pontos}", (90, 40, 50), centro=(c.LARGURA // 2, 125), sombra=False)
        if getattr(self, "novo_recorde", False):
            self.texto(self.f_pequena, "Novo recorde!", (190, 80, 40), centro=(c.LARGURA // 2, 160), sombra=False)
        if t > 60:
            self.texto(self.f_pequena, "Enter para voltar ao menu", (110, 60, 70), centro=(c.LARGURA // 2, 195), sombra=False)
