import json
import random

class Brain():
    def __init__(self):
        self.learning_rate = 0.7 # learning rate of the brain
        self.GAMMA = 1.0 # discount of the brain
        self.reward = {"alive": 0,"die": -1000} # rewards for stay alive and die
        self.load_qvalues() # load Q_values from json file
        self.replay_memory = [] # replay memory of the brain
        self.last_state = "0_0_0_0" # initilize state 
        self.init_state(self.last_state) 
        self.cycle_count = 0 # game cycle count
        self.last_action = 0 # last action bird performed

    def load_qvalues(self):
        """ load Q values from json file
        """
        self.qvalues = {}
        try:
            fp = open("data/qvalues.json")
        except IOError:
            return
        self.qvalues = json.load(fp)
        fp.close()
        
    def get_state(self,x,y,vel,pipe):
        """ Calculate state of the game from given game settings
        
        Arguments:
            x {float} -- bird x coordinate
            y {float} -- bird y coordinate
            vel {float} -- velocity of the bird 
            lower_pipes {[pipe]} -- lower pipes in the game
        
        Returns:
            [string] -- "A_B_C_D"
            where:
            A -- diff(x,leftmost lower pipe x)
            B -- diff(y,leftmost lower pipe y)
            C -- velocity of the bird
            D -- diff(y, second lower pipe from the left's y)
        """

        pipe0 = pipe[0] # leftmost lower pipes
        pipe1 = pipe[1] # second lower pipes from the left

        # move the brain view to the next pipe if entering over 50px 
        if x - pipe[0][0] >= 50:
            pipe0 = pipe[1]
            if len(pipe) > 2:
                pipe1 = pipe[2]

        diff_x = pipe0[0] - x
        diff_y = pipe0[1] - y

        if -50 < diff_x <= 0:  
            y1 = pipe1[1] - y
        else:
            y1 = 0

        if diff_x < -40: 
            diff_x = int(diff_x)
        elif diff_x < 140:
            diff_x = int(diff_x) - (int(diff_x) % 10)
        else:
            diff_x = int(diff_x) - (int(diff_x) % 70)

        if -180 < diff_y < 180:
            diff_y = int(diff_y) - (int(diff_y) % 10)
        else:
            diff_y = int(diff_y) - (int(diff_y) % 60)

        if -180 < y1 < 180:
            y1 = int(y1) - (int(y1) % 10)
        else:
            y1 = int(y1) - (int(y1) % 60)

        state = str(int(diff_x)) + "_" + str(int(diff_y)) + "_" + str(int(vel)) + "_" + str(int(y1))
        self.init_state(state)
        return state
    
    def init_state(self,state):
        if self.qvalues.get(state) == None:
            self.qvalues[state] = [0,0,0]
            num = len(self.qvalues.keys())
            if num > 20000 and num % 1000 == 0:
                print("======== Total state: {} ========".format(num))
            if num > 30000:
                print("======== New state: {0:14s}, Total: {1} ========".format(state, num))


    def act(self,x,y,vel,lower_pipes): 
        """ act based on the information passed from game
        
        Arguments:
            x {float} -- bird x coordinate
            y {float} -- bird y coordinate
            vel {float} -- velocity of the bird 
            lower_pipes {[pipe]} -- lower pipes in the game
        
        Returns:
            [int] -- 1 if flap, 0 if do nothing
        """
        state = self.get_state(x,y,vel,lower_pipes)
        self.replay_memory.append((self.last_state,self.last_action,state))

        self.save_qvalue()

        if self.qvalues[state][0] >= self.qvalues[state][1]: action = 0
        else: action = 1

        self.last_state = state 
        self.last_action = action

        return action
    
    def save_qvalue(self):
        if len(self.replay_memory) > 6000000:
            history = list(reversed(self.replay_memory[:5000000]))
            for replay in history:
                curr_state, action, next_state = replay
                self.qvalues[curr_state][action] = (1-self.learning_rate) * self.qvalues[curr_state][action] + \
                                       self.learning_rate * (self.reward['alive'] + self.GAMMA*max(self.qvalues[next_state][0:2]) )
                self.qvalues[curr_state][action] = round(self.qvalues[curr_state][action],5)
            self.replay_memory = self.replay_memory[5_000_000:]
    
    def terminate_game(self):
        replay_history = list(reversed(self.replay_memory))
        for replay in replay_history:
            curr_state, action, next_state = replay
            self.qvalues[curr_state][action] = (1-self.learning_rate) * self.qvalues[curr_state][action] + self.learning_rate * (self.reward["alive"] + self.GAMMA*max(self.qvalues[next_state][0:2]))
            self.qvalues[curr_state][action] = round(self.qvalues[curr_state][action],5)

        self.last_state = "0_0_0_0" # initial position, MUST NOT be one of any other possible state
        self.last_action = 0
        self.moves = []
        self.cycle_count += 1

    # this function only get called when the game terminates
    def update_score(self,score):
        replay_history = list(reversed(self.replay_memory))
        
        if int(replay_history[0][2].split("_")[1]) >= 120: upper_death = True
        else: upper_death = False

        if int(replay_history[0][2].split("_")[1]) <= -180 and int(replay_history[0][2].split("_")[0]) <= 20: lower_death = True
        else: lower_death = False

        step = 0
        for replay in replay_history:
            step += 1
            curr_state, action, next_state = replay
            self.qvalues[curr_state][2] += 1
            if step <= 2:
                curr_reward = self.reward["die"]
            elif upper_death and action:
                curr_reward = self.reward["die"]
                upper_death = False
            elif lower_death:
                curr_reward = self.reward["die"]
                lower_death = False
            else:
                curr_reward = self.reward["alive"]
            
            self.qvalues[curr_state][action] = (1-self.learning_rate) * self.qvalues[curr_state][action] + self.learning_rate * (curr_reward + self.GAMMA*max(self.qvalues[next_state][0:2]))
            self.qvalues[curr_state][action] = round(self.qvalues[curr_state][action],5)
            

        self.replay_memory = []
        self.cycle_count += 1

    def dump_qvalues(self):
        """
        Dump the qvalues to the JSON file
        """
        print("******** Saving Q-table(%d keys) to local file... ********" % len(self.qvalues.keys()))
        fp = open("data/qvalues.json", "w")
        json.dump(self.qvalues, fp)
        fp.close()
        print("******** Q-table(%d keys) updated on local file ********" % len(self.qvalues.keys()))


        
