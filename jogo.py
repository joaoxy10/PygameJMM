import pygame
import math
import sys
import json
from jij import ordena

nomex = 455
numx = 988
posy = 438
increase = 110

with open('ranking.json', 'r') as arquivo_json:
    lista_ranking = json.load(arquivo_json)
print(lista_ranking)

pygame.init()
pygame.mixer.init()
#tela
WIDTH, HEIGHT = 1536, 1024
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Insper Racers")
clock = pygame.time.Clock()
FPS = 60

#cores
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

#fonte
fonte_pixel = pygame.font.Font("PressStart2P-Regular.ttf", 20)
fonte_pixel2 = pygame.font.Font("PressStart2P-Regular.ttf", 40)

#imagens
pista_img = pygame.image.load("pista4.0.png").convert()
pista_img = pygame.transform.scale(pista_img, (WIDTH, HEIGHT-60))

col_map = pygame.image.load('pista4 colisao.png').convert()
col_map = pygame.transform.scale(col_map, (WIDTH, HEIGHT - 60))

inicio_img = pygame.image.load("telainicial.png").convert()
inicio_img = pygame.transform.scale(inicio_img, (WIDTH, HEIGHT-60))

ranking_img = pygame.image.load("telaranking.png").convert()
ranking_img = pygame.transform.scale(ranking_img, (WIDTH, HEIGHT-60))

nome_img = pygame.image.load("telanome.png").convert()
nome_img = pygame.transform.scale(nome_img, (WIDTH, HEIGHT-60))

car_img = pygame.image.load("carro4.png").convert_alpha()
car_img = pygame.transform.scale(car_img, (47, 43))

car_img2 = pygame.image.load("carro5 .png").convert_alpha()
car_img2 = pygame.transform.scale(car_img2, (47, 43))
car_width, car_height = 47, 43

segredo_img = pygame.image.load('segredo_img.png').convert()
segredo_img = pygame.transform.scale(segredo_img, (WIDTH, HEIGHT - 60))

instrucao_img = pygame.image.load('instrucao_img.jpg').convert()
instrucao_img = pygame.transform.scale(instrucao_img, (WIDTH, HEIGHT - 60))

#volta_invalida_img = pygame.image.load("volta_invalida.png").convert_alpha()
#volta_invalida_img = pygame.transform.scale(volta_invalida_img, (400, 100))  # ajustar tamanho

nome_player = ""
ativo = False  
limite_caracteres = 8
input_rect = pygame.Rect(200, 200, 240, 50)

#sons
acelera = pygame.mixer.Sound('acelera.ogg')
freia = pygame.mixer.Sound('car brake.ogg')
segredo_sound = pygame.mixer.Sound('segredo som.ogg')

#som_volta_invalida = pygame.mixer.Sound('volta_invalida.ogg')


pygame.mixer.music.load('musicaBIT.ogg')
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

acelera.set_volume(0)
acelera.play(loops=-1)

#carros como dicionarios
carro1 = {
    "img": car_img,
    "pos": [500, 830], 
    "angle": 0,
    "speed": 0,
    "accel": 0.3,
    "max_speed": 7,
    "friction": 0.05,
    "turn_speed": 2.7,
    "last_pos1": [550, 830]
}


#estados do jogo
TELA_INICIAL = 0
TELA_JOGO = 1
estado = TELA_INICIAL
TELA_SEGREDO = 2
TELA_INSTRUCOES = 3
TELA_NOME = 4
TELA_RANKING = 5


# cronometro
tempo_inicial = 0
cronometro_ativo = False
tempo_pausado_total = 0

lap_times = []
lap_started = False
last_cross_time = 0
lap_start_time = 0
ultimo_tempo_volta = None
melhor_volta = None
diferenca_voltas = None
mostrar_volta_invalida = False
tempo_erro_mostrado = 3000
imprimido = False
salvo = False
appendado = False


#funcoes

def formatar_tempo(ms):
    minuto = ms // 60000
    seg = (ms % 60000) // 1000
    mil = ms % 1000
    formatado = f"{minuto:02}:{seg:02}.{mil:03}"
    return formatado

def audio(teclas, frente, tras):
    if teclas[frente]:
        acelera.play()
        freia.stop()
    else:
        acelera.stop()
        freia.play()

def desenhar_tela_inicial():
    screen.blit(inicio_img, (0, 45))

def tela_nome():
    screen.blit(nome_img, (0, 45))
    
def tela_instrucao():
    screen.blit(instrucao_img, (0, 45))

def draw_track():
    screen.blit(pista_img, (0, 0))
    
    #pygame.draw.rect(screen, (0, 255, 0), largada_rect, 2) 

def blit_rotate_center(surf, image, pos, angle):
    rotated_image = pygame.transform.rotate(image, -angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(center=pos).center)
    surf.blit(rotated_image, new_rect.topleft)

def aplicar_movimento(teclas, frente, tras, esquerda, direita, car):
    if teclas[frente]:
        car["speed"] += car["accel"]
    if teclas[tras]:
        car["speed"] -= car["accel"]
    if teclas[direita]:
        car["angle"] += car["turn_speed"]
    if teclas[esquerda]:
        car["angle"] -= car["turn_speed"]
    
    car["speed"] = max(-car["max_speed"], min(car["max_speed"], car["speed"]))
    
    #atrito
    if abs(car["speed"]) < car["friction"]:
        car["speed"] = 0
    else:
        car["speed"] -= math.copysign(car["friction"], car["speed"])

    #movimento
    radians = math.radians(car["angle"])
    car["last_pos"] = car["pos"][:]
    car["pos"][0] += math.cos(radians) * car["speed"]
    car["pos"][1] += math.sin(radians) * car["speed"]

def na_pista(pos, mapa_col, angle):
    x, y = pos
    radians = math.radians(angle)
    
    # pegar 5 pontos em volta do carrinho  
    offsets = [
        (0, 0),  # centro
        (math.cos(radians) * 20, math.sin(radians) * 20),  # frente
        (math.cos(radians) * -20, math.sin(radians) * -20),  # tras
        (math.cos(radians + math.pi/2) * 15, math.sin(radians + math.pi/2) * 15),  # esquerda
        (math.cos(radians - math.pi/2) * 15, math.sin(radians - math.pi/2) * 15),  # direita
    ]

    for dx, dy in offsets:
        cx, cy = int(x + dx), int(y + dy)
        if not (0 <= cx < mapa_col.get_width() and 0 <= cy < mapa_col.get_height()):
            return False
        cor = mapa_col.get_at((cx, cy))[:3] #usar so rgb
        if any(c < 250 for c in cor):  #se nao for proximo de branco eh fora da pista
            return False
    return True

def penalty(pos, mapa_col, angle):
    x, y = pos    
    cor = mapa_col.get_at((int(x), int(y)))[:3]
    
    if cor == (255, 0, 0):
        return True
    else:
        return False

def segredo():
    acelera.stop()
    freia.stop()
    pygame.mixer_music.stop()
    
    screen.blit(segredo_img, (0, 45))
    best_text = fonte_pixel.render('Sem Trapacear', True, RED)
    best_rect = best_text.get_rect(topleft=(670, 90))
    screen.blit(best_text, best_rect)
    
    pygame.display.flip()
    segredo_sound.play()
    tempo_start = pygame.time.get_ticks()
    tempo_current = pygame.time.get_ticks()
    while (tempo_current - tempo_start) < 4000:
        tempo_current = pygame.time.get_ticks()
    pygame.quit()

def tela_ranking():
    screen.blit(ranking_img, (0, 45))
    acelera.stop()
    freia.stop()
    pygame.mixer_music.stop()

def mostrar_voltas():
    
    if len(lista_ranking) >= 1:
        lap1_text = fonte_pixel.render(formatar_tempo(lista_ranking[0]["volta"]), True, BLACK)
        lap1_rect = lap1_text.get_rect(topleft=(numx, posy))
        screen.blit(lap1_text, lap1_rect)

        nome1_text = fonte_pixel.render(lista_ranking[0]["nome"], True, BLACK)
        nome1_rect = nome1_text.get_rect(topleft=(nomex, posy))
        screen.blit(nome1_text, nome1_rect)

    if len(lista_ranking) >= 2:  
        lap2_text = fonte_pixel.render(formatar_tempo(lista_ranking[1]["volta"]), True, BLACK)
        lap2_rect = lap2_text.get_rect(topleft=(numx, posy+(increase*1)))
        screen.blit(lap2_text, lap2_rect)

        nome2_text = fonte_pixel.render(lista_ranking[1]["nome"], True, BLACK)
        nome2_rect = nome2_text.get_rect(topleft=(nomex, posy+(increase*1)))
        screen.blit(nome2_text, nome2_rect)

    if len(lista_ranking) >= 3:    
        lap3_text = fonte_pixel.render(formatar_tempo(lista_ranking[2]["volta"]), True, BLACK)
        lap3_rect = lap3_text.get_rect(topleft=(numx, posy+(increase*2)))
        screen.blit(lap3_text, lap3_rect)

        nome3_text = fonte_pixel.render(lista_ranking[2]["nome"], True, BLACK)
        nome3_rect = nome3_text.get_rect(topleft=(nomex, posy+(increase*2)))
        screen.blit(nome3_text, nome3_rect)

    if len(lista_ranking) >= 4:    
        lap4_text = fonte_pixel.render(formatar_tempo(lista_ranking[3]["volta"]), True, BLACK)
        lap4_rect = lap4_text.get_rect(topleft=(numx, posy+(increase*3)))
        screen.blit(lap4_text, lap4_rect)

        nome4_text = fonte_pixel.render(lista_ranking[3]["nome"], True, BLACK)
        nome4_rect = nome4_text.get_rect(topleft=(nomex, posy+(increase*3)))
        screen.blit(nome4_text, nome4_rect)

    if len(lista_ranking) >= 5:   
        lap5_text = fonte_pixel.render(formatar_tempo(lista_ranking[4]["volta"]), True, BLACK)
        lap5_rect = lap5_text.get_rect(topleft=(numx, posy+(increase*4)))
        screen.blit(lap5_text, lap5_rect)

        nome5_text = fonte_pixel.render(lista_ranking[4]["nome"], True, BLACK)
        nome5_rect = nome5_text.get_rect(topleft=(nomex, posy+(increase*4)))
        screen.blit(nome1_text, nome5_rect)

def organizar_por_tempo(lista):
    lista_org = sorted(lista_ranking, key=lambda x: x['volta']) #que funcao maravilhosa como eu nunca vi isso antes
    return lista_org
    


#linha de largada/chegada  
largada_rect = pygame.Rect(575, 750, 30, 100)  


# Loop principal
running = True
while running:
    clock.tick(FPS)
    screen.fill(WHITE)
    if estado == TELA_SEGREDO:
        segredo()

    
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
        elif event.type == pygame.KEYDOWN and estado == TELA_INICIAL and event.key == pygame.K_RETURN:
            estado = TELA_NOME
        elif event.type == pygame.KEYDOWN and estado == TELA_NOME:
            if event.key == pygame.K_RETURN:
                estado = TELA_INSTRUCOES
                print("Nome digitado:", nome_player)
            elif event.key == pygame.K_BACKSPACE:
                nome_player = nome_player[:-1]
            else:
                if len(nome_player) < limite_caracteres and event.unicode.isalnum():
                    nome_player += event.unicode
        elif event.type == pygame.KEYDOWN and estado == TELA_INSTRUCOES and event.key == pygame.K_RETURN:
            estado = TELA_JOGO
            tempo_inicial = pygame.time.get_ticks()
            cronometro_ativo = True
        elif event.type == pygame.KEYDOWN and estado == TELA_JOGO and event.key == pygame.K_BACKSPACE:
            estado = TELA_RANKING


    if estado == TELA_INICIAL:
        desenhar_tela_inicial()

    elif estado == TELA_JOGO:
        pygame.mixer.music.set_volume(0.3)
        draw_track()
        
        keys = pygame.key.get_pressed()

        if keys[pygame.K_BACKSPACE]:
            estado = TELA_RANKING


        aplicar_movimento(keys, pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, carro1)
        

        blit_rotate_center(screen, carro1["img"], carro1["pos"], carro1["angle"])
        

        #pygame.draw.circle(screen, (255, 0, 0), (int(carro1["pos"][0]), int(carro1["pos"][1])), 3)      ponto de debug no meio do carro
        
        now = pygame.time.get_ticks()

        if (largada_rect.collidepoint(carro1["pos"])):
            
            if now - last_cross_time > 2000:  # debounce a cada 2 segundos
                last_cross_time = now

                if lap_started == True:  #tudo sobre a contagem de voltas
                    lap_time = now - lap_start_time
                    
                    #segredo hihi
                    if lap_time <= 9000:
                        estado = TELA_SEGREDO
                        
                    if estado != TELA_SEGREDO:
                        lap_times.append(lap_time)
                        
                        #formatar twmpo da ultima volta
                        ultimo_tempo_volta = formatar_tempo(lap_time)

                        #setar a melhot volta
                        if melhor_volta == None or lap_time < melhor_volta:
                            melhor_volta = lap_time

                        #calcular diferenca
                        if len(lap_times) >= 2:
                            diferenca = lap_times[-1] - lap_times[-2]
                            
                            if diferenca > 0:
                                sinal = '+'
                                diff_cor = RED
                            else:
                                sinal = '-'
                                diff_cor = GREEN
                            
                            diferenca = abs(diferenca)
                            diferenca_voltas = formatar_tempo(diferenca)
                    
                    
                else:
                    lap_started = True  #primeira vez cruzando a linha

                lap_start_time = now


        #cronometro
        tempo_atual = pygame.time.get_ticks() if cronometro_ativo else tempo_inicial
        tempo_decorrido_ms = tempo_atual - tempo_inicial - tempo_pausado_total

        tempo_formatado = formatar_tempo(tempo_decorrido_ms)

        texto = fonte_pixel.render(tempo_formatado, True, WHITE)
        texto_rect = texto.get_rect(center=(WIDTH // 2+500, 100))
        screen.blit(texto, texto_rect)
        
        #mostrar ultima volta
        if ultimo_tempo_volta:
            lap_text = fonte_pixel.render(f"Última: {ultimo_tempo_volta}", True, WHITE)
            lap_rect = lap_text.get_rect(topleft=(50, 50))
            screen.blit(lap_text, lap_rect)

        # mostrar melhor volta
        if melhor_volta is not None:
            melhor_formatado = formatar_tempo(melhor_volta)
            best_text = fonte_pixel.render(f"Melhor: {melhor_formatado}", True, WHITE)
            best_rect = best_text.get_rect(topleft=(50, 90))
            screen.blit(best_text, best_rect)

        # mstrar diferenca de tempo
        if diferenca_voltas:
            diff_text = fonte_pixel.render(f"Δ: {diferenca_voltas}", True, diff_cor)
            diff_rect = diff_text.get_rect(topleft=(50, 130))
            screen.blit(diff_text, diff_rect)
        

        if not na_pista(carro1['pos'], col_map, carro1['angle']):
            carro1['speed'] = carro1['speed'] * 0.8

        if penalty(carro1["pos"], col_map, carro1["angle"]) == True:
            carro1['pos'] = [700, 830]
            carro1['angle'] = 0
    
    elif estado == TELA_NOME:
        tela_nome()
        texto_surface = fonte_pixel2.render(nome_player, True, WHITE)
        texto_rect = texto_surface.get_rect(center=(480, 475))
        screen.blit(texto_surface, texto_rect)
        pygame.display.flip()
    
    elif estado == TELA_RANKING:
        
        
        if melhor_volta is not None and appendado == False:
            
            lista_ranking.append({"nome":nome_player, "volta":melhor_volta})
            lista_ranking = organizar_por_tempo(lista_ranking)
            
            appendado = True
        
        
        tela_ranking()
        
        mostrar_voltas()


        if imprimido == False:
            print(lista_ranking)
            imprimido = True
        
        if salvo == False:
            with open('ranking.json', 'w') as file:
                json.dump(lista_ranking, file)
            salvo = True
    elif estado == TELA_INSTRUCOES:
        
        
        tela_instrucao()


    pygame.display.flip()









pygame.quit()

