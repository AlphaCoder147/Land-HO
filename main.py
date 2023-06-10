import pygame, sys
from settings import *
from level import *
from game_data import *
pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
level = Level(level_0, screen)
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:   
            pygame.quit()
            sys.exit()
    screen.fill('black')
    level.run()
    pygame.display.update()
    clock.tick(60)          