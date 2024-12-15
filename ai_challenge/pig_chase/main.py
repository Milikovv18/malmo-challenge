# Copyright (c) 2017 Microsoft Corporation.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
#  TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ===================================================================================================================

import os
import sys

from threading import Thread, active_count
from time import sleep

from malmo import minecraftbootstrap
from malmopy.visualization import ConsoleVisualizer

from common import parse_clients_args, ENV_AGENT_NAMES, ENV_TARGET_NAMES
from agent import get_agent_type, RandomAgent
from environment import PigChaseEnvironment, PigChaseSymbolicStateBuilder

from custom_agent import CustomAgent

# Enforce path
sys.path.insert(0, os.getcwd())
sys.path.insert(1, os.path.join(os.path.pardir, os.getcwd()))


def agent_factory(name, role, clients):
    assert len(clients) >= 2, 'Not enough clients (need at least 2)'
    clients = parse_clients_args(clients)

    builder = PigChaseSymbolicStateBuilder()
    env = PigChaseEnvironment(clients, builder, role=role,
                              randomize_positions=True)

    if role != 0:
        agent = CustomAgent(name)
    else:
        agent = RandomAgent(name, 5)
    obs = env.reset(get_agent_type(agent))

    reward = 0
    agent_done = False

    while True:
        if env.done:
            while True:
                obs = env.reset(get_agent_type(agent))
                if obs:
                    break

        # select an action
        action = agent.act(obs, reward, agent_done)

        # reset if needed
        if env.done:
            obs = env.reset(get_agent_type(agent))

        # take a step
        obs, reward, agent_done = env.do(action)


def run_experiment(agents_def):
    assert len(agents_def) == 2, 'Not enough agents (required: 2, got: %d)'\
                % len(agents_def)

    processes = []
    for agent in agents_def:
        p = Thread(target=agent_factory, kwargs=agent)
        p.daemon = True
        p.start()

        # Give the server time to start
        if agent['role'] == 0:
            sleep(1)

        processes.append(p)

    try:
        # wait until only the challenge agent is left
        while active_count() > 2:
            sleep(0.1)
    except KeyboardInterrupt:
        print('Caught control-c - shutting down.')


if __name__ == '__main__':
    # Launch 2 Minecraft instances if needed (both reusable)
    minecraftbootstrap.launch_minecraft([10000, 10001])

    visualizer = ConsoleVisualizer()
    agents = [{'name': agent, 'role': role, 'clients': ['127.0.0.1:10000', '127.0.0.1:10001']}
              for role, agent in enumerate(ENV_AGENT_NAMES)]

    run_experiment(agents)