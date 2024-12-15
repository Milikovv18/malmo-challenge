from common import ENV_AGENT_NAMES, ENV_ACTIONS, ENV_TARGET_NAMES
from strategy import Strategy
from agent import BaseAgent
from random import random
import numpy as np
import json


class CustomAgent(BaseAgent):
    """Pig Chase agent - uses Tabular Q-Learning."""

    def __init__(self, name, visualizer=None):
        nb_actions = len(ENV_ACTIONS)
        super().__init__(name, nb_actions, visualizer = visualizer)

        self.fitness = 0
        self.avg_guess = 1
        self.last_move = 0
        self.catchable = 0
        self.pruned_move = None

        self.strategy = Strategy()

        # This agent is only for testing purposes
        self.load()
    
    def sign(self, value):
        if value < 0: return -1
        elif value > 0: return +1
        else: return 0
    
    def generate_state(self, state):
        # Surface and entities
        surface = state[0]
        agent = [agent for agent in state[1] if agent['name'] == self.name][0]
        partner = [agent for agent in state[1] if agent['name'] != self.name][0]
        pig = [pig for pig in state[1] if pig['name'] == ENV_TARGET_NAMES[0]][0]

        # Pig coordinates on a surface
        xP = round(pig['z']-0.5)
        zP = round(pig['x']-0.5)

        # Checking if pig is catchable
        self.catchable =\
            int(surface[xP-1, zP].startswith("sand") or xP < 2) +\
            int(surface[xP+1, zP].startswith("sand") or xP > 9) +\
            int(surface[xP, zP-1].startswith("sand") or zP < 2) +\
            int(surface[xP, zP+1].startswith("sand") or zP > 9)
        
        # Evaluating partner strategy before moving agent
        avg_guess = self.evaluate_strategy(partner, pig)
        binary_guess = round(avg_guess)

        # Choosing appropriate target based on estimated partner strategy (lapis or pig)
        target = [{'x' : 10, 'z' : 1}, pig][binary_guess]
        self.catchable = [4, self.catchable][binary_guess]

        # Agent coordinates on a surface
        xA = round(agent['z']-0.5)
        zA = round(agent['x']-0.5)

        # Checking if there is lapis block nearby
        self.pruned_move =\
            1 * surface[xA-1, zA].startswith("lapis") +\
            3 * surface[xA+1, zA].startswith("lapis") +\
            4 * surface[xA, zA-1].startswith("lapis") +\
            2 * surface[xA, zA+1].startswith("lapis")
        if self.pruned_move == 0 or target != pig:
            self.pruned_move = None
        else:
            self.pruned_move -= 1

        # Obstacles observation
        food_related = 3*self.sign(target['z']-agent['z']) + self.sign(target['x']-agent['x'])

        obstacles = []
        for a in range(-1, 2):
            for b in range(-1, 2):
                obstacles.append(int(surface[xA+a][zA+b].startswith("sand")) if 0 < xA+a < 11 and 0 < zA+b < 11 else 0)

        # Upper, right, bottom and left observations sorted by 'bits' in obstacle_comb
        obstacle_comb = (obstacles[3] << 3) + (obstacles[1] << 2) + (obstacles[5] << 1) + obstacles[7]
        return str(4 * (15*food_related + obstacle_comb) + self.last_move)

    def act(self, new_state, reward, done):
        if done:
            print("Resetting level parameters")
            self.pruned_move = None
            self.catchable = 0
            self.last_move = 0
            self.avg_guess = 1
            self.fitness = 0

        state = self.generate_state(new_state)
        if self.catchable < 2:
            return 4 # Stay in place
        self.fitness += 1
        move = self.get_best_move(state)
        self.last_move = move
        return move
    
    def get_best_move(self, state):
        actions = self.Q[state].copy()
        if self.pruned_move != None:
            actions.pop(str(self.pruned_move))
        return int(max(actions, key=actions.get))
    
    def evaluate_strategy(self, agent_pos, food_pos):
        # Updating Bayes inference
        dist_to_food = int(abs(agent_pos['x']-food_pos['x']) + abs(agent_pos['z']-food_pos['z']))
        if self.fitness > 3:
            strat_state = self.strategy.get_state(dist_to_food, self.fitness)
            strat_guess = self.strategy.get_best_guess(strat_state)
            self.avg_guess = 0.80 * self.avg_guess + 0.20 * strat_guess

        return self.avg_guess

    def load(self):
        self.Q = json.load(open("Agent.json", "r"))