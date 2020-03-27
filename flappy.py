import pygame
from pygame.locals import *
import random
from itertools import cycle
import sys
import params # files for all constants

class Image_Sprite(pygame.sprite.Sprite):
        def __init__(self,width,height):

            pygame.sprite.Sprite.__init__(self)

            self.image = pygame.Surface([width, height])
            self.rect = self.image.get_rect()

class Flappy():
    def __init__(self):
        self.pipe_vgap = params.pipe_vgap
        self.pipe_hgap = params.pipe_hgap
        # resolution settings
        self.fps = params.fps
        self.screen_width = params.screen_width
        self.screen_height = params.screen_height
        self.base_line_y = 0.8*self.screen_height

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

        # start the main game
        self.init_game()

    def init_game(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.fps_clock = pygame.time.Clock()
        pygame.display.set_caption('Flappy Bird')

        # load the score numbers picture
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

        # load the audios
        # check if Windows OS
        if 'win' in sys.platform:
            file_extension = '.wav'
        else:
            file_extension = '.ogg'

        self.sound_die    = pygame.mixer.Sound('assets/audio/die' + file_extension)
        self.sound_hit   = pygame.mixer.Sound('assets/audio/hit' + file_extension)
        self.sound_point  = pygame.mixer.Sound('assets/audio/point' + file_extension)
        self.sound_swoosh = pygame.mixer.Sound('assets/audio/swoosh' + file_extension)
        self.sound_wing   = pygame.mixer.Sound('assets/audio/wing' + file_extension)

        while True:
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
            self.pipe = [pygame.transform.rotate(pygame.image.load(self.pipe_path_list[random_pipe]).convert_alpha(), 180),
                         pygame.image.load(self.pipe_path_list[random_pipe]).convert_alpha()]

            # load base line
            self.base_line = pygame.image.load(self.base_line_path).convert_alpha()

            # show the welcome screen
            initial_pose = self.show_welcome_screen()
            # if welcome screen returns, use the returned position to start main game
            crash_info = self.main_game(initial_pose)
            # if crash_info returns, use the returned position to show gameover screen
            self.show_gameover_screen(crash_info)

    def show_welcome_screen(self):
        # coordinates of all items
        bird_index = 0
        bird_index_seq = [0,1,2,1]

        osc_value = [0,'i']
        bird_x = int(self.screen_width * 0.2)
        bird_y = int((self.screen_height - self.bird[0].get_height()) / 2)

        messagex = int((self.screen_width - self.message.get_width()) / 2)
        messagey = int(self.screen_height * 0.1)

        base_line_x = 0
        base_shift = self.base_line.get_width() - self.background.get_width()

        while True:
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                    self.sound_wing.play()
                    return [base_line_x,bird_index,bird_y+osc_value[0]]

            bird_index = (bird_index+1) % 4

            if osc_value[1] == 'i':
                osc_value[0] += 1
            else:
                osc_value[0] -= 1

            if osc_value[0] > 10:
                osc_value[1] = 'd'
            elif osc_value[0] < -10:
                osc_value[1] = 'i'
            
            base_line_x = -((-base_line_x + 4) % base_shift)

            self.screen.blit(self.background, (0,0))
            self.screen.blit(self.message,(messagex,messagey))
            self.screen.blit(self.bird[bird_index_seq[bird_index]],(bird_x,bird_y + osc_value[0]))
            self.screen.blit(self.base_line, (base_line_x,self.base_line_y))

            pygame.display.update()
            self.fps_clock.tick(self.fps)
    
    def main_game(self,initial_pose):
        score = 0

        bird_index = 0
        bird_index_seq = [0,1,2,1]
        
        bird_x = self.screen_width*0.2
        bird_y = initial_pose[2]

        base_line_x = initial_pose[0]
        base_shift = self.base_line.get_width() - self.background.get_width()

        # generate two sets of random pipes
        new_pipe_1 = self.generate_random_pipes()
        new_pipe_2 = self.generate_random_pipes()

        # divide them into upper and lower pipes
        upper_pipes = [
                            [new_pipe_1[0][0],new_pipe_1[0][1]],
                            [new_pipe_2[0][0]+params.pipe_hgap,new_pipe_2[0][1]]
                      ]

        lower_pipes = [
                            [new_pipe_1[1][0],new_pipe_1[1][1]],
                            [new_pipe_2[1][0]+params.pipe_hgap,new_pipe_2[1][1]]
                      ]

        bird_flapping = False
        bird_max_drop_y = params.bird_max_drop_y
        bird_drop_y = params.bird_drop_y
        bird_flap_acc_y = params.bird_flap_acc_y
        bird_drop_h_angle = params.bird_drop_h_angle
        bird_flap_h_angle = params.bird_flap_h_angle
        bird_min_h_angle = params.bird_min_h_angle

        bird_vel_y = bird_flap_acc_y
        bird_h_angle = bird_flap_h_angle
        

        while True:
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                    if (bird_y + self.bird[0].get_height() / 2) > 0:
                        self.sound_wing.play()
                        bird_flapping = True
                        bird_vel_y = bird_flap_acc_y
                        
            # check if the bird is crashed
            if self.bird_crashed([bird_x,bird_y,bird_index_seq[bird_index]],upper_pipes,lower_pipes):
                return [bird_x,bird_y,bird_vel_y,bird_h_angle,base_line_x,upper_pipes,lower_pipes,score]
            # bird movement
            if bird_h_angle >= bird_min_h_angle:
                bird_h_angle += bird_drop_h_angle  

            if bird_vel_y < bird_max_drop_y and bird_flapping == False:
                bird_vel_y += bird_drop_y

            if bird_flapping:
                bird_flapping = False
                bird_h_angle = bird_flap_h_angle

            bird_y += bird_vel_y
            
            bird_mid_x = bird_x + self.bird[0].get_width() / 2
            for upper_pipe in upper_pipes:
                upper_pipe_mid_x = upper_pipe[0] + self.pipe[0].get_width() / 2
                if upper_pipe_mid_x <= bird_mid_x <= upper_pipe_mid_x + (- params.pipe_x_vel):
                    self.sound_point.play()
                    score += 1

            base_line_x = -((-base_line_x + 100) % base_shift)

            bird_index = (bird_index+1) % 4

            for upper_pipe, lower_pipe in zip(upper_pipes,lower_pipes):
                upper_pipe[0] += params.pipe_x_vel
                lower_pipe[0] += params.pipe_x_vel 

            self.screen.blit(self.background,(0,0))
            bird_surface = pygame.transform.rotate(self.bird[bird_index_seq[bird_index]],bird_h_angle)
            self.screen.blit(bird_surface,(bird_x,bird_y))
            
            # move the pipes to the left and draw them
            for upper_pipe, lower_pipe in zip(upper_pipes,lower_pipes):         
                self.screen.blit(self.pipe[0], (upper_pipe[0], upper_pipe[1]))
                self.screen.blit(self.pipe[1], (lower_pipe[0], lower_pipe[1]))

            # draw new pipes when the leftmost pipe is touching the left border
            if 0 < upper_pipes[0][0] < -(params.pipe_x_vel-1):
                new_pipe = self.generate_random_pipes()
                upper_pipes.append(new_pipe[0])
                lower_pipes.append(new_pipe[1])
            
            if upper_pipes[0][0] < -self.pipe[0].get_width():
                upper_pipes.pop(0)
                lower_pipes.pop(0)

            self.screen.blit(self.base_line,(base_line_x,self.base_line_y))
            self.show_score(score)
            pygame.display.update()
            self.fps_clock.tick(self.fps)

    def show_gameover_screen(self,crash_info):
        bird_x,bird_y,bird_vel_y,bird_h_angle,base_line_x,upper_pipes,lower_pipes,score = crash_info

        bird_max_drop_y = params.bird_max_drop_y
        bird_drop_y = params.bird_drop_y
        bird_drop_h_angle = params.bird_drop_h_angle
        bird_min_h_angle = params.bird_min_h_angle

        bird_height = self.bird[0].get_height()

        while True:
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                    if bird_y + bird_height > self.base_line_y - 1:
                        return
            
            if bird_y + bird_height < self.base_line_y - 1:
                bird_y += bird_vel_y

            if bird_vel_y < 15:
                bird_vel_y += (bird_drop_y+1)

            if bird_h_angle >= bird_min_h_angle:
                bird_h_angle += (bird_drop_h_angle*3) 

            self.screen.blit(self.background, (0,0))

            for upper_pipe, lower_pipe in zip(upper_pipes, lower_pipes):
                self.screen.blit(self.pipe[0], (upper_pipe[0], upper_pipe[1]))
                self.screen.blit(self.pipe[1], (lower_pipe[0], lower_pipe[1]))

            self.screen.blit(self.base_line, (base_line_x, self.base_line_y))
            self.show_score(score)

            bird_surface = pygame.transform.rotate(self.bird[1], bird_h_angle)

            self.screen.blit(bird_surface, (bird_x,bird_y))

            self.fps_clock.tick(self.fps)
            pygame.display.update()
    
    def show_score(self,score):
        score_digits = [int(digits) for digits in list(str(score))]
        score_width = 0
        
        for digit in score_digits:
            score_width += self.score_numbers_list[digit].get_width()

        score_offset_x = (self.screen_width - score_width) / 2
        for digit in score_digits:
            self.screen.blit(self.score_numbers_list[digit], (score_offset_x, self.screen_height * 0.1))
            score_offset_x += self.score_numbers_list[digit].get_width()

    # generate random (x,y) coordinates for the upper and lower pipes
    def generate_random_pipes(self):
        pipe_image_height = self.pipe[0].get_height()
        upper_pipe_y = random.randint(0,int(0.7*self.base_line_y-self.pipe_vgap))

        upper_pipe_y += self.base_line_y*0.2
        return [[self.screen_width,upper_pipe_y-pipe_image_height],[self.screen_width,upper_pipe_y+params.pipe_vgap]]
    
    def bird_crashed(self,bird_info,upper_pipes,lower_pipes):
        bird_height = self.bird[0].get_height()
        bird_width = self.bird[0].get_width()
        bird_x, bird_y, bird_index = bird_info
        all_pipes_sprites = pygame.sprite.Group()

        if bird_y + bird_height >= self.base_line_y:
            self.sound_hit.play()
            return True
        
        bird_sprite = Image_Sprite(bird_width,bird_height)
        bird_sprite.rect.x = bird_x
        bird_sprite.rect.y = bird_y

        pipe_height = self.pipe[0].get_height()
        pipe_width = self.pipe[0].get_width()

        for upper_pipe, lower_pipe in zip(upper_pipes, lower_pipes):
            upper_pipe_sprite = Image_Sprite(pipe_width,pipe_height)
            lower_pipe_sprite = Image_Sprite(pipe_width,pipe_height)

            upper_pipe_sprite.rect.x = upper_pipe[0]
            upper_pipe_sprite.rect.y = upper_pipe[1]
            lower_pipe_sprite.rect.x = lower_pipe[0]
            lower_pipe_sprite.rect.y = lower_pipe[1]

            all_pipes_sprites.add(upper_pipe_sprite)
            all_pipes_sprites.add(lower_pipe_sprite)

            if pygame.sprite.spritecollide(bird_sprite,all_pipes_sprites,False):
                self.sound_hit.play()
                self.sound_die.play()
                return True
            
            all_pipes_sprites.empty()

        return False

if __name__ == "__main__":
    f = Flappy()
