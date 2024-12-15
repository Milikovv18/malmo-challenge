# 🤖 QLearning for malmo-challenge

<img src="https://github.com/user-attachments/assets/d24f4da6-06aa-43e6-b48c-33fc66fc3138" align="right" width=180/>

![Minecraft](https://img.shields.io/badge/Minecraft-green?logo=anycubic&logoColor=gray)
![AI](https://img.shields.io/badge/QLearning-orange?logo=tensorflow&logoColor=white)

This project, completed as a Bachelor's thesis, addresses a solution for the [Microsoft Malmo Collaborative AI Challenge](https://github.com/microsoft/malmo-challenge).

The research aims to develop collaborative strategies for AI agents to recognize the intentions of teammates and achieve shared goals.

The solution is divided into two stages: a simplified 2D simulation environment and adaptation to the complex 3D game environment of Minecraft.

---

## 🌐 Simplified 2D Simulation

### Overview
The 2D simulation simplifies the problem by discretizing the environment into a grid-based layout. The agents navigate this grid to achieve specific objectives while avoiding obstacles. This step aims to efficiently train and test fundamental behaviors before transitioning to the more complex 3D environment.
Code for this stage can be found in [QLearning2D](QLearning2D) directory.

### Environment Representation

<p align="center">
  <img src="https://github.com/user-attachments/assets/9e540171-c6e4-4379-9625-77b31adbb0fe" />
</p>

- **Grid Layout**: The environment is a 10x10 grid with obstacles, agents, and a movable target.
- **Actions**: The agents can move up, down, left, or right, constrained by obstacles and grid boundaries.

### Methodology
The core algorithm for training is Q-Learning, which updates the agent's knowledge through reward-based interactions with the environment. The Q-table captures the expected utility of actions for each state, which is updated using the Bellman equation:

$$ Q(s, a) \leftarrow Q(s, a) + \alpha \left[ r + \gamma \max_a Q(s', a) - Q(s, a) \right] $$

Where:
- $\ Q(s, a) $: The current value of state-action pair
- $\ \alpha $: Learning rate
- $\ \gamma $: Discount factor
- $\ r $: Immediate reward
- $\ s' $: Next state

### Results
1. **Behavior Demonstration**:

| ![Collaborative](https://github.com/user-attachments/assets/bf6dd7fe-46bb-45dd-bc33-937226779a97) | ![Random](https://github.com/user-attachments/assets/dd1a052c-c1c1-4c2b-8335-50e5458c2f10) | 
|:--:| :--: | 
| *Collaborative behavior* | *Random behavior* |


2. **Metrics**:

   - **Average Distance between agents and the goal** (orange - random behavior, blue - collaborative behavior):

      <p align="left">
        <img src="https://github.com/user-attachments/assets/4fc5cad4-0a2c-49e2-a073-5258ba8cf002" width="500"/>
      </p>

   - **Game Outcomes**: Average game score for every step number:

      <p align="left">
        <img src="https://github.com/user-attachments/assets/825c2f8b-6372-4e1d-bc4e-6e5c4cab94b9" width="500"/>
      </p>

4. **Cycle Detection**:
   Fourier analysis was used to identify cyclic behaviors, helping optimize agent policies:

      <p align="left">
        <img src="https://github.com/user-attachments/assets/fcd2e712-6ae8-4da6-aa6a-0c5ac95572ad" width="500"/>
      </p>

---

## 🌎 Adaptation to the Minecraft Environment

### Overview
The 3D environment introduces a dynamic, continuous space with additional challenges, such as real-time movements and collisions. The target application is the "Pig Chase" mini-game, where agents collaborate to capture a pig while navigating obstacles.

### Environment Representation
- **Game Features**:
  - Agents interact in real-time.
  - Obstacles and boundaries create a sparse maze.
  - Goals and obstacles are dynamically positioned.

### Methodology
Adapting the trained 2D models required enhancing the Q-learning framework to accommodate:
- Continuous state space representation.
- Real-time interaction with Minecraft's physics and object constraints.

The agent's decision-making process relies on a modified version of the Q-table that accounts for:
- Distance to the target.
- Interaction with dynamic obstacles.
- Recognition of teammate behavior.

### Results
1. **Behavior Demonstration in 3D**:

<p align="center">
  <img src="https://github.com/user-attachments/assets/3a687f4e-eed9-4f6a-97d6-088ea758779e" width="500"/>
</p>

2. **Success Rates**:
The collaborative strategies from the 2D environment achieved an approximate 90% accuracy in recognizing teammate intentions and completing tasks.

### Challenges
- **Collision Handling**: Modifications to the Minecraft environment were required to disable collisions, improving agent pathfinding in dynamic setups.
- **Dynamic Obstacles**: Agents adapted well but showed minor inefficiencies in complex scenarios, which can be improved with further refinements.

---

## Conclusion
This project demonstrates the effectiveness of combining simplified environments for initial training with adaptations for more complex, realistic setups. The achieved models provide a robust foundation for multiagent collaboration with minimal communication.

---

## References
- [John McCarthy. What is artificial intelligence? (2007)](https://www-formal.stanford.edu/jmc/whatisai.pdf)
- [Mark Stefik. Roots and Requirements for Collaborative AI (2023)](https://arxiv.org/ftp/arxiv/papers/2303/2303.12040.pdf)
- [Jason Lee. Teaching a computer how to play Snake with Q-Learning (2020)](https://towardsdatascience.com/teaching-a-computer-how-to-play-snake-with-q-learning-93d0a316ddc0)
- [Alex Maszański. Reinforcement Learning explained with simple examples (2021)](https://proglib.io/p/chto-takoe-obuchenie-s-podkrepleniem-i-kak-ono-rabotaet-obyasnyaem-na-prostyh-primerah)
- [Adrià Garriga-Alonso. The Malmo Collaborative AI Challenge (2017)](https://github.com/rhaps0dy/malmo-challenge)
- [Florin Gogianu. Malmo Challenge Overview (2017)](https://github.com/village-people/flying-pig)
- [James Allen, George Ferguson. Human-machine collaborative planning (2020)](https://www.researchgate.net/publication/228911168_Human-machine_collaborative_planning)
- [Johnson M., Hofmann K., Hutton T., Bignell D. The Malmo Platform for AI Experimentation (2016)](https://github.com/Microsoft/malmo)
- [Gary Klein, David D. Woods, Jeffrey M. Bradshaw, Robert R. Hoffman, Paul J. Feltovich. Ten Challenges for Making Automation a “Team Player” in Joint Human-Agent Activity (2004)](https://www.ihmc.us/wp-content/uploads/2021/04/17.-Team-Players.pdf)
- [Wikipedia: Intelligent Agent](https://ru.wikipedia.org/wiki/%D0%98%D0%BD%D1%82%D0%B5%D0%BB%D0%BB%D0%B5%D0%BA%D1%82%D1%83%D0%B0%D0%BB%D1%8C%D0%BD%D1%8B%D0%B9_%D0%B0%D0%B3%D0%B5%D0%BD%D1%82)
- [Wikipedia: Temporal Logic](https://ru.wikipedia.org/wiki/%D0%A2%D0%B5%D0%BC%D0%BF%D0%BE%D1%80%D0%B0%D0%BB%D1%8C%D0%BD%D0%B0%D1%8F_%D0%BB%D0%BE%D0%B3%D0%B8%D0%BA%D0%B0)
- [Wikipedia: Q-learning](https://en.wikipedia.org/wiki/Q-learning)
- [Wikipedia: Deep Learning](https://ru.wikipedia.org/wiki/%D0%93%D0%BB%D1%83%D0%B1%D0%BE%D0%BA%D0%BE%D0%B5_%D0%BE%D0%B1%D1%83%D1%87%D0%B5%D0%BD%D0%B8%D0%B5)
- [Wikipedia: Tkinter](https://ru.wikipedia.org/wiki/Tkinter)

For further details, see the [Thesis.pdf](Thesis.pdf) file. Please note that the document was machine translated, and the accuracy of the translation has not been fully verified. Original thesis can be found in [VKR.pdf](VKR.pdf)
