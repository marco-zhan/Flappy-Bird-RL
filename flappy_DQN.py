import tensorflow as tf
import cv2
import numpy as np 
import random
import flappy

# process the observation screenshot into 80 * 80 gray scale image
def process_observation(observation):
    observation = cv2.cvtColor(cv2.resize(observation, (80, 80)), cv2.COLOR_BGR2GRAY)
    ret, observation = cv2.threshold(observation,1,255,cv2.THRESH_BINARY)
    return np.reshape(observation,(80,80,1))

def play_flappy_birds():
    game = flappy.Flappy()
    actions = numpy.array([1])

    observation, reward, terminated = game.frame_step(action)
    observation = cv2.cvtColor(cv2.resize(observation, (80, 80)), cv2.COLOR_BGR2GRAY)
    ret, observation = cv2.threshold(observation,1,255,cv2.THRESH_BINARY)
    
    # initialize DQN with the initial observation
    dqn = Flappy_DQN(observation)

    while True:
        action = dqn.get_action()
        observation, reward, terminated = game.frame_step(action)
        observation = process_observation(observation)
        dqn.set_perception(action,observation,reward,terminated)
    

class Flappy_DQN():
    def __init__(self):
        pass 
    
    def create_DQN_network(self):

    def get_action(self):
        pass 
    def set_perception(action,observation,reward,terminated):
        pass

if __name__ == "__main__":
    play_flappy_birds()