import json
# ===== Inicialização =====
# ----- Importa e inicia pacotes
import pygame

pygame.init()
with open("ranking.json","r") as arquivo:
    texto=arquivo.read()
# ----- Gera tela principal
WIDTH = 500
HEIGHT = 400
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Hello World!')
font = pygame.font.SysFont(None,34)
font2 = pygame.font.SysFont(None,54)
text = font.render(texto, True, (250, 250, 250))
text2 = font2.render("recorde", True, (250, 250, 250))

# ----- Inicia estruturas de dados
game = True

# ----- Inicia assets
image = pygame.image.load(r'C:\Users\joaox\Downloads\referencia\referencia\assets\img\logo-madfox.png').convert()

# ===== Loop principal =====
while game:
    # ----- Trata eventos
    for event in pygame.event.get():
        # ----- Verifica consequências
        if event.type == pygame.QUIT:
            game = False

    # ----- Gera saídas
    window.fill((0, 0, 0))  # Preenche com a cor branca
    window.blit(image, (10, 10))
    window.blit(text, (150, 150))
    window.blit(text2, (220, 100))



    # ----- Atualiza estado do jogo
    pygame.display.update()  # Mostra o novo frame para o jogador

# ===== Finalização =====
pygame.quit()  # Função do PyGame que finaliza os recursos utilizados

