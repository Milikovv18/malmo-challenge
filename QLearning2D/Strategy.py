from random import random
import json

# Класс отвечает за анализ поведения агента
class Strategy:
    def __init__(self) -> None:
        # Параметры для Q-обучения
        self.learn_rate = 0.1
        self.discount = 0.9
        self.randomness = 0.9
        self.randomness_decay = 1.0005
        self.randomness_min = 0.00005

        # Инициализация Q-таблицы нулями
        # Можно использовать self.load_Q() для загрузки готовой таблицы
        self.Q = {}
        # Минимальное расстояние до цели равно (0,0) и максимальное (9,9), поэтому L1 расстояние находится в пределах [0, 18]
        for dist in range(20):
            # 3 категории: первый шаг агента, первые 15 шагов и остальные
            for stage in range(3):
                shift = 3 * dist + stage
                self.Q[str(shift)] = {}
                # Два варианта "ответа": агент целенаправленный или со случайным поведением
                for strategy in range(2):
                    self.Q[str(shift)][str(strategy)] = 0

    # Выбрать наиболее подходящий класс поведения или случайный при обучении модели
    def get_best_guess(self, state):
        return int(max(self.Q[state], key=self.Q[state].get)) if random() > self.randomness else int(2*random())

    # Функция тренировки модели обновляет значение в ячейке Q-таблицы на пересечении state и guess (action)
    def train(self, state, guess, reward, newState):
        self.Q[state][str(guess)] *= 1 - self.learn_rate
        self.Q[state][str(guess)] += self.learn_rate * (reward + self.discount * max(self.Q[newState].values()))

    # Уменьшение случайности в предсказании намерений агента
    def update_randomness(self):
        if self.randomness > self.randomness_min:
            self.randomness /= self.randomness_decay

    # Получить текущее состояние агента в системе на основании расстояния от него до цели и
    # количества шагов с начала игры
    def get_state(self, relative_distance, steps_count):
        # Разделение количества сделанных шагов на категории
        step_group = 0 if steps_count <= 1 else 1 if steps_count <= 15 else 2
        # Формирование строки состояния
        state = 3 * relative_distance + step_group
        return str(state)

    # Сохранить Q-таблицу в файл
    def save_Q(self):
        open("Strategy.json", "w").write(json.dumps(self.Q))

    # Загрузить Q-таблицу из файла
    def load_Q(self):
        self.Q = json.load(open("Strategy.json", "r"))

# Получение расстояния метрики L1 между двумя точками на плоскости
def get_L1distance_from_target(agent_pos, target_pos):
    return abs(agent_pos['x']-target_pos['x']) + abs(agent_pos['y']-target_pos['y'])