import pygame
from pygame.locals import *

class Flappy():
    def __init__(self):
        pygame.init()
        self.screen_width = 300
        self.screen_height = 520
        self.screen = pygame.display.set_mode((self.screen_width,self.screen_height))
        pygame.display.set_caption("Flappy Bird")
        
        self.start_game()

    def start_game(self):
        while True:
            pass

if __name__ == "__main__":
    f = Flappy()
