import marlo
from marlo import commands
import numpy as np
import json
import sys
import random
import time
import MalmoPython

class CliffWalking:
    def __init__(self):
        client_pool = [('127.0.0.1', 10000)]

        join_tokens = marlo.make('MarLo-CliffWalking-v0',
                                  params={
                                    "client_pool": client_pool,
                                    "comp_all_commands": ["movenorth", "movesouth", "moveeast", "movewest"],
                                    "prioritise_offscreen_rendering":False
                                  })

        join_token = join_tokens[0]

        self.env = marlo.init(join_token)
        self.env.params.suppress_info = False
        self.env.mission_spec.setViewpoint(1)
        for z in range(0,13,1):
            x = 2
            self.env.mission_spec.drawBlock( x,45,z,"lava")

        # command_parser = commands.CommandParser()
        # self.commands = command_parser.get_commands(self.env.params.mission_xml.encode('ascii'), self.env.params.role)
        # self.commands_size = len(self.commands)
        for _space, _commands in zip(self.env.action_spaces, self.env.action_names):
            self.commands = _commands
            self.commands_size = len(_commands) - 1
            print(self.commands)

        self.previousState = None
        self.alpha = 0.1
        self.gamma = 1.0
        self.epsilon = 0.1
        self.q_table = {}
        self.test = 0

    def take_action(self, currentState):
        if random.uniform(0, 1) < self.epsilon:
            action = random.randint(1, self.commands_size - 1)
            # if self.test == 0:
            #     action = 4
            # else:
            #     action = 1
        else:
            action = self.get_action(currentState)
        # print("take action : ", action)
        return action

    def get_action(self, currentState):
        actions = []
        m = max(self.q_table[currentState])
        for action in range(0, self.commands_size):
            if self.q_table[currentState][action] == m:
                actions.append(action)
        return (random.choice(actions) + 1)

    def act(self, currentState, currentReward):
        action = self.take_action(currentState)
        print("Je vais à {}".format(self.commands[action - 1]))
        obs, reward, done, info = self.env.step(action)
        # self.env.send_command(self.commands[action])
        self.previousState = currentState
        self.prevousAction = action - 1

    def run(self):
        totalReward = 0
        currentReward = 0
        obs, reward, done, info = self.env.step(0)
        while info["is_mission_running"]:
            currentState = "{}:{}".format(info["observation"]["XPos"], info["observation"]["ZPos"])
            currentReward = -1 if currentReward == 0 else currentReward
            # while (currentState == self.previousState):
            #         print("haha")
            #         obs, currentReward, done, info = self.env.step(0)
            #         currentState = "{}:{}".format(info["observation"]["XPos"], info["observation"]["ZPos"])
            if not currentState in self.q_table:
                self.q_table[currentState] = ([0.0] * self.commands_size)
            if self.previousState :
                old_q_action = self.q_table[self.previousState][self.prevousAction]
                # print("previous state : {}\nCurrent state : {}".format(self.previousState, currentState))
                # print("old q : ", old_q_action)
                # print("alpha : ", self.alpha)
                # print("reward : ", currentReward)
                # print("gamme : ", self.gamma)
                # print("q_table[{}] : {}".format(currentState, self.q_table[currentState]))
                # print("max : ", max(self.q_table[currentState]))
                self.q_table[self.previousState][self.prevousAction] = old_q_action + self.alpha * \
                 (currentReward + self.gamma * max(self.q_table[currentState]) - old_q_action)
                print(self.q_table)
            self.act(currentState, currentReward)
            # return
            # self.test = 1 if self.test == 0 else 0
            time.sleep(0.2)
            obs, currentReward, done, info = self.env.step(0)
            totalReward = currentReward
        if self.previousState:
            old_q_action = self.q_table[self.previousState][self.prevousAction]
            self.q_table[self.previousState][self.prevousAction] = old_q_action + self.alpha * \
             (currentReward - old_q_action)
        return totalReward

    def wait_mission_running(self):
        while not self.env._get_world_state().is_mission_running:
            time.sleep(.100)

    def reset(self):
        self.previousState = None
        self.prevousAction = None
        self.env.agent_host.startMission(
            self.env.mission_spec,
            self.env.mission_record_spec
        )
        # print("exp : ", self.env.experiment_id)
        # self.env.agent_host.startMission(
        #     self.env.mission_spec,
        #     self.env.client_pool,
        #     self.env.mission_record_spec,
        #     self.env.params.role,
        #     self.env.experiment_id
        # )
        # logger.info("Waiting for mission to start...")
        # world_state = self.agent_host.getWorldState()

if __name__ == '__main__':
    q_table = {}
    num_repeat = 1000
    cliff = CliffWalking()

    # cliff.reset()
    # cliff.wait_mission_running()
    # obs, reward, done, info = cliff.env.step(1)
    # obs, reward, done, info = cliff.env.step(0)
    # print(reward)
    # cliff.env.step(3)
    # cliff.env.step(3)
    # cliff.env.step(3)
    # cliff.env.step(3)
    # cliff.env.step(3)
    # cliff.env.step(3)
    # cliff.env.step(3)
    # cliff.env.step(3)
    # cliff.env.step(3)
    # cliff.env.step(3)
    # obs, reward, done, info = cliff.env.step(3)
    # print(reward)
    # obs, reward, done, info = cliff.env.step(2)
    # print(reward)
    # obs, reward, done, info = cliff.env.step(0)
    # print(info)

    for i in range(0, num_repeat):
        print("Mission ", i + 1, " : ")
        cliff.reset()
        cliff.wait_mission_running()
        print("je suis là")
        reward = cliff.run()

        # print("reward : ", reward)

        time.sleep(1)
