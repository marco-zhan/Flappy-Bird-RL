import random
import time
# set random seeds for generating random pipes
seed = int(time.time())
random.seed(seed)
import os
import argparse
import pygame
import sys
from pygame.locals import *

# define game modes 
from enum import Enum
class Mode(Enum):
    HUMAN = 1
    AI = 2
    TRAIN = 3
    TRAIN_NOUI = 4

# import DQN brain
from brain import Brain 
brain = Brain()

# settings
SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512
PIPE_V_GAP = 100
PIPE_H_GAP = 200
PIPE_VEL = -4

BASE_Y = 0.8 * SCREEN_HEIGHT
MODE = Mode.HUMAN

IMAGE, SOUND = {}, {} # images and sound dictionary

SCORES = [] # past score list

BIRD_PATH_LIST = [
    # Red birds
    [
        '../assets/sprites/redbird-upflap.png',      
        '../assets/sprites/redbird-midflap.png',     
        '../assets/sprites/redbird-downflap.png',      
    ],
    # Blue birds
    [
        '../assets/sprites/bluebird-upflap.png',        
        '../assets/sprites/bluebird-midflap.png', 
        '../assets/sprites/bluebird-downflap.png',
    ],
    # Yellow birds
    [
        '../assets/sprites/yellowbird-upflap.png',
        '../assets/sprites/yellowbird-midflap.png',
        '../assets/sprites/yellowbird-downflap.png',
    ]]

BIRD_INDEX_SEQ = [0,1,2,1]

BACKGROUND_PATH_LIST = [
    '../assets/sprites/background-day.png',
    '../assets/sprites/background-night.png']

PIPE_PATH_LIST = [
    '../assets/sprites/pipe-green.png',
    '../assets/sprites/pipe-red.png']


# Image sprite class
# This class is used to detect collision
class Image_Sprite(pygame.sprite.Sprite):
    def __init__(self,width,height):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([width, height])
        self.rect = self.image.get_rect()

def main():
    global SCREEN, FPSCLOCK, FPS, bot, MODE, SCORES, EPISODE, MAX_SCORE
    parser = argparse.ArgumentParser("flappy.py")
    parser.add_argument("--fps", type=int, default=60, help="number of frames per second, default 60")
    parser.add_argument("--mode", action="store", choices=('human','ai','train','train_noui'), default='human',help="choose the game mode")
    parser.add_argument("--episode", type=int, default=1000, help="episode number, default: 1000")
    parser.add_argument("--max", type=int, default=1000, help="max score to train, default: 1000")

    args = parser.parse_args()

    FPS = args.fps
    EPISODE = args.episode
    MAX_SCORE = args.max

    if args.mode == "human":
        MODE = Mode.HUMAN
        FPS = 30

    elif args.mode == "ai":
        MODE = Mode.AI

    elif args.mode == "train":
        MODE = Mode.TRAIN
    
    elif args.mode == "train_noui":
        MODE = Mode.TRAIN_NOUI
        FPS = 120

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # load score numbers image
    IMAGE["number"] = [
            pygame.image.load('../assets/sprites/0.png').convert_alpha(),
            pygame.image.load('../assets/sprites/1.png').convert_alpha(),
            pygame.image.load('../assets/sprites/2.png').convert_alpha(),
            pygame.image.load('../assets/sprites/3.png').convert_alpha(),
            pygame.image.load('../assets/sprites/4.png').convert_alpha(),
            pygame.image.load('../assets/sprites/5.png').convert_alpha(),
            pygame.image.load('../assets/sprites/6.png').convert_alpha(),
            pygame.image.load('../assets/sprites/7.png').convert_alpha(),
            pygame.image.load('../assets/sprites/8.png').convert_alpha(),
            pygame.image.load('../assets/sprites/9.png').convert_alpha()]

    # load the game over image
    IMAGE["gameover"] = pygame.image.load('../assets/sprites/gameover.png').convert_alpha()

    # load the base line image
    IMAGE["base"]= pygame.image.load('../assets/sprites/base.png').convert_alpha()

    # load the message image
    IMAGE["message"] = pygame.image.load('../assets/sprites/message.png').convert_alpha()

    # load sound tracks
    if 'win' in sys.platform:
        file_extension = '.wav'
    else:
        file_extension = '.ogg'

    SOUND["die"]   = pygame.mixer.Sound('../assets/audio/die' + file_extension)
    SOUND["hit"]   = pygame.mixer.Sound('../assets/audio/hit' + file_extension)
    SOUND["point"] = pygame.mixer.Sound('../assets/audio/point' + file_extension)
    SOUND["wing"]  = pygame.mixer.Sound('../assets/audio/wing' + file_extension)

    while True:
        # load random background
        random_background = random.randint(0,len(BACKGROUND_PATH_LIST)-1)
        IMAGE["background"] = pygame.image.load(BACKGROUND_PATH_LIST[random_background]).convert()

        # load random bird
        random_bird = random.randint(0,len(BIRD_PATH_LIST)-1)
        IMAGE["bird"] = [
            pygame.image.load(BIRD_PATH_LIST[random_bird][0]).convert_alpha(),
            pygame.image.load(BIRD_PATH_LIST[random_bird][1]).convert_alpha(),
            pygame.image.load(BIRD_PATH_LIST[random_bird][2]).convert_alpha()]
        
        # load random pipe
        random_pipe = random.randint(0,len(PIPE_PATH_LIST)-1)
        IMAGE["pipe"] = [
            pygame.transform.rotate(pygame.image.load(PIPE_PATH_LIST[random_pipe]).convert_alpha(), 180),
            pygame.image.load(PIPE_PATH_LIST[random_pipe]).convert_alpha()]

        # show the welcome screen
        movement_info = show_welcome_screen()
        # if welcome screen returns, use the returned position to start main game
        position_info = main_game(movement_info)
        # # if crash_info returns, use the returned position to show gameover screen
        show_gameover_screen(position_info)

# show welcome screen
def show_welcome_screen():
    # coordinates infos
    BIRD_WIDTH = IMAGE["bird"][0].get_width()
    BIRD_HEIGHT = IMAGE["bird"][0].get_height()

    MESSAGE_WIDTH =  IMAGE["message"].get_width()
    MESSAGE_HEIGHT =  IMAGE["message"].get_height()

    bird_index = 0
    
    bird_x = int(SCREEN_WIDTH*0.2)
    bird_y = int((SCREEN_HEIGHT - BIRD_HEIGHT) / 2)

    message_x = int((SCREEN_WIDTH - MESSAGE_WIDTH) / 2)
    message_y = int(SCREEN_HEIGHT * 0.1)

    base_x = 0

    base_shift = IMAGE['base'].get_width() - IMAGE['background'].get_width()

    osc_value = [0,'i'] # oscalliation y value and direction (inrease or decrease)

    # skip out welcome screen if playing in AI or train mode 
    if MODE != Mode.HUMAN:
        pygame.event.pump() # pump the game to avoid "no response issue"
        if MODE != Mode.TRAIN_NOUI:
            SOUND["wing"].play()
        return [bird_y+osc_value[0], base_x, bird_index]

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                # return out if space or up are pressed
                if MODE != Mode.TRAIN_NOUI:
                    SOUND["wing"].play()
                return [bird_y+osc_value[0], base_x, bird_index]
        
        # loop through bird index
        bird_index = (bird_index+1) % 4

        # welcome screen bird move up and down using some simple if statement
        if osc_value[1] == 'i':
            osc_value[0] += 1
        else:
            osc_value[0] -= 1

        if osc_value[0] > 10:
            osc_value[1] = 'd'
        elif osc_value[0] < -10:
            osc_value[1] = 'i'
        
        # base line movement 
        base_x = -((-base_x + 4) % base_shift)
        
        # draw the images
        SCREEN.blit(IMAGE["background"], (0,0))
        SCREEN.blit(IMAGE["message"],(message_x,message_y))
        SCREEN.blit(IMAGE["bird"][BIRD_INDEX_SEQ[bird_index]],(bird_x,bird_y + osc_value[0]))
        SCREEN.blit(IMAGE["base"], (base_x,BASE_Y))

        pygame.display.update()
        FPSCLOCK.tick(FPS)

# operate the main game
def main_game(movement_info):
    score = 0
    bird_y, base_x, bird_index = movement_info
    bird_x = SCREEN_WIDTH * 0.2
    base_shift = IMAGE['base'].get_width() - IMAGE['background'].get_width()

    # generate random pipes, the argument passed in is the the previous pipe x
    # the horizontal distance between pipes can be changed by altering PIPE_H_GAP global variable
    new_pipe_1 = generate_random_pipes(SCREEN_WIDTH/2)
    new_pipe_2 = generate_random_pipes(new_pipe_1[0][0])

    # divide them into upper and lower pipes
    upper_pipes = [
        [new_pipe_1[0][0],new_pipe_1[0][1]],
        [new_pipe_2[0][0],new_pipe_2[0][1]]]

    lower_pipes = [
        [new_pipe_1[1][0],new_pipe_1[1][1]],
        [new_pipe_2[1][0],new_pipe_2[1][1]]]
    
    bird_drop_y = 1 # bird downward accelration in pixels
    bird_flap_acc_y = -9 # bird flap acceleration in pixels
    bird_max_drop_y = 10 # bird maximum downward acceleration
    bird_max_acc_y = 8 # bird max ascend speed
    bird_flap_h_angle = 20 # bird flap horizontal up angle
    bird_drop_h_angle = -3 # bird dropping angle 
    bird_min_h_angle = -90 # bird maximum dropping angle

    bird_flapping = False
    bird_vel_y = -9
    bird_h_angle = 20

    while True:
        # if playing in human mode, check keyboard inputs
        if MODE == Mode.HUMAN:
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                    if bird_y > -2 * IMAGE["bird"][0].get_height():
                        SOUND["wing"].play()
                        bird_flapping = True
                        bird_vel_y = bird_flap_acc_y
        
        # if playing in AI mode or Train mode, get action from brain
        elif brain.act(bird_x, bird_y, bird_vel_y, lower_pipes):
            pygame.event.pump()
            if bird_y > -2 * IMAGE["bird"][0].get_height():
                if MODE != Mode.TRAIN_NOUI:
                    SOUND["wing"].play()
                bird_flapping = True
                bird_vel_y = bird_flap_acc_y

        # pump the game to avoid "no response" issue
        else: pygame.event.pump()
        
        # check if the bird is crashed return crash_info if true
        if bird_crashed(bird_x,bird_y,upper_pipes,lower_pipes):
            # update score if in training mode
            if MODE == Mode.TRAIN or MODE == Mode.TRAIN_NOUI:
                brain.update_score(score)

            return [bird_x,bird_y,bird_vel_y,bird_h_angle,upper_pipes,lower_pipes,base_x,score]
        
        # count score
        bird_mid_x = bird_x + IMAGE["bird"][0].get_width() / 2
        for upper_pipe in upper_pipes:
            upper_pipe_mid_x = upper_pipe[0] + IMAGE["pipe"][0].get_width() / 2
            if upper_pipe_mid_x <= bird_mid_x < upper_pipe_mid_x + (-PIPE_VEL):
                if MODE != Mode.TRAIN_NOUI:
                    SOUND['point'].play()
                score += 1

                # terminate game if max score reached
                if score >= MAX_SCORE:
                    brain.terminate_game()
                    print("\nMax Training Score Reached")
                    exit(1)

        # bird movement
        if bird_h_angle >= bird_min_h_angle:
            bird_h_angle += bird_drop_h_angle  

        if bird_vel_y < bird_max_drop_y and bird_flapping == False:
            bird_vel_y += bird_drop_y

        if bird_flapping:
            bird_flapping = False
            bird_h_angle = bird_flap_h_angle

        bird_y += bird_vel_y
        
        #move the pipes to the left and draw them
        for upper_pipe, lower_pipe in zip(upper_pipes,lower_pipes):
            upper_pipe[0] += PIPE_VEL
            lower_pipe[0] += PIPE_VEL 
        
        # if leftmost pipe is touching the left border, or there are enough space to draw the next set of pipes
        # generate a new set of pipes
        if 0 < upper_pipes[0][0] < -(PIPE_VEL-1) or upper_pipes[-1][0] <= SCREEN_WIDTH: 
            new_pipe = generate_random_pipes(upper_pipes[-1][0])
            upper_pipes.append(new_pipe[0])
            lower_pipes.append(new_pipe[1])
        
        # if pipes are touching the left border, remove them from pipes list
        if upper_pipes[0][0] < -IMAGE['pipe'][0].get_width():
            upper_pipes.pop(0)
            lower_pipes.pop(0)

        # move baseline
        base_x = -((-base_x + 100) % base_shift)

        # iterate bird index
        bird_index = (bird_index+1) % 4

        # draw images
        if MODE != Mode.TRAIN_NOUI:
            SCREEN.blit(IMAGE['background'], (0,0))

            for upper_pipe, lower_pipe in zip(upper_pipes, lower_pipes):
                SCREEN.blit(IMAGE["pipe"][0], (upper_pipe[0], upper_pipe[1]))
                SCREEN.blit(IMAGE["pipe"][1], (lower_pipe[0], lower_pipe[1]))

            SCREEN.blit(IMAGE["base"], (base_x, BASE_Y))
            show_score(score)

            bird_surface = pygame.transform.rotate(IMAGE["bird"][1], bird_h_angle)

            SCREEN.blit(bird_surface, (bird_x,bird_y))

            pygame.display.update()
            FPSCLOCK.tick(FPS)

# show the game over screen
def show_gameover_screen(position_info):
    bird_x,bird_y,bird_vel_y,bird_h_angle,upper_pipes,lower_pipes,base_x,score = position_info
    if MODE != Mode.HUMAN:
        update_Q_table(score)
        pygame.event.pump()
        return
    bird_drop_y = 1 # bird downward accelration in pixels
    bird_flap_acc_y = -9 # bird flap acceleration in pixels
    bird_max_drop_y = 10 # bird maximum downward acceleration
    bird_max_acc_y = 8 # bird max ascend speed
    bird_flap_h_angle = 20 # bird flap horizontal up angle
    bird_drop_h_angle = -3 # bird dropping angle 
    bird_min_h_angle = -90 # bird maximum dropping angle

    bird_height = IMAGE['bird'][0].get_height()
    
    on_ground = False

    gameover_x = int((SCREEN_WIDTH - IMAGE["gameover"].get_width()) / 2)
    gameover_y = int(SCREEN_HEIGHT * 0.4)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if bird_y + bird_height > BASE_Y - 1: # this is to check bird is on the ground
                    return
        # bird movement
        if bird_y + bird_height < BASE_Y- 1:
            bird_y += bird_vel_y
        else: on_ground = True

        if bird_vel_y < 15:
            bird_vel_y += (bird_drop_y+1)
        
        if bird_h_angle >= bird_min_h_angle and not on_ground:
            bird_h_angle += (bird_drop_h_angle*3) 
        
        # draw images
        SCREEN.blit(IMAGE["background"], (0,0))

        for upper_pipe, lower_pipe in zip(upper_pipes, lower_pipes):
            SCREEN.blit(IMAGE["pipe"][0], (upper_pipe[0], upper_pipe[1]))
            SCREEN.blit(IMAGE["pipe"][1], (lower_pipe[0], lower_pipe[1]))

        SCREEN.blit(IMAGE["base"], (base_x, BASE_Y))
        show_score(score)

        bird_surface = pygame.transform.rotate(IMAGE["bird"][1], bird_h_angle)
        SCREEN.blit(IMAGE["gameover"], (gameover_x, gameover_y))

        SCREEN.blit(bird_surface, (bird_x,bird_y))

        FPSCLOCK.tick(FPS)
        pygame.display.update()

def update_Q_table(score):
    print("Game " + str(brain.cycle_count) + ": " + "Score: " + str(score))

    if MODE == Mode.TRAIN or MODE == Mode.TRAIN_NOUI:
        brain.dump_qvalues()

    if brain.cycle_count >= EPISODE:
        print("Training finished")
        exit(1)
    
    if score > max(SCORES, default=0):
        print("\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        print("\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        print("$$$$$$$$ NEW RECORD: %d $$$$$$$$" % score)
        print("\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n")

    SCORES.append(score)

def generate_random_pipes(prev_pipe_x):
    pipe_height = IMAGE['pipe'][0].get_height()
    upper_pipe_y = random.randint(0,int(0.7*BASE_Y-PIPE_V_GAP))

    upper_pipe_y += BASE_Y*0.2
    return [[prev_pipe_x + PIPE_H_GAP,upper_pipe_y-pipe_height],[prev_pipe_x + PIPE_H_GAP,upper_pipe_y+PIPE_V_GAP]]

def bird_crashed(bird_x,bird_y,upper_pipes,lower_pipes):
    bird_height = IMAGE['bird'][0].get_height()
    bird_width = IMAGE['bird'][0].get_width()
    all_pipes_sprites = pygame.sprite.Group()

    # if bird crashed on ground
    if bird_y + bird_height >= BASE_Y:
        if MODE != Mode.TRAIN_NOUI:
            SOUND["hit"].play()
        return True
    
    bird_sprite = Image_Sprite(bird_width,bird_height)
    bird_sprite.rect.x = bird_x
    bird_sprite.rect.y = bird_y

    pipe_height = IMAGE["pipe"][0].get_height()
    pipe_width = IMAGE["pipe"][0].get_width()

    for upper_pipe, lower_pipe in zip(upper_pipes, lower_pipes):
        upper_pipe_sprite = Image_Sprite(pipe_width,pipe_height)
        lower_pipe_sprite = Image_Sprite(pipe_width,pipe_height)

        upper_pipe_sprite.rect.x = upper_pipe[0]
        upper_pipe_sprite.rect.y = upper_pipe[1]
        lower_pipe_sprite.rect.x = lower_pipe[0]
        lower_pipe_sprite.rect.y = lower_pipe[1]

        all_pipes_sprites.add(upper_pipe_sprite)
        all_pipes_sprites.add(lower_pipe_sprite)
        
        # using the pygame builtin sprite function
        if pygame.sprite.spritecollide(bird_sprite,all_pipes_sprites,False):
            if MODE != Mode.TRAIN_NOUI:
                SOUND["hit"].play()
                SOUND["die"].play()
            return True
    return False

def show_score(score):
    score_digits = [int(digits) for digits in list(str(score))]
    score_width = 0
    
    for digit in score_digits:
        score_width += IMAGE["number"][digit].get_width()

    score_offset_x = (SCREEN_WIDTH - score_width) / 2
    for digit in score_digits:
        SCREEN.blit(IMAGE["number"][digit], (score_offset_x, SCREEN_HEIGHT * 0.1))
        score_offset_x += IMAGE["number"][digit].get_width()
        
if __name__ == "__main__":
    main()

