import tensorflow as tf
import cv2
import numpy as np 
import random
from collections import deque
import wrapped_flappy as game 

FRAME_PER_ACTION = 1
NUM_VALID_ACTIONS = 2
GAMMA = 0.95
OBSERVE = 3000
EXPLORE = 600000
INITIAL_EPSILON = 0.1
FINAL_EPSILON = 0.0001
REPLAY_MEMORY = 20000
BATCH_SIZE = 32
UPDATE_TIME = 1000

tf.compat.v1.disable_eager_execution()

# process the observation screenshot into 80 * 80 gray scale image
def process_observation(observation):
    observation = cv2.cvtColor(cv2.resize(observation, (80, 80)), cv2.COLOR_BGR2GRAY)
    ret, observation = cv2.threshold(observation,1,255,cv2.THRESH_BINARY)
    return np.reshape(observation,(80,80,1))

def play_flappy_birds():
    flappy = game.GameState()
    action = np.array([1,0])

    observation, reward, terminated = flappy.frame_step(action)
    observation = cv2.cvtColor(cv2.resize(observation, (80, 80)), cv2.COLOR_BGR2GRAY)
    ret, observation = cv2.threshold(observation,1,255,cv2.THRESH_BINARY)
    
    # initialize DQN with the initial observation
    dqn = Flappy_DQN(observation)

    while True:
        action = dqn.get_action()
        next_observation, reward, terminated = flappy.frame_step(action)
        next_observation = process_observation(next_observation)
        dqn.update_perception(action,next_observation,reward,terminated)

class Flappy_DQN():
    def __init__(self,observation):
        # stack to create a (80,80,4) initial state
        self.state = np.stack((observation,observation,observation,observation),axis=2)
        # initialize replay memory
        self.replay_memory = deque()
        self.time_steps = 0
        self.epsilon = INITIAL_EPSILON

        self.state_input, self.Q_value,self.weight_conv1,self.bias_conv1,self.weight_conv2,self.bias_conv2,self.weight_conv3,self.bias_conv3,self.weight_dense1,self.bias_dense1,self.weight_dense2,self.bias_dense2 = self.create_DQN_network()
        self.state_input_t, self.Q_value_t,self.weight_conv1_t,self.bias_conv1_t,self.weight_conv2_t,self.bias_conv2_t,self.weight_conv3_t,self.bias_conv3_t,self.weight_dense1_t,self.bias_dense1_t,self.weight_dense2_t,self.bias_dense2_t = self.create_DQN_network()
        
        self.copy_target_Q_network_operation = [self.weight_conv1_t.assign(self.weight_conv1),self.bias_conv1_t.assign(self.bias_conv1),self.weight_conv2_t.assign(self.weight_conv2),self.bias_conv2_t.assign(self.bias_conv2),self.weight_conv3_t.assign(self.weight_conv3),self.bias_conv3_t.assign(self.bias_conv3),self.weight_dense1_t.assign(self.weight_dense1),self.bias_dense1_t.assign(self.bias_dense1),self.weight_dense2_t.assign(self.weight_dense2),self.bias_dense2_t.assign(self.bias_dense2)]
        self.create_training_params()

        # saving and loading networks
        self.saver = tf.compat.v1.train.Saver()
        self.session = tf.compat.v1.InteractiveSession()
        self.session.run(tf.compat.v1.initialize_all_variables())

        checkpoint = tf.train.get_checkpoint_state("saved_networks")
        if checkpoint and checkpoint.model_checkpoint_path:
                self.saver.restore(self.session, checkpoint.model_checkpoint_path)
                print ("Successfully loaded:", checkpoint.model_checkpoint_path)
        else:
                print ("Could not find old network weights")

    def create_DQN_network(self):
        # initialize weight and bias for conv layers
        weight_conv1 = self.weight_variable([8,8,4,32])
        bias_conv1 = self.bias_variable([32])

        weight_conv2 = self.weight_variable([4,4,32,64])
        bias_conv2 = self.bias_variable([64])

        weight_conv3 = self.weight_variable([3,3,64,64])
        bias_conv3 = self.bias_variable([64])

        weight_dense1 = self.weight_variable([1600,512])
        bias_dense1 = self.bias_variable([512])

        weight_dense2 = self.weight_variable([512,NUM_VALID_ACTIONS])
        bias_dense2 = self.bias_variable([NUM_VALID_ACTIONS])

        # create input layer
        state_input = tf.compat.v1.placeholder("float",[None,80,80,4])

        # create hidden layers
        hidden_conv1 = tf.nn.relu(self.conv2d(state_input,weight_conv1,4) + bias_conv1)
        hidden_maxpool1 = self.max_pool_2d(hidden_conv1)

        hidden_conv2 = tf.nn.relu(self.conv2d(hidden_maxpool1,weight_conv2,2) + bias_conv2)

        hidden_conv3 = tf.nn.relu(self.conv2d(hidden_conv2,weight_conv3,1) + bias_conv3)

        hidden_flat = tf.reshape(hidden_conv3, [-1, 1600])

        hidden_dense1 = tf.nn.relu(tf.matmul(hidden_flat, weight_dense1) + bias_dense1)

        # Q_value layer
        Q_value = tf.matmul(hidden_dense1, weight_dense2) + bias_dense2

        return state_input,Q_value,weight_conv1,bias_conv1,weight_conv2,bias_conv2,weight_conv3,bias_conv3,weight_dense1,bias_dense1,weight_dense2,bias_dense2
    
    def copy_target_Q_network(self):
        self.session.run(self.copy_target_Q_network_operation)

    def create_training_params(self):
        self.a = tf.compat.v1.placeholder("float",[None,NUM_VALID_ACTIONS])
        self.y = tf.compat.v1.placeholder("float",[None])
        Q_action = tf.compat.v1.reduce_sum(tf.multiply(self.Q_value, self.a), reduction_indices = 1)
        self.cost = tf.reduce_mean(tf.square(self.y - Q_action))
        self.train_step = tf.compat.v1.train.AdamOptimizer(1e-6).minimize(self.cost)

    def train_network(self):
        # get a random batch from replay memory
        batch = random.sample(self.replay_memory,BATCH_SIZE)

        state_batch = [data[0] for data in batch]
        action_batch = [data[1] for data in batch]
        reward_batch = [data[2] for data in batch]
        next_state_batch = [data[3] for data in batch]
    

        # set y value
        y_batch = []
        Q_value_batch = self.Q_value_t.eval(feed_dict={self.state_input_t:next_state_batch})

        for i in range(BATCH_SIZE):
            terminated = batch[i][4]
            if terminated:
                y_batch.append(reward_batch[i])
            else:
                y_batch.append(reward_batch[i] + GAMMA * np.max(Q_value_batch[i]))
        
        self.train_step.run(feed_dict={
                            self.y: y_batch,
                            self.a: action_batch,
                            self.state_input: state_batch
                            })

        # save network every 100000 iteration
        if self.time_steps % 10000 == 0:
            self.saver.save(self.session, 'saved_networks/' + 'network' + '-dqn', global_step = self.time_steps)

        if self.time_steps % UPDATE_TIME == 0:
            self.copy_target_Q_network()

        
    def get_action(self):
        Q_value = self.Q_value.eval(feed_dict= {self.state_input:[self.state]})[0]
        action = np.zeros(NUM_VALID_ACTIONS)
        action_index = 0

        if self.time_steps % FRAME_PER_ACTION == 0:
            if random.random() <= self.epsilon:
                print("----Random Action----")
                action_index = random.randrange(NUM_VALID_ACTIONS)
                action[action_index] = 1
            else:
                action_index = np.argmax(Q_value)
                action[action_index] = 1
        else: 
            action[0] = 1

        if self.epsilon > FINAL_EPSILON and self.time_steps > OBSERVE:
            self.epsilon -= (INITIAL_EPSILON - FINAL_EPSILON) / EXPLORE

        return action 

    def update_perception(self,action,observation,reward,terminated):
        # generate the new state
        new_state = np.append(self.state[:,:,1:],observation,axis = 2)
        # store state s_t action a_t reward r_t and new state s_(t+1) into memory
        self.replay_memory.append([self.state,action,reward,new_state,terminated])

        # if memory grows out of the customized bound
        if len(self.replay_memory) > REPLAY_MEMORY:
            self.replay_memory.popleft

        if self.time_steps > OBSERVE:
            self.train_network()
        
        self.state = new_state

        # print training information
        state = ""
        if self.time_steps <= OBSERVE:
            state = "observe"
        elif self.time_steps > OBSERVE and self.time_steps < OBSERVE + EXPLORE:
            state = "explore"
        else:
            state = "train"
        
        print("TIMESTEP [{}] STATE [{}] ACTION [{}] ESPILON [{}] REWARD [{}]".format(self.time_steps,state,action,self.epsilon, reward))
        self.time_steps += 1

    # random generate a weight variable
    def weight_variable(self,shape):
        initial = tf.random.truncated_normal(shape, stddev = 0.01)
        return tf.Variable(initial)
    
    # create bias variable with shape
    def bias_variable(self,shape):
        initial = tf.constant(0.01, shape = shape)
        return tf.Variable(initial)

    # create conv2d with weight variable W and stride
    def conv2d(self,input, filters, stride):
        return tf.nn.conv2d(input=input,filters=filters,strides = [1, stride, stride, 1], padding = "SAME")
    
    def max_pool_2d(self,input):
        return tf.nn.max_pool(input=input, ksize = [1, 2, 2, 1], strides = [1, 2, 2, 1], padding = "SAME")
    

if __name__ == "__main__":
    play_flappy_birds()