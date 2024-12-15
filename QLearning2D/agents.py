# Импорт класса Strategy из файла strategy.py (Листинг 4)
from Strategy import Strategy, get_L1distance_from_target
from random import random
import json

# Базовый класс перемещающегося объекта
class Observer:
    label = "O" # Метка класса
    # Список наград, предоставляемых средой
    rewards = {'step' : -1, 'step_back' : -200, 'loss' : -1000, 'caught' : 50, 'stay' : -10}

    # Конструктор принимает начальную позицию объекта и максимально допустимое количество шагов за игру
    def __init__(self, pos, max_fitness) -> None:
        self.position = pos
        self.max_fitness = max_fitness
        self.last_move = 0 # Предыдущее действие, соверешенное агентом
        self.goal_achieved = False # Достигнута ли цель (агент находится на соседней клетке от сущности)
        self.edible = False # Достижима ли цель (возможно ли поймать сущность)

    # Геттер положения агента
    def get_pos(self):
        return self.position

    # Получение размера награждения за сооветствующее действие
    def get_reward(self, action):
        return self.rewards[action]

    # Получение знака числа
    def sign(self, value):
        if value < 0: return -1
        elif value > 0: return +1
        else: return 0

    # Формирование строки состояния системы из положений цели и препятствийы
    def generate_state(self, target, obstacles):
        # Горизонтальное (-1,0,1) и вертикальное (-1,0,1) положения цели относительно агента
        target_related = 3*self.sign(target['y']-self.position['y']) + self.sign(target['x']-self.position['x'])
        # Наличие препятствия слева от агента
        left_side = int({'x' : self.position['x']-1, 'y' : self.position['y']} in obstacles)
        # Наличие препятствия снизу от агента
        bottom_side = int({'x' : self.position['x'], 'y' : self.position['y']+1} in obstacles)
        # Наличие препятствия справа от агента
        right_side = int({'x' : self.position['x']+1, 'y' : self.position['y']} in obstacles)
        # Наличие препятствия сверху от агента
        upper_side = int({'x' : self.position['x'], 'y' : self.position['y']-1} in obstacles)
        # Комбинация наличия препятствий со всех сторон
        obstacle_comb = (left_side << 3) + (bottom_side << 2) + (right_side << 1) + upper_side
        # Комбинация всех состояний в одну строку
        return str(4 * (15*target_related + obstacle_comb) + self.last_move)
    
    # Установка достижимости цели извне класса
    def set_edibility(self, edible):
        self.edible = edible

    # Совершения действия агентом и получение награды
    def move(self, target, obstacles, fitness):
        # Текущее состояние среды
        state = self.generate_state(target, obstacles)
        # Получение наилучшего или случайного движения агента
        move = self.get_best_move(state)

        # Результат действия агента (не награда), нейтральный по умолчанию
        result = 0

        # Получение новых координат агента на плоскости
        tempX = self.position['x'] + (move == 1) -(move == 3)
        tempY = self.position['y'] + (move == 2) -(move == 0)
        # Обновление положения агента
        self.position = {'x' : tempX, 'y' : tempY}
        # Если агент вышел за пределы уровня, столкнулся с препятствием или
        # превысил максимально допустимое колчичество шагов за один эпизод
        if not 0 <= tempX < 10 or not 0 <= tempY < 10 or self.position in obstacles or fitness > self.max_fitness:
            result = -1
            reward = self.get_reward('loss')
        # Если агент достиг цели (находит в той клетке или смежной с ней)
        elif abs(tempX-target['x']) + abs(tempY-target['y']) <= 1:
            result = 1 # Goal has been achieved
            reward = self.get_reward('caught')
        # Обработка перемещения агента на предыдущую позицию
        elif self.last_move == 0 and move == 2:
            reward = self.get_reward('step_back')
        elif self.last_move == 1 and move == 3:
            reward = self.get_reward('step_back')
        elif self.last_move == 2 and move == 0:
            reward = self.get_reward('step_back')
        elif self.last_move == 3 and move == 1:
            reward = self.get_reward('step_back')
        else:
            reward = self.get_reward('step')

        # Получение нового состония системы
        newState = self.generate_state(target, obstacles)
        # Обучение модели на основании последнего шага и награды
        self.train(state, move, reward, newState)
        # Обновление последнего шага агента
        self.last_move = move
        # -1 - агент нарушил правила, 0 - состояние не изменилось, 1 - агент достиг цели
        return result
    
    # Установка состояния достижения цели извне класса
    def set_goal_state(self, achieved):
        self.goal_achieved = achieved

    # Сброс игрового прогресса
    def reset(self):
        self.goal_achieved = False

# Класс целенаправленного агента
class Focused(Observer):
    label = "F" # Метка класса

    def __init__(self, pos, max_fitness) -> None:
        super().__init__(pos, max_fitness)
        # Параметры для Q-обучения
        self.learn_rate = 0.1
        self.discount = 0.9
        self.randomness = 0.0 # 0.9 для обучения
        self.randomness_decay = 1.3
        self.randomness_min = 0.00005

        # Загрузка готовой Q-таблицы для целенаправленого агента
        self.load_Q()
        # Для обучения модели навигации необходимо раскомментировать код и
        # запустить программу с одним агентом
        # Нельзя запускать параллельно с обучением модели определения намерений,
        # это не даст желаемого результата
        #self.Q = {} # Filling self.Q with all zeroes
        #for y in range(-1,2): # Lower, Upper, Equal
        #    for x in range(-1,2): # Left, Right, Equal
        #        for o in range(15): # Combinations of 4 obstacles around agent
        #            for prev in range(4): # Previous move
        #                shift = 4 * (15 * (3*y + x) + o) + prev
        #                self.Q[str(shift)] = {}
        #                for a in range(4): # Up, Right, Down, Left
        #                    self.Q[str(shift)][str(a)] = 0

    def move(self, target, obstacles, fitness):
        # Если цель недостижима или уже достигнута, целенаправленному агенту не следует двигаться
        if self.goal_achieved == True or not self.edible:
            return 0
        # Вызов родительской функции перемещения агента
        return super().move(target, obstacles, fitness)

    # Получить наилучшее действие в соответствии с Q-таблицей или выбрать случайное для исследования среды
    def get_best_move(self, state):
        return int(max(self.Q[state], key=self.Q[state].get)) if random() > self.randomness else int(4*random())

    # Функция тренировки модели обновляет значение в ячейке Q-таблицы на пересечении state и action
    def train(self, state, action, reward, newState):
        # Значение не обновляется, если действие привело к завершению игры
        self.Q[state][str(action)] *= 1 - self.learn_rate
        self.Q[state][str(action)] += self.learn_rate *\
            (reward + self.discount * max(self.Q[newState].values()) * int(reward != self.rewards['loss']))

    # Уменьшение случайности в поведении агента при обучении модели
    def reset(self):
        super().reset()
        if self.randomness > self.randomness_min:
            self.randomness /= self.randomness_decay

    # Сохранить Q-таблицу в файл
    def save_Q(self):
        open("Agent.json", "w").write(json.dumps(self.Q))

    # Загрузить Q-таблицу из файла
    def load_Q(self):
        self.Q = json.load(open("Agent.json", "r"))

# Класс "мудрого" агента, выполняющего анализ поведения объекта Observer
class Wise(Focused):
    label = "W" # Метка класса

    def __init__(self, pos, max_fitness) -> None:
        super().__init__(pos, max_fitness)
        # Перед началом новой игры напарник по умолчанию считается целенаправленным
        self.avg_guess = 1
        # Инициализация объекта Strategy для определения намерений
        self.strategy = Strategy()

    # Функция оценки поведения напарника
    def evaluate_strategy(self, other_agent, target_pos, fitness):
        # Получение расстояния от агента до цели в метрике L1
        dist_to_target = get_L1distance_from_target(other_agent.get_pos(), target_pos)
        # Задержка для более точного определения
        if fitness > 3:
            # Получение текущего состояния напарника
            strat_state = self.strategy.get_state(dist_to_target, fitness)
            # Оценка его поведения
            strat_guess = self.strategy.get_best_guess(strat_state)
            # Награда, размер которой зависит от правильности определения поведения
            strat_reward = 1 if ["R", "F"][strat_guess] == other_agent.label else 0
            # Обучение модели на основании состояния напарника и награды
            self.strategy.train(strat_state, strat_guess, strat_reward, strat_state if strat_guess == 1 else str(int(36*random())))
            # Обновление вероятности целенаправленности напарника
            self.avg_guess = 0.80 * self.avg_guess + 0.20 * strat_guess
        # Если напарник предположительно имеет случайное поведение, сброс состояния достижения цели
        if round(self.avg_guess) == 0:
            self.goal_achieved = False
        # Возврат нового значения вероятности
        return self.avg_guess
    
    # Уменьшение случайности тренировки модели определения намерений
    def reset(self):
        super().reset()
        self.strategy.update_randomness()
        self.avg_guess = 1

# Класс агента со случайным поведением
class Random(Observer):
    label = "R" # Метка класса

    def __init__(self, pos, max_fitness) -> None:
        super().__init__(pos, max_fitness)

    # Выбор наилучшего действия, не приводящего к немедленному завершению игры
    def get_best_move(self, state):
        # Анализ наличия препятствий вокруг агента
        obstacle_info = int(state) // 4 % 15
        # Обрезка недопустимых действий
        actions = ('3' if not (obstacle_info & 8) and self.position['x'] != 0 else '') +\
            ('2' if not (obstacle_info & 4) and self.position['y'] != 9 else '') +\
            ('1' if not (obstacle_info & 2) and self.position['x'] != 9 else '') +\
            ('0' if not (obstacle_info & 1) and self.position['y'] != 0 else '')
        return int(actions[int(len(actions)*random())])

    # Функция тренировки модели отсутствует
    def train(self, state, action, reward, newState):
        pass

    # Функция сброса прогресса отсутствует
    def reset(self):
        pass