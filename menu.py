import pygame

from game import *

def text_objects(text, font):
    textSurface = font.render(text, True, black)
    return textSurface, textSurface.get_rect()

def game_menu():
    screen = pygame.display.get_surface()
    clock = pygame.time.Clock()
    intro = True
    selection = 0
    cursor = pygame.Rect(display_width / 4, display_height * (selection + 3)/5 - 15, 30, 30)

    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                quit()
            
        key = pygame.key.get_pressed()
        if (key[K_s] or key[K_DOWN]) and selection == 0:
            cursor.y += display_height / 5
            selection = 1
        if (key[K_w] or key[K_UP]) and selection == 1:
            cursor.y -= display_height / 5
            selection = 0
        if key[K_RETURN]:
            intro = False
            return selection

        screen.fill(white)
        large_text = pygame.font.Font('freesansbold.ttf',115)
        small_text = pygame.font.Font('freesansbold.ttf', 40)

        TextSurf, TextRect = text_objects("ColorRunner", large_text)
        TextRect.center = ((display_width/2),(display_height/4))
        screen.blit(TextSurf, TextRect)

        TextSurf, TextRect = text_objects("Start Game", small_text)
        TextRect.center = ((display_width/2),(display_height*3/5))
        screen.blit(TextSurf, TextRect)

        TextSurf, TextRect = text_objects("Level Creator", small_text)
        TextRect.center = ((display_width/2),(display_height*4/5))
        screen.blit(TextSurf, TextRect)

        pygame.draw.rect(screen, red, cursor)

        pygame.display.update()
        clock.tick(15)
