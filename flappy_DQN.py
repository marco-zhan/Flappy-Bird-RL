import tensorflow as tf
import cv2
import numpy as np 
import random
import flappy

# process the observation screenshot into 80 * 80 gray scale image
def process_observation(observation):
    observation = cv2.imread(observation)
    observation = cv2.cvtColor(cv2.resize(observation, (80, 80)), cv2.COLOR_BGR2GRAY)
    ret, observation = cv2.threshold(observation,1,255,cv2.THRESH_BINARY)
    print(observation)
    return np.reshape(observation,(80,80,1))

def play_flappy_birds():
    game = flappy.Flappy()
    actions = [0,1]
    

class Flappy_DQN():
    def __init__(self):
        pass 

if __name__ == "__main__":
    process_observation("/training_observations/1.png")