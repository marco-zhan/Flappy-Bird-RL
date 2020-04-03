import json
import random

class Brain():
    def __init__(self):
        self.learning_rate = 0.7
        self.GAMMA = 1.0
        self.reward = {"alive": 0,"die": -1000}
        self.load_qvalues()
        self.replay_memory = []
        self.last_state = "0_0_0_0"
        self.init_state(self.last_state)
        self.cycle_count = 0
        self.last_action = 0

    def load_qvalues(self):
        self.qvalues = {}
        try:
            fp = open("data/qvalues.json")
        except IOError:
            return
        self.qvalues = json.load(fp)
        fp.close()
        
    def get_state(self,x,y,vel,pipe):
        pipe0 = pipe[0]
        pipe1 = pipe[1]
        if x - pipe[0][0] >= 50:
            pipe0 = pipe[1]
            if len(pipe) > 2:
                pipe1 = pipe[2]

        x0 = pipe0[0] - x
        y0 = pipe0[1] - y
        if -50 < x0 <= 0:  
            y1 = pipe1[1] - y
        else:
            y1 = 0

        if x0 < -40:
            x0 = int(x0)
        elif x0 < 140:
            x0 = int(x0) - (int(x0) % 10)
        else:
            x0 = int(x0) - (int(x0) % 70)

        if -180 < y0 < 180:
            y0 = int(y0) - (int(y0) % 10)
        else:
            y0 = int(y0) - (int(y0) % 60)

        #x1 = int(x1) - (int(x1) % 10)
        if -180 < y1 < 180:
            y1 = int(y1) - (int(y1) % 10)
        else:
            y1 = int(y1) - (int(y1) % 60)

        state = str(int(x0)) + "_" + str(int(y0)) + "_" + str(int(vel)) + "_" + str(int(y1))
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
        """ Choose the best action based on the current state
        
        Arguments:
            x {[type]} -- [description]
            y {[type]} -- [description]
            vel {[type]} -- [description]
            pipe {[type]} -- [description]
        
        Returns:
            [Bool] -- [Which action to do, "flap" if True, "do nothing" if false]
        """
        state = self.get_state(x,y,vel,lower_pipes)
        self.replay_memory.append([self.last_state,self.last_action,state])

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
            self.replay_memory = self.replay_memory[5_000_000:]
    
    # this function only get called when the game terminates
    def update_score(self,score):
        replay_history = list(reversed(self.replay_memory))

        step = 0
        for replay in replay_history:
            step += 1
            curr_state, action, next_state = replay
            self.qvalues[curr_state][2] += 1
            if step <= 2:
                curr_reward = self.reward["die"]
            else:
                curr_reward = self.reward["alive"]
            
            self.qvalues[curr_state][action] = (1-self.learning_rate) * self.qvalues[curr_state][action] + \
                                                self.learning_rate * (curr_reward + self.GAMMA*max(self.qvalues[next_state][0:2]))
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


        
