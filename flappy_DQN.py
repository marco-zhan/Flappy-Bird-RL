import tensorflow as tf
import cv2
import numpy as np 
import random
import flappy

NUM_VALID_ACTIONS = 2
GAMMA = 0.99
OBSERVE_BEFORE = 100000
EXPLORE = 2000000
INITIAL_EPSILON = 1.0
FINAL_EPSILON = 0.005
REPLAY_MEMORY = 50000
BATCH_SIZE = 32
UPDATE_TIME = 100


# process the observation screenshot into 80 * 80 gray scale image
def process_observation(observation):
    observation = cv2.cvtColor(cv2.resize(observation, (80, 80)), cv2.COLOR_BGR2GRAY)
    ret, observation = cv2.threshold(observation,1,255,cv2.THRESH_BINARY)
    return np.reshape(observation,(80,80,1))

def play_flappy_birds():
    game = flappy.Flappy()
    action = np.array([1])

    observation, reward, terminated = game.train_step(action)
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
    def __init__(self,observation):
        # stack to create a (80,80,4) state
        self.state = np.stack((observation,observation,observation,observation),axis=2)
    
    def create_DQN_network(self):
        # initialize weight and bias for conv layers
        weight_conv1 = self.weight_variable([8,8,4,32])
        bias_conv1 = self.bias_variable([32])

        weight_conv2 = self.weight_variable([4,4,32,64])
        bias_conv2 = self.bias_variable([64])

        weight_conv3 = self.weight_variable([3,3,64,64])
        bias_conv3 = self.bias_variable([64])

        # create input layer
        input_layer = tf.placeholder("float",[None,80,80,4])

        # create hidden layers
        hidden_conv1 = tf.nn.relu(self.conv2d(input_layer,weight_conv1,4) + bias_conv1)
        hidden_maxpool1 = self.max_pool_2d(hidden_conv1)

        hidden_conv2 = tf.nn.relu(self.conv2d(hidden_maxpool1,weight_conv2,2) + bias_conv2)
        hideen_maxpool2 = tf.nn.relu(hidden_conv2)

        hidden_conv3 = tf.nn.relu(self.conv2d(hideen_maxpool2,weight_conv3,1) + bias_conv3)
        

        


    def get_action(self):
        pass 

    def set_perception(self,action,observation,reward,terminated):
        pass
    
    # random generate a weight variable
    def weight_variable(self,shape):
        initial = tf.truncated_normal(shape, stddev = 0.01)
        return tf.Variable(initial)
    
    # create bias variable with shape
    def bias_variable(self,shape):
		initial = tf.constant(0.01, shape = shape)
		return tf.Variable(initial)

    # create conv2d with weight variable W and stride
    def conv2d(self,input, filter, stride):
		return tf.nn.conv2d(input=input,filter=filter,strides = [1, stride, stride, 1], padding = "SAME")
    
    def max_pool_2d(self,input):
		return tf.nn.max_pool(input=input, ksize = [1, 2, 2, 1], strides = [1, 2, 2, 1], padding = "SAME")
    

if __name__ == "__main__":
    play_flappy_birds()