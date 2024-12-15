from random import random
import json

class Strategy:
    def __init__(self) -> None:
        # Setting basic Q-Learning
        self.load_Q()

    def get_best_guess(self, state):
        return int(max(self.Q[state], key=self.Q[state].get))

    def get_state(self, relative_distance, steps_count):
        step_group = 0 if steps_count <= 1 else 1 if steps_count <= 15 else 2
        state = 3 * relative_distance + step_group
        return str(state)

    def load_Q(self):
        self.Q = json.load(open("Strategy.json", "r"))