import pygame

from game import *

def creator_loop():
    screen = pygame.display.get_surface()
    clock = pygame.time.Clock()
    tile_pos = (0, 0)
    player_move = 0
    shifting_left = 0
    shifting_right = 0
    running = True
    player, goal, platforms = load_level("base")
    color = red
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                quit()
            elif event.type == KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                quit()

        key = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        cur_tile = pygame.Rect(tile_width * (mouse_pos[0] // tile_width), tile_width * (mouse_pos[1] // tile_width), tile_width, tile_width)

        if player_move < 0:
            if key[pygame.K_w]:
                player.rect.y = player.rect.y - tile_width
                player_move = 10
            if key[pygame.K_s]:
                player.rect.y = player.rect.y + tile_width
                player_move = 10
            if key[pygame.K_a]:
                player_move = 10
                player.rect.x = player.rect.x - tile_width
            if key[pygame.K_d]:
                player.rect.x = player.rect.x + tile_width
                player_move = 10
        if key[pygame.K_q] and shifting_left < 0:
            color = shift_color_left(color)
            shifting_left = 10
            shifting_right = 0
        if key[pygame.K_e] and shifting_right < 0:
            color = shift_color_right(color)
            shifting_right = 10
            shifting_left = 0

        shifting_left -= 1
        shifting_right -= 1
        player_move -= 1

        draw(player, goal, platforms)
        pygame.draw.rect(screen, color, cur_tile)
        pygame.display.flip()