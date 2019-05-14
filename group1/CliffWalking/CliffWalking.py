import marlo
from marlo import commands
import numpy as np
import json
import sys
import random
import time

class CliffWalking:

    def __init__(self):
        client_pool = [('127.0.0.1', 10000)]

        join_tokens = marlo.make('MarLo-CliffWalking-v0',
                                  params={
                                    "client_pool": client_pool
                                  })

        join_token = join_tokens[0]

        self.env = marlo.init(join_token)
        self.env.params.suppress_info = False
        # command_parser = commands.CommandParser()
        # self.commands = command_parser.get_commands(self.env.params.mission_xml.encode('ascii'), self.env.params.role)
        # self.commands_size = len(self.commands)
        for _space, _commands in zip(self.env.action_spaces, self.env.action_names):
            self.commands = _commands
            self.commands_size = len(_commands) - 1
        self.previousState = None
        self.alpha = 0.1
        self.gamma = 1

    def take_action(self, currentState, q_table, eps):
        if random.uniform(0, 1) < eps:
            action = random.randint(0, self.commands_size)
        else:
            action = self.get_action(q_table, currentState)
        print("take action : ", action)
        return action

    def get_action(self, q_table, currentState):
        actions = []
        max = self.get_high_value(q_table, currentState)
        for action in range(0, self.commands_size):
            if q_table[currentState, action] == max:
                actions.append(action)
        return random.choice(actions)

    def get_high_value(self, q_table, currentState):
        value = -sys.maxsize - 1
        for i in range(0, self.commands_size):
            if q_table[currentState, i] > value:
                value = q_table[currentState, i]
        return value

    def act(self, currentState, q_table, currentReward):
        if self.previousState :
            old_q_action = q_table[self.previousState, self.prevousAction]
            q_table[self.previousState, self.prevousAction] = old_q_action + self.alpha * \
             (currentReward + self.gamma * self.get_high_value(q_table, currentState) - old_q_action)
        action = self.take_action(currentState, q_table, 0.1)
        obs, reward, done, info = self.env.step(action)
        self.previousState = currentState
        self.prevousAction = action
        return reward

    def run(self, q_table):
        totalReward = 0
        currentReward = 0
        while self.env._get_world_state().is_mission_running:
            info = self.env._get_observation(self.env._get_world_state())
            currentState = "{}:{}".format(info["YPos"], info["ZPos"])
            if not (currentState, 0) in q_table:
                print("size :", self.commands_size)
                for i in range(0, self.commands_size):
                    q_table[currentState, i] = 0.0
            currentReward = self.act(currentState, q_table, currentReward)
            totalReward += currentReward
            time.sleep(0.5)
        return totalReward

    def wait_mission_running(self):
        while not self.env._get_world_state().is_mission_running:
            time.sleep(.100)

    def reset(self):
        self.env.reset()
if __name__ == '__main__':
    q_table = {}
    num_repeat = 1000
    cliff = CliffWalking()
    for i in range(0, num_repeat):
        cliff.reset()
        cliff.wait_mission_running()
        cliff.run(q_table)
        print(q_table)
    # print(q_table)
    # print(CliffWalking.run)
