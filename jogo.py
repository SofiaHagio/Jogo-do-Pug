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

# dicionario do jogador
jogador = {
    "x": 100, "y": 300,
    "largura": 40, "altura": 50,
    "vel_y": 0, "no_chao": False,
    "velocidade": 5, "vidas": 3,
}

gravidade = 0.5
forca_pulo = -12
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
    {"x": 160, "y": 330, "coletada": False},
    {"x": 370, "y": 260, "coletada": False},
    {"x": 560, "y": 190, "coletada": False},
    {"x": 700, "y": 300, "coletada": False},
    {"x": 250, "y": 150, "coletada": False},
    {"x": 440, "y": 110, "coletada": False},
]

# monstros que andam: x, y, direcao, velocidade
inimigos = [
    {"x": 320, "y": 262, "dir": 1, "vel": 2},
    {"x": 650, "y": 302, "dir": 1, "vel": 1},
]

# monstro que cospe: x, y, timer, intervalo
cuspidor = {"x": 500, "y": 185, "timer": 0, "intervalo": 90}

# bolinhas no ar: x, y, vel_x, vel_y
bolinhas = []

# portal de saida
portal = {"x": 730, "y": 130, "largura": 40, "altura": 60}

# estado do jogo
estado = "inicio"


# desenho do cenario
def desenhar_fundo():
    tela.fill((10, 5, 25))

    # lua sangrenta
    pygame.draw.circle(tela, (160, 0, 0), (680, 60), 40)
    pygame.draw.circle(tela, (220, 30, 30), (680, 60), 40, 3)
    pygame.draw.circle(tela, (10, 5, 25), (696, 50), 30)  # recorte crescente
    pygame.draw.ellipse(tela, (180, 0, 0), (658, 88, 7, 14))
    pygame.draw.ellipse(tela, (180, 0, 0), (672, 92, 5, 10))
    pygame.draw.ellipse(tela, (180, 0, 0), (648, 85, 6, 18))
    pygame.draw.circle(tela, (180, 0, 0), (661, 103), 4)
    pygame.draw.circle(tela, (180, 0, 0), (651, 104), 3)

    # estrelas
    for ex, ey in [(50,30),(120,15),(200,45),(300,20),(370,55),(450,10),(530,40),(600,25),(760,15),(80,80),(160,65),(250,90),(420,75),(700,110)]:
        pygame.draw.circle(tela, (200, 200, 220), (ex, ey), 2)

    # montanhas
    pygame.draw.polygon(tela, (20, 10, 40), [(0,500),(0,320),(80,200),(160,320),(240,230),(320,320),(400,180),(480,320),(560,250),(640,320),(720,210),(800,320),(800,500)])
    pygame.draw.polygon(tela, (15, 8, 30),  [(0,500),(0,380),(60,300),(140,380),(220,310),(300,390),(380,330),(460,390),(540,320),(620,400),(700,340),(800,400),(800,500)])


# desenho das plataformas e moedas
def desenhar_plataformas_e_moedas():
    for p in plataformas:
        pygame.draw.rect(tela, VERDE, (p[0], p[1], p[2], p[3]))
        pygame.draw.rect(tela, PRETO, (p[0], p[1], p[2], p[3]), 2)
    for m in moedas:
        if not m["coletada"]:
            pygame.draw.circle(tela, AMARELO, (m["x"], m["y"]), 12)
            pygame.draw.circle(tela, LARANJA,  (m["x"], m["y"]), 12, 3)


# desenho dos espinhos dos monstros
def espinhos(cx, cy, raio, qtd, tamanho, cor):
    for i in range(qtd):
        ang = (360 / qtd) * i
        rad = math.radians(ang)
        b1 = (cx + math.cos(math.radians(ang - 8)) * raio, cy + math.sin(math.radians(ang - 8)) * raio)
        b2 = (cx + math.cos(math.radians(ang + 8)) * raio, cy + math.sin(math.radians(ang + 8)) * raio)
        p  = (cx + math.cos(rad) * (raio + tamanho),       cy + math.sin(rad) * (raio + tamanho))
        pygame.draw.polygon(tela, cor, [b1, b2, p])


# desenho dos monstros que andam e do monstro que cospe
def desenhar_inimigos():
    for i in inimigos:
        cx, cy = i["x"] + 18, i["y"] + 18
        espinhos(cx, cy, 16, 8, 10, (180, 0, 0))
        pygame.draw.circle(tela, (140, 0, 20), (cx, cy), 16)          # corpo
        pygame.draw.circle(tela, VERMELHO, (cx, cy), 16, 2)           # borda
        pygame.draw.circle(tela, (255, 50, 50), (cx - 6, cy - 4), 5)  # olho esq
        pygame.draw.circle(tela, (255, 50, 50), (cx + 6, cy - 4), 5)  # olho dir
        pygame.draw.circle(tela, PRETO, (cx - 6, cy - 4), 2)
        pygame.draw.circle(tela, PRETO, (cx + 6, cy - 4), 2)
        pygame.draw.line(tela, PRETO, (cx - 10, cy - 10), (cx - 3, cy - 7), 2)  # sobrancelha esq
        pygame.draw.line(tela, PRETO, (cx + 10, cy - 10), (cx + 3, cy - 7), 2)  # sobrancelha dir
        pygame.draw.arc(tela, PRETO, (cx - 7, cy + 2, 14, 8), math.pi, 2 * math.pi, 2)  # boca
        pygame.draw.line(tela, BRANCO, (cx - 4, cy + 6), (cx - 4, cy + 10), 2)  # dente esq
        pygame.draw.line(tela, BRANCO, (cx,     cy + 6), (cx,     cy + 10), 2)  # dente meio
        pygame.draw.line(tela, BRANCO, (cx + 4, cy + 6), (cx + 4, cy + 10), 2)  # dente dir

    cx, cy = cuspidor["x"] + 22, cuspidor["y"] + 22
    espinhos(cx, cy, 20, 10, 14, (120, 0, 160))
    pygame.draw.circle(tela, (60, 0, 90),   (cx, cy), 20)             # corpo
    pygame.draw.circle(tela, (200, 0, 220), (cx, cy), 20, 3)          # borda
    pygame.draw.circle(tela, AMARELO, (cx - 8, cy - 5), 7)            # olho esq
    pygame.draw.circle(tela, AMARELO, (cx + 8, cy - 5), 7)            # olho dir
    pygame.draw.circle(tela, PRETO,   (cx - 8, cy - 5), 3)
    pygame.draw.circle(tela, PRETO,   (cx + 8, cy - 5), 3)
    pygame.draw.circle(tela, BRANCO,  (cx - 6, cy - 7), 2)            # brilho esq
    pygame.draw.circle(tela, BRANCO,  (cx + 10, cy - 7), 2)           # brilho dir
    pygame.draw.line(tela, PRETO, (cx - 14, cy - 13), (cx - 4, cy - 9), 3)  # sobrancelha esq
    pygame.draw.line(tela, PRETO, (cx + 14, cy - 13), (cx + 4, cy - 9), 3)  # sobrancelha dir
    pygame.draw.ellipse(tela, PRETO, (cx - 10, cy + 6, 20, 12))       # boca
    pygame.draw.line(tela, BRANCO, (cx - 6, cy + 6), (cx - 6, cy + 14), 2)  # dente esq
    pygame.draw.line(tela, BRANCO, (cx,     cy + 6), (cx,     cy + 14), 2)  # dente meio
    pygame.draw.line(tela, BRANCO, (cx + 6, cy + 6), (cx + 6, cy + 14), 2)  # dente dir

    # bolinhas no ar
    for b in bolinhas:
        pygame.draw.circle(tela, (180, 0, 220),  (int(b[0]), int(b[1])), 8)
        pygame.draw.circle(tela, (220, 100, 255), (int(b[0]) - 2, int(b[1]) - 2), 3)


# desenho do pug
def desenhar_pug(x, y):
    cc = (180, 140, 100)  # cor corpo
    cf = (130, 90, 60)    # cor focinho
    co = (110, 70, 40)    # cor orelha

    pygame.draw.ellipse(tela, cc, (x+4,  y+20, 34, 26))   # corpo
    pygame.draw.circle(tela, cc, (x+20, y+18), 18)         # cabeca
    pygame.draw.ellipse(tela, co, (x,    y+2,  14, 18))    # orelha esq
    pygame.draw.ellipse(tela, co, (x+28, y+2,  14, 18))    # orelha dir
    pygame.draw.ellipse(tela, cf, (x+11, y+20, 18, 12))    # focinho
    pygame.draw.ellipse(tela, PRETO, (x+14, y+20, 12, 7))  # nariz
    pygame.draw.circle(tela, (60,30,10), (x+16, y+23), 2)  # narina esq
    pygame.draw.circle(tela, (60,30,10), (x+23, y+23), 2)  # narina dir
    pygame.draw.circle(tela, BRANCO, (x+13, y+13), 7)      # olho esq
    pygame.draw.circle(tela, BRANCO, (x+27, y+13), 7)      # olho dir
    pygame.draw.circle(tela, (60,30,10), (x+13, y+13), 4)
    pygame.draw.circle(tela, (60,30,10), (x+27, y+13), 4)
    pygame.draw.circle(tela, PRETO, (x+13, y+13), 2)
    pygame.draw.circle(tela, PRETO, (x+27, y+13), 2)
    pygame.draw.circle(tela, BRANCO, (x+15, y+11), 1)      # brilho esq
    pygame.draw.circle(tela, BRANCO, (x+29, y+11), 1)      # brilho dir
    pygame.draw.ellipse(tela, (220,80,100), (x+15, y+30, 10, 8))     # lingua
    pygame.draw.ellipse(tela, cf, (x+5,  y+44, 12, 7))     # pata esq
    pygame.draw.ellipse(tela, cf, (x+22, y+44, 12, 7))     # pata dir
    pygame.draw.arc(tela, cc, (x+34, y+28, 12, 12), 0, 4, 4)        # rabo


# frame do jogador quando leva dano
def desenhar_jogador():
    if invencivel > 0 and (invencivel // 5) % 2 == 0:
        return
    desenhar_pug(jogador["x"], jogador["y"])


# mostra pontos, vidas e portal na tela
def desenhar_hud_e_portal():
    tela.blit(fonte_media.render(f"Pontos: {pontos}", True, BRANCO), (10, 10))
    tela.blit(fonte_media.render(f"Vidas: {jogador['vidas']}", True, BRANCO), (10, 40))
    pygame.draw.rect(tela, (150, 50, 255), (portal["x"], portal["y"], portal["largura"], portal["altura"]), border_radius=8)
    pygame.draw.rect(tela, (200, 100, 255), (portal["x"], portal["y"], portal["largura"], portal["altura"]), 3, border_radius=8)
    tela.blit(fonte_pequena.render("SAIDA", True, BRANCO), (portal["x"] - 10, portal["y"] - 25))


# verifica se o jogador ta em cima de uma plataforma
def checar_colisao_plataforma():
    jogador["no_chao"] = False
    jrect = pygame.Rect(jogador["x"], jogador["y"], jogador["largura"], jogador["altura"])
    for p in plataformas:
        prect = pygame.Rect(p[0], p[1], p[2], p[3])
        if jrect.colliderect(prect):
            if jogador["vel_y"] >= 0:  # caindo
                jogador["y"] = p[1] - jogador["altura"]
                jogador["vel_y"] = 0
                jogador["no_chao"] = True
            else:  # subindo
                jogador["y"] = p[1] + p[3]
                jogador["vel_y"] = 0


# verifica se o jogador pegou uma moeda
def checar_colisao_moedas():
    global pontos
    jrect = pygame.Rect(jogador["x"], jogador["y"], jogador["largura"], jogador["altura"])
    for m in moedas:
        if not m["coletada"]:
            if jrect.colliderect(pygame.Rect(m["x"] - 12, m["y"] - 12, 24, 24)):
                m["coletada"] = True
                pontos += 5


# verifica se o jogador encostou num inimigo ou bolinha
def checar_dano():
    global invencivel
    if invencivel > 0:
        return
    jrect = pygame.Rect(jogador["x"], jogador["y"], jogador["largura"], jogador["altura"])

    for i in inimigos:
        if jrect.colliderect(pygame.Rect(i["x"], i["y"], 36, 36)):
            tomar_dano()
            return

    if jrect.colliderect(pygame.Rect(cuspidor["x"], cuspidor["y"], 44, 44)):
        tomar_dano()
        return

    for b in bolinhas[:]:
        if jrect.colliderect(pygame.Rect(b[0]-8, b[1]-8, 16, 16)):
            tomar_dano()
            bolinhas.remove(b)
            return


# tira uma vida e manda o jogador pro inicio
def tomar_dano():
    global invencivel
    jogador["vidas"] -= 1
    jogador["x"] = 100
    jogador["y"] = 300
    jogador["vel_y"] = 0
    invencivel = 60


# move as bolinhas e o monstro roxo
def atualizar_inimigos():
    for i in inimigos:
        i["x"] += i["dir"] * i["vel"]
        if i["x"] < 50 or i["x"] > LARGURA - 80:
            i["dir"] *= -1  # inverte a direcao

    cuspidor["timer"] += 1
    if cuspidor["timer"] >= cuspidor["intervalo"]:
        cuspidor["timer"] = 0
        cx, cy = cuspidor["x"] + 22, cuspidor["y"] + 22
        dx, dy = jogador["x"] - cx, jogador["y"] - cy
        dist = max(1, (dx**2 + dy**2) ** 0.5)
        bolinhas.append([cx, cy, (dx / dist) * 5, (dy / dist) * 5])

    for b in bolinhas[:]:
        b[0] += b[2]
        b[1] += b[3]
        b[3] += 0.15  # gravidade na bolinha
        if b[0] < -20 or b[0] > LARGURA + 20 or b[1] > ALTURA + 20:
            bolinhas.remove(b)


# mostra a tela inicial
def tela_inicio():
    tela.fill((10, 5, 25))
    tela.blit(fonte_grande.render("JOGO DO PUG", True, AMARELO), (LARGURA//2 - 175, 100))
    tela.blit(fonte_media.render("Setas para mover | ESPACO para pular", True, BRANCO), (LARGURA//2 - 270, 200))
    tela.blit(fonte_media.render("Cuidado com as bolinhas do monstro roxo!", True, VERMELHO), (LARGURA//2 - 300, 250))
    tela.blit(fonte_media.render("Colete moedas e chegue a SAIDA!", True, BRANCO), (LARGURA//2 - 230, 300))
    tela.blit(fonte_grande.render("Pressione ENTER para comecar", True, VERMELHO), (LARGURA//2 - 330, 380))
    pygame.display.flip()


# mostra o game over
def tela_morte():
    tela.fill((50, 0, 0))
    tela.blit(fonte_grande.render("GAME OVER", True, VERMELHO), (LARGURA//2 - 160, 150))
    tela.blit(fonte_media.render(f"Sua pontuacao: {pontos}", True, BRANCO), (LARGURA//2 - 160, 260))
    tela.blit(fonte_media.render("R para reiniciar | Q para sair", True, BRANCO), (LARGURA//2 - 220, 320))
    pygame.display.flip()


# desenha a cena do pug chegando em casa
def desenhar_cena_vitoria():
    tela.fill((135, 200, 255))  # ceu azul
    pygame.draw.circle(tela, (255, 230, 50), (120, 80), 45)  # sol
    for ex, ey, lx, ly in [(200,40,120,50),(240,30,100,50),(550,60,130,45),(590,50,100,45)]:
        pygame.draw.ellipse(tela, BRANCO, (ex, ey, lx, ly))  # nuvens
    pygame.draw.rect(tela, (60, 180, 60), (0, 380, 800, 120))  # grama

    hx = 430
    pygame.draw.rect(tela, (220, 190, 150), (hx, 240, 200, 160))      # parede
    pygame.draw.rect(tela, (180, 150, 110), (hx, 240, 200, 160), 3)
    pygame.draw.polygon(tela, (160, 60, 40), [(hx-20,240),(hx+100,150),(hx+220,240)])  # telhado
    pygame.draw.rect(tela, (110, 70, 30), (hx+83, 290, 55, 110))      # porta
    pygame.draw.rect(tela, (80, 50, 20),  (hx+83, 290, 55, 110), 3)

    dx = hx + 88
    pygame.draw.rect(tela, (50, 80, 160),   (dx+2,  360, 18, 40))     # calca esq
    pygame.draw.rect(tela, (50, 80, 160),   (dx+22, 360, 18, 40))     # calca dir
    pygame.draw.rect(tela, (40, 25, 10),    (dx,    355, 42,  7))     # cinto
    pygame.draw.rect(tela, (30, 30, 30),    (dx,    300, 42, 60))     # camiseta
    pygame.draw.rect(tela, (30, 30, 30),    (dx-12, 300, 14, 35))     # manga esq
    pygame.draw.rect(tela, (30, 30, 30),    (dx+42, 300, 14, 35))     # manga dir
    pygame.draw.circle(tela, (210,170,120), (dx-5,  336), 8)          # mao esq
    pygame.draw.circle(tela, (210,170,120), (dx+47, 336), 8)          # mao dir
    pygame.draw.rect(tela, (210,170,120),   (dx+14, 285, 14, 18))     # pescoco
    pygame.draw.circle(tela, (210,170,120), (dx+21, 268), 26)         # cabeca
    pygame.draw.circle(tela, BRANCO,        (dx+13, 264), 5)          # olho esq
    pygame.draw.circle(tela, BRANCO,        (dx+29, 264), 5)          # olho dir
    pygame.draw.circle(tela, (50,30,10),    (dx+13, 264), 3)
    pygame.draw.circle(tela, (50,30,10),    (dx+29, 264), 3)
    pygame.draw.line(tela, (60,40,20), (dx+8, 257),  (dx+18, 258), 3)  # sobrancelha esq
    pygame.draw.line(tela, (60,40,20), (dx+24, 258), (dx+34, 257), 3)  # sobrancelha dir
    pygame.draw.polygon(tela, (60,40,20), [(dx+2,275),(dx-4,285),(dx,300),(dx+8,308),(dx+21,312),(dx+34,308),(dx+42,300),(dx+46,285),(dx+40,275)])  # barba
    pygame.draw.ellipse(tela, (70,48,25), (dx+6, 274, 30, 10))         # bigode
    for bx in range(dx+4, dx+40, 6):
        pygame.draw.line(tela, (80,55,30), (bx, 280), (bx-2, 310), 1) # fios da barba

    desenhar_pug(hx + 35, 350)  # pug em casa
    pygame.draw.polygon(tela, (255,80,120),  [(hx+65,330),(hx+60,320),(hx+55,325),(hx+65,340),(hx+75,325),(hx+70,320)])  # coracao
    pygame.draw.polygon(tela, (255,120,150), [(hx+70,310),(hx+66,302),(hx+62,306),(hx+70,318),(hx+78,306),(hx+74,302)])  # coracao


# mostra a tela de vitoria
def tela_vitoria():
    desenhar_cena_vitoria()
    tela.blit(fonte_grande.render("O PUG CHEGOU EM CASA!", True, (255,200,0)), (LARGURA//2 - 280, 50))
    tela.blit(fonte_media.render(f"Pontuacao final: {pontos}", True, PRETO), (LARGURA//2 - 155, 110))
    tela.blit(fonte_pequena.render("R para jogar de novo | Q para sair", True, PRETO), (LARGURA//2 - 195, 148))
    pygame.display.flip()


# volta tudo pro inicio quando aperta R
def resetar_jogo():
    global pontos, estado, invencivel
    jogador["x"] = 100
    jogador["y"] = 300
    jogador["vel_y"] = 0
    jogador["vidas"] = 3
    pontos = 0
    invencivel = 0
    bolinhas.clear()
    for m in moedas:
        m["coletada"] = False
    inimigos[0]["x"] = 320
    inimigos[1]["x"] = 650
    cuspidor["timer"] = 0
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
                if evento.key in (pygame.K_SPACE, pygame.K_UP):
                    if jogador["no_chao"]:
                        jogador["vel_y"] = forca_pulo  # pula
            elif estado in ("morreu", "ganhou"):
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
            vel_x = -jogador["velocidade"]
        if teclas[pygame.K_RIGHT]:
            vel_x = jogador["velocidade"]

        # aplica gravidade e move o jogador
        jogador["vel_y"] += gravidade
        jogador["x"] += vel_x
        jogador["y"] += jogador["vel_y"]

        # nao deixa sair da tela pelos lados
        if jogador["x"] < 0:
            jogador["x"] = 0
        if jogador["x"] + jogador["largura"] > LARGURA:
            jogador["x"] = LARGURA - jogador["largura"]

        # verifica colisoes e atualiza inimigos
        checar_colisao_plataforma()
        checar_colisao_moedas()
        checar_dano()
        atualizar_inimigos()

        if invencivel > 0:
            invencivel -= 1

        # se caiu no buraco
        if jogador["y"] > ALTURA + 50:
            if invencivel == 0:
                tomar_dano()

        if jogador["vidas"] <= 0:
            estado = "morreu"

        if pygame.Rect(jogador["x"], jogador["y"], jogador["largura"], jogador["altura"]).colliderect(
           pygame.Rect(portal["x"], portal["y"], portal["largura"], portal["altura"])):
            pontos += 20
            estado = "ganhou"

    # desenha a tela de acordo com o estado
    if estado == "inicio":
        tela_inicio()
    elif estado == "jogando":
        desenhar_fundo()
        desenhar_plataformas_e_moedas()
        desenhar_inimigos()
        desenhar_hud_e_portal()
        desenhar_jogador()
        pygame.display.flip()
    elif estado == "morreu":
        tela_morte()
    elif estado == "ganhou":
        tela_vitoria()

    clock.tick(FPS)