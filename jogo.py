import pygame
import sys
import math

pygame.init()

# configuracoes da tela
LARGURA = 800
ALTURA = 500
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo em Python")
clock = pygame.time.Clock()
FPS = 60

# cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERMELHO = (200, 50, 50)
VERDE = (50, 180, 80)
AMARELO = (255, 215, 0)
LARANJA = (255, 140, 0)

# fontes
fonte_grande = pygame.font.SysFont("Arial", 48, bold=True)
fonte_media = pygame.font.SysFont("Arial", 30)
fonte_pequena = pygame.font.SysFont("Arial", 22)

# variaveis do jogador
jogador_x = 100
jogador_y = 300
jogador_largura = 40
jogador_altura = 50
jogador_vel_y = 0
jogador_no_chao = False
jogador_velocidade = 5
gravidade = 0.5
forca_pulo = -12
vidas = 3
pontos = 0
invencivel = 0  # frames de quando leva dano

# plataformas: x, y, largura, altura
plataformas = [
    [0, 460, 800, 40],
    [100, 360, 150, 20],
    [320, 290, 130, 20],
    [500, 220, 160, 20],
    [650, 330, 120, 20],
    [200, 180, 140, 20],
    [400, 140, 100, 20],
]

# moedas: x, y, coletada
moedas = [
    [160, 330, False],
    [370, 260, False],
    [560, 190, False],
    [700, 300, False],
    [250, 150, False],
    [440, 110, False],
]

# monstros que andam: x, y, direcao, velocidade
inimigos = [
    [320, 262, 1, 2],
    [650, 302, 1, 1],
]

# monstro que cospe: x, y, timer, intervalo
inimigo_cuspidor = [500, 185, 0, 90]

# bolinhas no ar: x, y, vel_x, vel_y
bolinhas = []

# portal de saida
portal_x = 730
portal_y = 130
portal_largura = 40
portal_altura = 60

# estado do jogo
estado = "inicio"


# desenho do cenário
def desenhar_fundo():
    tela.fill((10, 5, 25))

    # lua
    pygame.draw.circle(tela, (160, 0, 0), (680, 60), 40)
    pygame.draw.circle(tela, (220, 30, 30), (680, 60), 40, 3)
    pygame.draw.circle(tela, (10, 5, 25), (696, 50), 30)  # recorte pra virar crescente
    # sangue escorrendo da lua
    pygame.draw.ellipse(tela, (180, 0, 0), (658, 88, 7, 14))
    pygame.draw.ellipse(tela, (180, 0, 0), (672, 92, 5, 10))
    pygame.draw.ellipse(tela, (180, 0, 0), (648, 85, 6, 18))
    pygame.draw.circle(tela, (180, 0, 0), (661, 103), 4)
    pygame.draw.circle(tela, (180, 0, 0), (651, 104), 3)

    # estrelas
    estrelas = [
        (50, 30), (120, 15), (200, 45), (300, 20), (370, 55),
        (450, 10), (530, 40), (600, 25), (760, 15),
        (80, 80), (160, 65), (250, 90), (420, 75), (700, 110),
    ]
    for ex, ey in estrelas:
        pygame.draw.circle(tela, (200, 200, 220), (ex, ey), 2)

    # montanhas de fundo
    montanha1 = [(0, 500), (0, 320), (80, 200), (160, 320),
                 (240, 230), (320, 320), (400, 180), (480, 320),
                 (560, 250), (640, 320), (720, 210), (800, 320), (800, 500)]
    pygame.draw.polygon(tela, (20, 10, 40), montanha1)

    montanha2 = [(0, 500), (0, 380), (60, 300), (140, 380),
                 (220, 310), (300, 390), (380, 330), (460, 390),
                 (540, 320), (620, 400), (700, 340), (800, 400), (800, 500)]
    pygame.draw.polygon(tela, (15, 8, 30), montanha2)

# desenho das plataformas
def desenhar_plataformas():
    for p in plataformas:
        pygame.draw.rect(tela, VERDE, (p[0], p[1], p[2], p[3]))
        pygame.draw.rect(tela, PRETO, (p[0], p[1], p[2], p[3]), 2)


# desenho das moedas nao coletadas
def desenhar_moedas():
    for m in moedas:
        if not m[2]:
            pygame.draw.circle(tela, AMARELO, (m[0], m[1]), 12)
            pygame.draw.circle(tela, LARANJA, (m[0], m[1]), 12, 3)


# desenho dos espinhos dos monstros
def espinhos(cx, cy, raio, qtd, tamanho, cor):
    for i in range(qtd):
        ang = (360 / qtd) * i
        rad = math.radians(ang)
        b1 = (cx + math.cos(math.radians(ang - 8)) * raio, cy + math.sin(math.radians(ang - 8)) * raio)
        b2 = (cx + math.cos(math.radians(ang + 8)) * raio, cy + math.sin(math.radians(ang + 8)) * raio)
        p  = (cx + math.cos(rad) * (raio + tamanho),       cy + math.sin(rad) * (raio + tamanho))
        pygame.draw.polygon(tela, cor, [b1, b2, p])


# desenho dos monstros que andam
def desenhar_inimigos():
    for i in inimigos:
        cx, cy = i[0] + 18, i[1] + 18
        espinhos(cx, cy, 16, 8, 10, (180, 0, 0))
        pygame.draw.circle(tela, (140, 0, 20), (cx, cy), 16)   # corpo
        pygame.draw.circle(tela, VERMELHO, (cx, cy), 16, 2)    # borda
        pygame.draw.circle(tela, (255, 50, 50), (cx - 6, cy - 4), 5)  # olho esq
        pygame.draw.circle(tela, (255, 50, 50), (cx + 6, cy - 4), 5)  # olho dir
        pygame.draw.circle(tela, PRETO, (cx - 6, cy - 4), 2)
        pygame.draw.circle(tela, PRETO, (cx + 6, cy - 4), 2)
        pygame.draw.line(tela, PRETO, (cx - 10, cy - 10), (cx - 3, cy - 7), 2)  # sobrancelha esq
        pygame.draw.line(tela, PRETO, (cx + 10, cy - 10), (cx + 3, cy - 7), 2)  # sobrancelha dir
        pygame.draw.arc(tela, PRETO, (cx - 7, cy + 2, 14, 8), math.pi, 2 * math.pi, 2)  # boca
        pygame.draw.line(tela, BRANCO, (cx - 4, cy + 6), (cx - 4, cy + 10), 2)  # dente esq
        pygame.draw.line(tela, BRANCO, (cx, cy + 6), (cx, cy + 10), 2)           # dente meio
        pygame.draw.line(tela, BRANCO, (cx + 4, cy + 6), (cx + 4, cy + 10), 2)  # dente dir


# desenho do monstro que cospe
def desenhar_cuspidor():
    cx, cy = inimigo_cuspidor[0] + 22, inimigo_cuspidor[1] + 22
    espinhos(cx, cy, 20, 10, 14, (120, 0, 160))
    pygame.draw.circle(tela, (60, 0, 90), (cx, cy), 20)    # corpo
    pygame.draw.circle(tela, (200, 0, 220), (cx, cy), 20, 3)  # borda
    pygame.draw.circle(tela, AMARELO, (cx - 8, cy - 5), 7)  # olho esq
    pygame.draw.circle(tela, AMARELO, (cx + 8, cy - 5), 7)  # olho dir
    pygame.draw.circle(tela, PRETO, (cx - 8, cy - 5), 3)
    pygame.draw.circle(tela, PRETO, (cx + 8, cy - 5), 3)
    pygame.draw.circle(tela, BRANCO, (cx - 6, cy - 7), 2)   # brilho olho esq
    pygame.draw.circle(tela, BRANCO, (cx + 10, cy - 7), 2)  # brilho olho dir
    pygame.draw.line(tela, PRETO, (cx - 14, cy - 13), (cx - 4, cy - 9), 3)  # sobrancelha esq
    pygame.draw.line(tela, PRETO, (cx + 14, cy - 13), (cx + 4, cy - 9), 3)  # sobrancelha dir
    pygame.draw.ellipse(tela, PRETO, (cx - 10, cy + 6, 20, 12))  # boca
    pygame.draw.line(tela, BRANCO, (cx - 6, cy + 6), (cx - 6, cy + 14), 2)  # dente esq
    pygame.draw.line(tela, BRANCO, (cx, cy + 6), (cx, cy + 14), 2)           # dente meio
    pygame.draw.line(tela, BRANCO, (cx + 6, cy + 6), (cx + 6, cy + 14), 2)  # dente dir


# desenho das bolinhas no ar
def desenhar_bolinhas():
    for b in bolinhas:
        pygame.draw.circle(tela, (180, 0, 220), (int(b[0]), int(b[1])), 8)
        pygame.draw.circle(tela, (220, 100, 255), (int(b[0]) - 2, int(b[1]) - 2), 3)


# desenho do pug
def desenhar_pug(x, y):
    cor_corpo = (180, 140, 100)
    cor_focinho = (130, 90, 60)
    cor_orelha = (110, 70, 40)

    pygame.draw.ellipse(tela, cor_corpo, (x + 4, y + 20, 34, 26))    # corpo
    pygame.draw.circle(tela, cor_corpo, (x + 20, y + 18), 18)         # cabeca
    pygame.draw.ellipse(tela, cor_orelha, (x, y + 2, 14, 18))         # orelha esq
    pygame.draw.ellipse(tela, cor_orelha, (x + 28, y + 2, 14, 18))    # orelha dir
    pygame.draw.ellipse(tela, cor_focinho, (x + 11, y + 20, 18, 12))  # focinho
    pygame.draw.ellipse(tela, PRETO, (x + 14, y + 20, 12, 7))         # nariz
    pygame.draw.circle(tela, (60, 30, 10), (x + 16, y + 23), 2)       # narina esq
    pygame.draw.circle(tela, (60, 30, 10), (x + 23, y + 23), 2)       # narina dir
    pygame.draw.circle(tela, BRANCO, (x + 13, y + 13), 7)             # olho esq
    pygame.draw.circle(tela, BRANCO, (x + 27, y + 13), 7)             # olho dir
    pygame.draw.circle(tela, (60, 30, 10), (x + 13, y + 13), 4)
    pygame.draw.circle(tela, (60, 30, 10), (x + 27, y + 13), 4)
    pygame.draw.circle(tela, PRETO, (x + 13, y + 13), 2)
    pygame.draw.circle(tela, PRETO, (x + 27, y + 13), 2)
    pygame.draw.circle(tela, BRANCO, (x + 15, y + 11), 1)             # brilho olho esq
    pygame.draw.circle(tela, BRANCO, (x + 29, y + 11), 1)             # brilho olho dir
    pygame.draw.arc(tela, cor_focinho, (x + 12, y + 4, 16, 8), 0, 3.14, 2)   # ruga
    pygame.draw.ellipse(tela, (220, 80, 100), (x + 15, y + 30, 10, 8))        # lingua
    pygame.draw.ellipse(tela, cor_focinho, (x + 5, y + 44, 12, 7))    # pata esq
    pygame.draw.ellipse(tela, cor_focinho, (x + 22, y + 44, 12, 7))   # pata dir
    pygame.draw.arc(tela, cor_corpo, (x + 34, y + 28, 12, 12), 0, 4, 4)  # rabo


# frame do jogador quando leva dano
def desenhar_jogador():
    if invencivel > 0 and (invencivel // 5) % 2 == 0:
        return
    desenhar_pug(jogador_x, jogador_y)


# desenho do portal de saida
def desenhar_portal():
    pygame.draw.rect(tela, (150, 50, 255), (portal_x, portal_y, portal_largura, portal_altura), border_radius=8)
    pygame.draw.rect(tela, (200, 100, 255), (portal_x, portal_y, portal_largura, portal_altura), 3, border_radius=8)
    texto = fonte_pequena.render("SAIDA", True, BRANCO)
    tela.blit(texto, (portal_x - 10, portal_y - 25))


# mostra pontos e vidas na tela
def desenhar_hud():
    texto_pontos = fonte_media.render(f"Pontos: {pontos}", True, BRANCO)
    tela.blit(texto_pontos, (10, 10))
    texto_vidas = fonte_media.render(f"Vidas: {vidas}", True, BRANCO)
    tela.blit(texto_vidas, (10, 40))


# verifica se o jogador ta em cima de uma plataforma
def checar_colisao_plataforma():
    global jogador_y, jogador_vel_y, jogador_no_chao

    jogador_no_chao = False
    jogador_rect = pygame.Rect(jogador_x, jogador_y, jogador_largura, jogador_altura)

    for p in plataformas:
        plat_rect = pygame.Rect(p[0], p[1], p[2], p[3])
        if jogador_rect.colliderect(plat_rect):
            if jogador_vel_y >= 0:  # caindo
                jogador_y = p[1] - jogador_altura
                jogador_vel_y = 0
                jogador_no_chao = True
            elif jogador_vel_y < 0:  # subindo
                jogador_y = p[1] + p[3]
                jogador_vel_y = 0


# verifica se o jogador pegou uma moeda
def checar_colisao_moedas():
    global pontos

    jogador_rect = pygame.Rect(jogador_x, jogador_y, jogador_largura, jogador_altura)
    for m in moedas:
        if not m[2]:
            moeda_rect = pygame.Rect(m[0] - 12, m[1] - 12, 24, 24)
            if jogador_rect.colliderect(moeda_rect):
                m[2] = True  # marca como coletada
                pontos += 5


# verifica se o jogador encostou num inimigo
def checar_colisao_inimigos():
    global vidas, jogador_x, jogador_y, jogador_vel_y, invencivel

    if invencivel > 0:
        return

    jogador_rect = pygame.Rect(jogador_x, jogador_y, jogador_largura, jogador_altura)

    for i in inimigos:
        inimigo_rect = pygame.Rect(i[0], i[1], 36, 36)
        if jogador_rect.colliderect(inimigo_rect):
            vidas -= 1
            invencivel = 60
            jogador_x = 100
            jogador_y = 300
            jogador_vel_y = 0
            return

    # dano da bolinha
    cuspidor_rect = pygame.Rect(inimigo_cuspidor[0], inimigo_cuspidor[1], 44, 44)
    if jogador_rect.colliderect(cuspidor_rect):
        vidas -= 1
        invencivel = 60
        jogador_x = 100
        jogador_y = 300
        jogador_vel_y = 0


# move as bolinhas e ve se acertaram o jogador
def atualizar_bolinhas():
    global vidas, jogador_x, jogador_y, jogador_vel_y, invencivel

    jogador_rect = pygame.Rect(jogador_x, jogador_y, jogador_largura, jogador_altura)

    for b in bolinhas[:]:
        b[0] += b[2]
        b[1] += b[3]
        b[3] += 0.15  # gravidade na bolinha

        # colisao com o jogador
        bolinha_rect = pygame.Rect(b[0] - 8, b[1] - 8, 16, 16)
        if bolinha_rect.colliderect(jogador_rect) and invencivel == 0:
            vidas -= 1
            invencivel = 60
            jogador_x = 100
            jogador_y = 300
            jogador_vel_y = 0
            bolinhas.remove(b)


# controla o disparo do monstro roxo
def atualizar_cuspidor():
    inimigo_cuspidor[2] += 1
    if inimigo_cuspidor[2] >= inimigo_cuspidor[3]:
        inimigo_cuspidor[2] = 0
        # atira bolinha em direcao ao jogador
        cx, cy = inimigo_cuspidor[0] + 22, inimigo_cuspidor[1] + 22
        dx, dy = jogador_x - cx, jogador_y - cy
        dist = max(1, (dx**2 + dy**2) ** 0.5)
        bolinhas.append([cx, cy, (dx / dist) * 5, (dy / dist) * 5])


# ve se o jogador chegou no portal
def checar_portal():
    jogador_rect = pygame.Rect(jogador_x, jogador_y, jogador_largura, jogador_altura)
    portal_rect = pygame.Rect(portal_x, portal_y, portal_largura, portal_altura)
    return jogador_rect.colliderect(portal_rect)


# move os monstros vermelhos
def mover_inimigos():
    for i in inimigos:
        i[0] += i[2] * i[3]
        if i[0] < 50 or i[0] > LARGURA - 80:
            i[2] *= -1  # inverte a direcao


# mostra a tela inicial
def tela_inicio():
    tela.fill((10, 5, 25))
    titulo = fonte_grande.render("JOGO DO PUG", True, AMARELO)
    tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 100))
    t1 = fonte_media.render("Setas para mover | ESPACO para pular", True, BRANCO)
    tela.blit(t1, (LARGURA // 2 - t1.get_width() // 2, 200))
    t2 = fonte_media.render("Cuidado com as bolinhas do monstro roxo!", True, VERMELHO)
    tela.blit(t2, (LARGURA // 2 - t2.get_width() // 2, 250))
    t3 = fonte_media.render("Colete moedas e chegue a SAIDA!", True, BRANCO)
    tela.blit(t3, (LARGURA // 2 - t3.get_width() // 2, 300))
    t4 = fonte_grande.render("Pressione ENTER para comecar", True, VERMELHO)
    tela.blit(t4, (LARGURA // 2 - t4.get_width() // 2, 380))
    pygame.display.flip()


# mostra o game over
def tela_morte():
    tela.fill((50, 0, 0))
    texto = fonte_grande.render("GAME OVER", True, VERMELHO)
    tela.blit(texto, (LARGURA // 2 - texto.get_width() // 2, 150))
    t1 = fonte_media.render(f"Sua pontuacao: {pontos}", True, BRANCO)
    tela.blit(t1, (LARGURA // 2 - t1.get_width() // 2, 260))
    t2 = fonte_media.render("R para reiniciar | Q para sair", True, BRANCO)
    tela.blit(t2, (LARGURA // 2 - t2.get_width() // 2, 320))
    pygame.display.flip()


# desenha a cena do pug chegando em casa
def desenhar_cena_vitoria():
    tela.fill((135, 200, 255))  # ceu azul

    # sol
    pygame.draw.circle(tela, (255, 230, 50), (120, 80), 45)

    # nuvens
    pygame.draw.ellipse(tela, BRANCO, (200, 40, 120, 50))
    pygame.draw.ellipse(tela, BRANCO, (240, 30, 100, 50))
    pygame.draw.ellipse(tela, BRANCO, (550, 60, 130, 45))
    pygame.draw.ellipse(tela, BRANCO, (590, 50, 100, 45))

    # grama
    pygame.draw.rect(tela, (60, 180, 60), (0, 380, 800, 120))

    # casa
    hx = 430
    pygame.draw.rect(tela, (220, 190, 150), (hx, 240, 200, 160))       # parede
    pygame.draw.rect(tela, (180, 150, 110), (hx, 240, 200, 160), 3)
    telhado = [(hx - 20, 240), (hx + 100, 150), (hx + 220, 240)]
    pygame.draw.polygon(tela, (160, 60, 40), telhado)                   # telhado

    pygame.draw.rect(tela, (110, 70, 30), (hx + 83, 290, 55, 110))     # porta
    pygame.draw.rect(tela, (80, 50, 20), (hx + 83, 290, 55, 110), 3)

    # pai do pug
    dx = hx + 88
    pygame.draw.rect(tela, (50, 80, 160), (dx + 2, 360, 18, 40))       # calca esq
    pygame.draw.rect(tela, (50, 80, 160), (dx + 22, 360, 18, 40))      # calca dir
    pygame.draw.rect(tela, (40, 25, 10), (dx, 355, 42, 7))             # cinto
    pygame.draw.rect(tela, (30, 30, 30), (dx, 300, 42, 60))            # camiseta preta
    pygame.draw.rect(tela, (30, 30, 30), (dx - 12, 300, 14, 35))       # manga esq
    pygame.draw.rect(tela, (30, 30, 30), (dx + 42, 300, 14, 35))       # manga dir
    pygame.draw.circle(tela, (210, 170, 120), (dx - 5, 336), 8)        # mao esq
    pygame.draw.circle(tela, (210, 170, 120), (dx + 47, 336), 8)       # mao dir
    pygame.draw.rect(tela, (210, 170, 120), (dx + 14, 285, 14, 18))    # pescoco
    pygame.draw.circle(tela, (210, 170, 120), (dx + 21, 268), 26)      # cabeca
    pygame.draw.circle(tela, BRANCO, (dx + 13, 264), 5)                # olho esq
    pygame.draw.circle(tela, BRANCO, (dx + 29, 264), 5)                # olho dir
    pygame.draw.circle(tela, (50, 30, 10), (dx + 13, 264), 3)
    pygame.draw.circle(tela, (50, 30, 10), (dx + 29, 264), 3)
    pygame.draw.line(tela, (60, 40, 20), (dx + 8, 257), (dx + 18, 258), 3)   # sobrancelha esq
    pygame.draw.line(tela, (60, 40, 20), (dx + 24, 258), (dx + 34, 257), 3)  # sobrancelha dir
    barba = [(dx + 2, 275), (dx - 4, 285), (dx, 300), (dx + 8, 308),
             (dx + 21, 312), (dx + 34, 308), (dx + 42, 300),
             (dx + 46, 285), (dx + 40, 275)]
    pygame.draw.polygon(tela, (60, 40, 20), barba)                     # barba grande
    pygame.draw.ellipse(tela, (70, 48, 25), (dx + 6, 274, 30, 10))     # bigode
    for bx in range(dx + 4, dx + 40, 6):
        pygame.draw.line(tela, (80, 55, 30), (bx, 280), (bx - 2, 310), 1)  # fios da barba

    # pug em casa
    desenhar_pug(hx + 35, 350)

    # coracoes
    pygame.draw.polygon(tela, (255, 80, 120),
        [(hx + 65, 330), (hx + 60, 320), (hx + 55, 325),
         (hx + 65, 340), (hx + 75, 325), (hx + 70, 320)])
    pygame.draw.polygon(tela, (255, 120, 150),
        [(hx + 70, 310), (hx + 66, 302), (hx + 62, 306),
         (hx + 70, 318), (hx + 78, 306), (hx + 74, 302)])


# mostra a tela de vitoria
def tela_vitoria():
    desenhar_cena_vitoria()
    titulo = fonte_grande.render("O PUG CHEGOU EM CASA!", True, (255, 200, 0))
    tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 50))
    t1 = fonte_media.render(f"Pontuacao final: {pontos}", True, PRETO)
    tela.blit(t1, (LARGURA // 2 - t1.get_width() // 2, 110))
    t2 = fonte_pequena.render("R para jogar de novo | Q para sair", True, PRETO)
    tela.blit(t2, (LARGURA // 2 - t2.get_width() // 2, 148))
    pygame.display.flip()


# volta tudo pro inicio quando aperta R
def resetar_jogo():
    global jogador_x, jogador_y, jogador_vel_y
    global vidas, pontos, estado, invencivel

    jogador_x = 100
    jogador_y = 300
    jogador_vel_y = 0
    vidas = 3
    pontos = 0
    invencivel = 0

    bolinhas.clear()

    for m in moedas:
        m[2] = False

    inimigos[0][0] = 320
    inimigos[1][0] = 650
    inimigo_cuspidor[2] = 0

    estado = "jogando"


# loop principal do jogo
while True:

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if evento.type == pygame.KEYDOWN:
            if estado == "inicio":
                if evento.key == pygame.K_RETURN:
                    estado = "jogando"

            elif estado == "jogando":
                if evento.key == pygame.K_SPACE or evento.key == pygame.K_UP:
                    if jogador_no_chao:
                        jogador_vel_y = forca_pulo  # pula

            elif estado == "morreu" or estado == "ganhou":
                if evento.key == pygame.K_r:
                    resetar_jogo()
                if evento.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

    if estado == "jogando":

        # pega as teclas pressionadas
        teclas = pygame.key.get_pressed()
        vel_x = 0
        if teclas[pygame.K_LEFT]:
            vel_x = -jogador_velocidade
        if teclas[pygame.K_RIGHT]:
            vel_x = jogador_velocidade

        # aplica gravidade e move o jogador
        jogador_vel_y += gravidade
        jogador_x += vel_x
        jogador_y += jogador_vel_y

        # nao deixa sair da tela pelos lados
        if jogador_x < 0:
            jogador_x = 0
        if jogador_x + jogador_largura > LARGURA:
            jogador_x = LARGURA - jogador_largura

        # verifica colisoes e atualiza inimigos
        checar_colisao_plataforma()
        checar_colisao_moedas()
        checar_colisao_inimigos()
        mover_inimigos()
        atualizar_cuspidor()
        atualizar_bolinhas()

        if invencivel > 0:
            invencivel -= 1

        # se caiu no buraco
        if jogador_y > ALTURA + 50:
            if invencivel == 0:
                vidas -= 1
                invencivel = 60
            jogador_x = 100
            jogador_y = 300
            jogador_vel_y = 0

        if vidas <= 0:
            estado = "morreu"

        if checar_portal():
            pontos += 20
            estado = "ganhou"

    # desenha a tela de acordo com o estado
    if estado == "inicio":
        tela_inicio()

    elif estado == "jogando":
        desenhar_fundo()
        desenhar_plataformas()
        desenhar_moedas()
        desenhar_inimigos()
        desenhar_cuspidor()
        desenhar_bolinhas()
        desenhar_portal()
        desenhar_jogador()
        desenhar_hud()
        pygame.display.flip()

    elif estado == "morreu":
        tela_morte()

    elif estado == "ganhou":
        tela_vitoria()

    clock.tick(FPS)