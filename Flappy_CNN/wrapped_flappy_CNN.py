import pygame
from pygame.locals import *
import random
from itertools import cycle
import sys
import os
import params # files for all constants
import time
import numpy as np
import cv2

pygame.init()
pygame.display.set_caption('Flappy Bird')
screen = pygame.display.set_mode((params.screen_width, params.screen_height))
fps_clock = pygame.time.Clock()

# Image sprite class
class Image_Sprite(pygame.sprite.Sprite):
    def __init__(self,width,height):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([width, height])
        self.rect = self.image.get_rect()

# Flappy bird game class
class Wrapped_Flappy_CNN():
    def __init__(self):
        # load settings from param file
        self.pipe_vgap = params.pipe_vgap
        self.pipe_hgap = params.pipe_hgap
        self.fps = params.fps
        self.screen_width = params.screen_width
        self.screen_height = params.screen_height
        self.base_line_y = 0.8*self.screen_height # ground y
        self.screen = screen
        self.fps_clock = fps_clock
        # assets paths
        self.background_path_list = ['assets/sprites/background-day.png',
                                     'assets/sprites/background-night.png']
        self.birds_path_list = [
                                # Red birds
                                [
                                    'assets/sprites/redbird-upflap.png',      
                                    'assets/sprites/redbird-midflap.png',     
                                    'assets/sprites/redbird-downflap.png',      
                                ],
                                # Blue birds
                                [
                                    'assets/sprites/bluebird-upflap.png',        
                                    'assets/sprites/bluebird-midflap.png', 
                                    'assets/sprites/bluebird-downflap.png',
                                ],
                                # Yellow birds
                                [
                                    'assets/sprites/yellowbird-upflap.png',
                                    'assets/sprites/yellowbird-midflap.png',
                                    'assets/sprites/yellowbird-downflap.png',
                                ],
        ]
        self.message_path = 'assets/sprites/message.png'
        self.base_line_path = 'assets/sprites/base.png'
        self.pipe_path_list = [
            'assets/sprites/pipe-green.png',
            'assets/sprites/pipe-red.png']

        self.score_numbers_list = [
            pygame.image.load('assets/sprites/0.png').convert_alpha(),
            pygame.image.load('assets/sprites/1.png').convert_alpha(),
            pygame.image.load('assets/sprites/2.png').convert_alpha(),
            pygame.image.load('assets/sprites/3.png').convert_alpha(),
            pygame.image.load('assets/sprites/4.png').convert_alpha(),
            pygame.image.load('assets/sprites/5.png').convert_alpha(),
            pygame.image.load('assets/sprites/6.png').convert_alpha(),
            pygame.image.load('assets/sprites/7.png').convert_alpha(),
            pygame.image.load('assets/sprites/8.png').convert_alpha(),
            pygame.image.load('assets/sprites/9.png').convert_alpha()]

        # load the game over picture
        self.gameover_label = pygame.image.load('assets/sprites/gameover.png').convert_alpha()

        # load the base line picture
        self.base_line = pygame.image.load('assets/sprites/base.png').convert_alpha()

        # load the message picture
        self.message = pygame.image.load(self.message_path).convert_alpha()

        # load bird index sequence
        self.bird_index = 0
        self.bird_index_seq = [0,1,2,1]

        # load the audios
        # check if Windows OS
        if 'win' in sys.platform:
            file_extension = '.wav'
        else:
            file_extension = '.ogg'

        self.sound_die    = pygame.mixer.Sound('assets/audio/die' + file_extension)
        self.sound_hit   = pygame.mixer.Sound('assets/audio/hit' + file_extension)
        self.sound_point  = pygame.mixer.Sound('assets/audio/point' + file_extension)
        self.sound_wing   = pygame.mixer.Sound('assets/audio/wing' + file_extension)

        # start the main game
        self.init_game()

    def init_game(self):
        # load random background
        random_background = random.randint(0,len(self.background_path_list)-1)
        self.background = pygame.image.load(self.background_path_list[random_background]).convert()

        # load random bird
        random_bird = random.randint(0,len(self.birds_path_list)-1)
        self.bird = [pygame.image.load(self.birds_path_list[random_bird][0]).convert_alpha(),
                        pygame.image.load(self.birds_path_list[random_bird][1]).convert_alpha(),
                        pygame.image.load(self.birds_path_list[random_bird][2]).convert_alpha()]
        
        # load random pipe
        random_pipe = random.randint(0,len(self.pipe_path_list)-1)
        self.pipe = [pygame.transform.rotate(pygame.image.load(self.pipe_path_list[0]).convert_alpha(), 180),
                        pygame.image.load(self.pipe_path_list[0]).convert_alpha()]

        # load base line
        self.base_line = pygame.image.load(self.base_line_path).convert_alpha()

        self.bird_x = int(self.screen_width * 0.2)
        self.bird_y = int((self.screen_height - self.bird[0].get_height()) / 2)
        self.base_line_x = 0
        self.base_shift = self.base_line.get_width() - self.background.get_width()
        self.score = 0
         # pipe horizontal gap size 
        pipe_h_gap = params.pipe_hgap

        # generate two sets of random pipes, x value of these pipes depending on the prev one
        # new_pipe_1 is the first pipe in the game
        new_pipe_1 = self.generate_random_pipes(0)
        new_pipe_2 = self.generate_random_pipes(new_pipe_1[0][0])

        # divide them into upper and lower pipes
        self.upper_pipes = [
                            [new_pipe_1[0][0],new_pipe_1[0][1]],
                            [new_pipe_2[0][0],new_pipe_2[0][1]]
                      ]

        self.lower_pipes = [
                            [new_pipe_1[1][0],new_pipe_1[1][1]],
                            [new_pipe_2[1][0],new_pipe_2[1][1]]
                      ]

        # load bird settings
        self.bird_flapping = False

        self.bird_vel_y = params.bird_flap_acc_y
        self.bird_h_angle = params.bird_flap_h_angle
        
    # show score on screen, combine multiple digit images if score is multidigits 
    def show_score(self):
        score_digits = [int(digits) for digits in list(str(self.score))]
        score_width = 0
        
        for digit in score_digits:
            score_width += self.score_numbers_list[digit].get_width()

        score_offset_x = (self.screen_width - score_width) / 2
        for digit in score_digits:
            self.screen.blit(self.score_numbers_list[digit], (score_offset_x, self.screen_height * 0.1))
            score_offset_x += self.score_numbers_list[digit].get_width()

    # generate random (x,y) coordinates for the upper and lower pipes
    def generate_random_pipes(self,prev_pipe_x):
        pip_hgap = params.pipe_hgap
        pipe_image_height = self.pipe[0].get_height()
        upper_pipe_y = random.randint(0,int(0.7*self.base_line_y-self.pipe_vgap))

        upper_pipe_y += self.base_line_y*0.2
        return [[prev_pipe_x + pip_hgap,upper_pipe_y-pipe_image_height],[prev_pipe_x + pip_hgap,upper_pipe_y+params.pipe_vgap]]
    
    # check if bird is crashed, given all pipes
    def bird_crashed(self):
        bird_height = self.bird[0].get_height()
        bird_width = self.bird[0].get_width()
        self.all_pipes_sprites = pygame.sprite.Group()

        # if bird crashed on ground
        if self.bird_y + bird_height >= self.base_line_y:
            # self.sound_hit.play()
            return True
        
        self.bird_sprite = Image_Sprite(bird_width,bird_height)
        self.bird_sprite.rect.x = self.bird_x
        self.bird_sprite.rect.y = self.bird_y

        pipe_height = self.pipe[0].get_height()
        pipe_width = self.pipe[0].get_width()

        for upper_pipe, lower_pipe in zip(self.upper_pipes, self.lower_pipes):
            self.upper_pipe_sprite = Image_Sprite(pipe_width,pipe_height)
            self.lower_pipe_sprite = Image_Sprite(pipe_width,pipe_height)

            self.upper_pipe_sprite.rect.x = upper_pipe[0]
            self.upper_pipe_sprite.rect.y = upper_pipe[1]
            self.lower_pipe_sprite.rect.x = lower_pipe[0]
            self.lower_pipe_sprite.rect.y = lower_pipe[1]

            self.all_pipes_sprites.add(self.upper_pipe_sprite)
            self.all_pipes_sprites.add(self.lower_pipe_sprite)
            
            # using the pygame builtin sprite function
            if pygame.sprite.spritecollide(self.bird_sprite,self.all_pipes_sprites,False):
                # self.sound_hit.play()
                # self.sound_die.play()
                return True
            
            self.all_pipes_sprites.empty()

        return False
    
    def train_step(self,action):
        bird_max_drop_y = params.bird_max_drop_y
        bird_drop_y = params.bird_drop_y
        bird_flap_acc_y = params.bird_flap_acc_y
        bird_drop_h_angle = params.bird_drop_h_angle
        bird_flap_h_angle = params.bird_flap_h_angle
        bird_min_h_angle = params.bird_min_h_angle

        pygame.event.pump()
  
        if action == 'f':
            # if action is flap
            if (self.bird_y + self.bird[0].get_height() / 2) > 0:
                # self.sound_wing.play()
                self.bird_flapping = True
                self.bird_vel_y = bird_flap_acc_y

         # bird movement
        if self.bird_h_angle >= bird_min_h_angle:
            self.bird_h_angle += bird_drop_h_angle  

        if self.bird_vel_y < bird_max_drop_y and self.bird_flapping == False:
            self.bird_vel_y += bird_drop_y

        if self.bird_flapping:
            self.bird_flapping = False
            self.bird_h_angle = bird_flap_h_angle

        self.bird_y += self.bird_vel_y
        
        # count score
        self.bird_mid_x = self.bird_x + self.bird[0].get_width() / 2
        for upper_pipe in self.upper_pipes:
            upper_pipe_mid_x = upper_pipe[0] + self.pipe[0].get_width() / 2
            if upper_pipe_mid_x <= self.bird_mid_x < upper_pipe_mid_x + (- params.pipe_x_vel):
                # self.sound_point.play()
                self.score += 1

        # move baseline
        self.base_line_x = -((-self.base_line_x + 100) % self.base_shift)

        # iterate bird index
        self.bird_index = (self.bird_index+1) % 4

        # draw the images
        self.screen.blit(self.background,(0,0))
        self.bird_surface = pygame.transform.rotate(self.bird[self.bird_index_seq[self.bird_index]],self.bird_h_angle)
        self.screen.blit(self.bird_surface,(self.bird_x,self.bird_y))
        
        # move the pipes to the left and draw them
        for upper_pipe, lower_pipe in zip(self.upper_pipes,self.lower_pipes):
            upper_pipe[0] += params.pipe_x_vel
            lower_pipe[0] += params.pipe_x_vel 

        for upper_pipe, lower_pipe in zip(self.upper_pipes,self.lower_pipes):         
            self.screen.blit(self.pipe[0], (upper_pipe[0], upper_pipe[1]))
            self.screen.blit(self.pipe[1], (lower_pipe[0], lower_pipe[1]))
        
        # if leftmost pipe is touching the left border, or there are enough space to draw the next set of pipes
        # generate a new set of pipes
        if 0 < self.upper_pipes[0][0] < -(params.pipe_x_vel-1) or self.upper_pipes[-1][0] <= self.screen_width: 
            new_pipe = self.generate_random_pipes(self.upper_pipes[-1][0])
            self.upper_pipes.append(new_pipe[0])
            self.lower_pipes.append(new_pipe[1])
        
        # if pipes are touching the left border, remove them from pipes list
        if self.upper_pipes[0][0] < -self.pipe[0].get_width():
            self.upper_pipes.pop(0)
            self.lower_pipes.pop(0)

        if self.bird_crashed():
            terminated = True
            reward = -1
            self.init_game()

        # draw base line 
        self.screen.blit(self.base_line,(self.base_line_x,self.base_line_y))
        # draw score
        self.show_score()

        pygame.display.update()
        self.fps_clock.tick(self.fps)

        return self.get_screen()

    def get_screen(self):
        screen = pygame.surfarray.array3d(pygame.display.get_surface())
        screen = screen[:,int(self.screen_height*0.1+self.score_numbers_list[0].get_height()):int(self.base_line_y)]
        screen = cv2.resize(screen, (80, 80))
        return np.reshape(screen,[1,80,80,3])
            
if __name__ == "__main__":
    pass
