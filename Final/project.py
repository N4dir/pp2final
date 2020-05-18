import pygame
import pika
import sys

# ИМПОРТИМ СЮДА ИГРУ С КОДА ТАНКОВ
from single_tank import igra
from online import game_online
from online_ai import game_online_ai

# НАЗНАЧАЕМ ТЕ ЖЕ ЗНАЧЕНИЯ ЧТО И БЫЛИ ТАМ
pygame.init()
width = 1100
height = 600
pygame.display.set_caption("Tanks")
screen = pygame.display.set_mode((width,height))

# МЕНЮ ГЛАВНОГО ЭКРАНА
def main_screen():
    font = pygame.font.Font('freesansbold.ttf', 30)     
    text = font.render("WELCOME TO TANKS GAME", 1, (22,110,199)) 
    place = text.get_rect(center = (550,120))   
    screen.blit(text, place)

    font2 = pygame.font.Font('freesansbold.ttf', 15)     
    text2 = font2.render("Press [SPACE] to start a single player", 1, (22,110,199)) 
    place2 = text2.get_rect(center = (550,200))   
    screen.blit(text2, place2)

    font3 = pygame.font.Font('freesansbold.ttf', 15)     
    text3 = font3.render("Press [M] to start a multiplayer", 1, (22,110,199)) 
    place3 = text3.get_rect(center = (550,230))   
    screen.blit(text3, place3)

    font4 = pygame.font.Font('freesansbold.ttf', 15)
    text4 = font4.render("Press [I] to start a multiplayer via AI", 1, (22,110,199))
    place4 = text4.get_rect(center = (550,260))
    screen.blit(text4,place4)

running = True
# ЗАПУСКАЕТСЯ ГЛАВНАЯ ПРОГРАММА
while running:
    screen.fill((255,255,255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            # ЕСЛИ МЫ НАЖИМАЕМ НА ESC, ТО ПРОГРАММА ЗАКРЫВАЕТСЯ
            if event.key == pygame.K_ESCAPE:
                running = False
                pygame.quit()
                sys.exit()
                

            # ЕСЛИ ЖЕ НА ПРОБЕЛ, ТО ЗАПУСКАЕТСЯ КОД ТАНКОВ
            if event.key == pygame.K_SPACE:
                igra()
            
            if event.key == pygame.K_m:
                game_online()

            if event.key == pygame.K_i:
                game_online_ai()

    # ВЫВОДИМ ГЛАВНЫЙ ЭКРАН
    main_screen()


    # ОБНОВЛЯЕМ ЭКРАН ИГРЫ :)
    pygame.display.flip()