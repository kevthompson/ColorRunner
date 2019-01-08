import os, sys
import json
import pygame
from pygame.locals import *

from objects import *

    
if not pygame.font: print("Warning, fonts disabled")
if not pygame.mixer: print("Warning, sound disabled")

pygame.init()
pygame.display.set_caption('ColorRunner')
pygame.mouse.set_visible(0)

clock = pygame.time.Clock()

game = Game()

shiftingLeft = 0
shiftingRight = 0
running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
    key = pygame.key.get_pressed()

    if key[pygame.K_w]:
        game.player.jump()
        if key[pygame.K_a]:
            game.player.walljumpleft()
        if key[pygame.K_d]:
            game.player.walljumpright()
    if key[pygame.K_a]:
        game.player.move_left()
    if key[pygame.K_d]:
        game.player.move_right()
    if key[pygame.K_q] and shiftingLeft < 0:
        game.player.shiftColorLeft()
        shiftingLeft = 10
        shiftingRight = 0
    if key[pygame.K_e] and shiftingRight < 0:
        game.player.shiftColorRight()
        shiftingRight = 10
        shiftingLeft = 0

    shiftingLeft -= 1
    shiftingRight -= 1
    
    game.update()
