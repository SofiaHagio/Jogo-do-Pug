"""Constantes do jogo: tela, física, cores e pontuação."""

TITULO = "Pug e a Lua Vermelha"

# Tela
LARGURA, ALTURA = 960, 540
FPS = 60
TILE = 36

# Física do pug (valores por quadro, a 60 FPS)
GRAVIDADE = 0.55
QUEDA_MAXIMA = 12
VELOCIDADE = 4.2
ACELERACAO = 0.6
ATRITO = 0.75
FORCA_PULO = 12
CORTE_PULO = 0.45  # soltar o botão no meio do pulo corta a subida
COYOTE = 6  # quadros em que ainda dá para pular depois de sair da beirada
BUFFER_PULO = 6  # quadros em que um pulo apertado cedo demais é guardado
QUIQUE = 8.5  # impulso ao pular em cima de um inimigo
INVENCIVEL = 90  # quadros piscando depois de levar dano

VIDAS = 3

# Pontos
PONTOS_OSSO = 10
PONTOS_OSSO_DOURADO = 100
PONTOS_INIMIGO = 50
BONUS_TEMPO_MAX = 300  # bônus que cai 2 pontos por segundo de fase

# Paleta
CEU_TOPO = (12, 6, 28)
CEU_HORIZONTE = (70, 14, 40)
LUA = (196, 32, 40)
LUA_BRILHO = (255, 96, 88)
MONTANHAS = [(28, 12, 46), (40, 14, 52), (22, 8, 34)]
TERRA = (46, 30, 58)
TERRA_ESCURA = (32, 20, 42)
GRAMA = (92, 58, 132)
GRAMA_CLARA = (138, 96, 186)
BRANCO = (245, 240, 250)
TEXTO = (232, 224, 240)
TEXTO_FRACO = (150, 136, 170)
OURO = (255, 206, 84)
OSSO = (240, 232, 214)
ROXO = (168, 72, 232)
VERMELHO = (226, 64, 72)
PRETO = (8, 4, 14)
