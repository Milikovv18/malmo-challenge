# Импорт агентов из файла agents.py (Листинг 2)
from agents import Focused, Random, Wise
from tkinter import *
# Импорт класса Design из файла design.py (Листинг 4)
from design import *
import random
import time

# Установка количества агентов в системе (1 или 2)
NUM_OF_AGENTS = 2
# Макимально допустимое количество шагов для каждого из агентов
MAX_FITNESS = 200
# Структура препятствий разреженного лабиринта, в котором существует путь между двумя любыми клетками
obstacle_pos = \
[{'x': 2, 'y': 1}, {'x': 5, 'y': 1}, {'x': 7, 'y': 1}, {'x': 1, 'y': 2}, {'x': 4, 'y': 2}, {'x': 8, 'y': 2}, {'x': 1, 'y': 3}, {'x': 3, 'y': 3}, {'x': 6, 'y': 3},\
{'x': 6, 'y': 4}, {'x': 7, 'y': 4}, {'x': 1, 'y': 5}, {'x': 4, 'y': 5}, {'x': 8, 'y': 5}, {'x': 4, 'y': 6}, {'x': 1, 'y': 7},{'x': 2, 'y': 7},{'x': 3, 'y': 7},{'x': 4, 'y': 7},\
{'x': 7, 'y': 7}, {'x': 3, 'y': 8}, {'x': 6, 'y': 8}, {'x': 7, 'y': 8}, {'x': 8, 'y': 8}, {'x': 1, 'y': 8}]
# Точка преждевременного завершения игры
giveup_pos = {'x' : 9, 'y' : 0}

# Инициализация графического интерфейса пользователя
design = Design(NUM_OF_AGENTS, obstacle_pos, giveup_pos)

# Случайный выбор свободной клетки на поле
def generate_object():
    global agents_brain
    # Получение положений всех агентов
    agents_pos = [agent.get_pos() for agent in agents_brain]
    obj_pos = {}
    while True:
        # Случайный выбор клетки по двум координатам
        obj_pos['x'] = int(9*random.random())
        obj_pos['y'] = int(9*random.random())
        # Если клетка не занята агентами или препятствиями
        if obj_pos not in agents_pos and obj_pos not in obstacle_pos:# and edibility() >= 4-NUM_OF_AGENTS:
            return obj_pos

# Инициализация целенаправленного, мудрого (анализирующего) агентов и агента со случайным поведением
# Поскольку NUM_OF_AGENTS принимает значение 2, система учитывает только двух первых агентов
# При запуске нового эпизода первое место занимает либо первый, либо третий агент из списка
agents_brain = []
agents_brain.append(Focused(generate_object(), MAX_FITNESS))
agents_brain.append(Wise(generate_object(), MAX_FITNESS))
agents_brain.append(Random(generate_object(), MAX_FITNESS))
# Акцивация отслеживания пути анализируемого агента
design.track_agent(0)
# Генерация начального положения цели
target_pos = generate_object()
# Отрисовка цели
design.move_pig(target_pos)

# Проверка на окруженность цели препятствиями
def edible():
    global target_pos
    obstacle_count =\
        ({'x' : target_pos['x']-1, 'y' : target_pos['y']} in obstacle_pos or target_pos['x'] == 0) +\
        ({'x' : target_pos['x']+1, 'y' : target_pos['y']} in obstacle_pos or target_pos['x'] == 9) +\
        ({'x' : target_pos['x'], 'y' : target_pos['y']-1} in obstacle_pos or target_pos['y'] == 0) +\
        ({'x' : target_pos['x'], 'y' : target_pos['y']+1} in obstacle_pos or target_pos['y'] == 9)
    # Если цель окружена минимум 2 препятствиями, ее возможно поймать
    return obstacle_count > 1

caught_per_agent = [False] * NUM_OF_AGENTS
# Начало новой игры, когда цель достигнута
def catch(agent):
    global target_pos, caught_per_agent, fitness, steps, target_brain, target_move_timer
    # Агенты должны находиться в разных клетках для поимки сущности
    if NUM_OF_AGENTS > 1 and agents_brain[agent].get_pos() == agents_brain[1-agent].get_pos():
        return
    caught_per_agent[agent] = True
    # Если каждый агент поймал сущность (сущность окружена), эпизод перезапускается
    if not all(caught_per_agent):
        return
    # Случайный выбор агента для новой игры (целенаправленный или со случайным поведением)
    agent_id = int(2*random.random())
    agents_brain[0], agents_brain[2] = agents_brain[2*agent_id], agents_brain[2*(1-agent_id)]
    # Временная заморозка цели на начало игры (на первые 5 шагов агентов)
    target_move_timer = 5
    # Случайный выбор клеток для расположения агентов в новой игре
    for a in range(NUM_OF_AGENTS):
        agents_brain[a].position = generate_object()
    # Обновление положения цели в классе, отвечающем за ее перемещение
    target_brain.position = target_pos = generate_object()
    # Сброс игрового прогресса
    fitness = 0
    caught_per_agent = [False] * NUM_OF_AGENTS
    # Отрисовка цели в новом положении
    design.move_pig(target_pos)
    # Очистка пути, пройденного анализируемым агентом
    design.clear_paths()

# Перезапуск игры
def restart_game():
    global caught_total, caught_per_agent
    # Сброс игрового прогресса
    caught_total = -1
    caught_per_agent = [False] * NUM_OF_AGENTS
    for agent in range(NUM_OF_AGENTS):
        agents_brain[agent].reset()
        # Начало новой игры для каждого агента
        catch(agent)

# Начало основного цикла программы
steps = 0 # Суммарное количество шагов, сделанных каждым агентом, по всем эпизодам
fitness = 0 # Количество шагов, сделанных каждым агентом за текущий эпизод
game_loses = 1 # Количество эпизодов, в которых агент неверно определил намерения напарника
game_wins = 1 # Количество эпизодов, в которых агент верно определил намерения напарника
target_brain = Random(target_pos, MAX_FITNESS) # Агент, управляющий перемещением сущности
target_move_timer = 5 # Таймер, разрешающий/запрещающий сущности передвигаться
while True:
    # Перемещение сущности-цели случайным образом
    if target_move_timer < 0:
        target_res = target_brain.move(target_pos, obstacle_pos, fitness=0)
        target_pos = target_brain.get_pos()
        # Если цель переместилась, она больше не является пойманной
        for agent in range(NUM_OF_AGENTS):
            caught_per_agent[agent] = False
        design.move_pig(target_pos)

    # Обновление таймера, разрешающего/запрещающего сущности передвигаться
    if target_move_timer == 0:
        # Максимум 5 шагов перемещния и 10 - отдыха
        target_move_timer = int(15 * random.random() - 5)
    else:
        target_move_timer -= target_brain.sign(target_move_timer)
    
    # Обновление положения агентов
    for agent in range(NUM_OF_AGENTS):
        # Если агент умеет анализировать поведение, выполняется анализ
        if hasattr(agents_brain[agent], "evaluate_strategy"):
            # Получение актуальных данных о поведении напарника в виде вероятности
            avg_guess = agents_brain[agent].evaluate_strategy(agents_brain[0], target_pos, fitness)
            binary_guess = round(avg_guess)

            # Выбор стратегии анализирующего агента в соответствии с актуальными данными
            target = [giveup_pos, target_pos][binary_guess]
            agents_brain[agent].set_edibility([True, edible()][binary_guess])

            # Если напарник предположительно не желает кооперироваться, забываем про сущность
            if binary_guess == 0:
                caught_per_agent[agent] = False
        # Если нет, выставляются параметры по умолчанию
        else:
            target = target_pos # цель - сущность
            agents_brain[agent].set_edibility(edible())
        
        # Передача управления текущему агенту
        result = agents_brain[agent].move(target, obstacle_pos, fitness)

        # Отрисовка агента в новом положении
        design.move_agent(agent, agents_brain[agent].get_pos())
        
        # Проверка на глобальные изменения в игре
        if result == 1 and target == target_pos: # Текущий агент достиг цели
            catch(agent)
        # Цели была достигнута всеми агентами, или агент столкнулся с препятствием
        if result < 0 or all(caught_per_agent):
            # Обновление счетчика игр в соответствии с правилами
            game_wins += agents_brain[0].label != "R"
            game_loses += agents_brain[0].label == "R"
            restart_game()
        if agents_brain[agent].get_pos() == giveup_pos: # Текущий агент сдался
            # Обновление счетчика игр в соответствии с правилами
            game_wins += agents_brain[0].label == "R"
            game_loses += agents_brain[0].label != "R"
            restart_game()

        # Обновление информации о достижении цели в классе агента
        agents_brain[agent].set_goal_state(caught_per_agent[agent])
    # Обновление графической информации в окне приложения
    design.update(avg_guess, agents_brain[0].label, agents_brain[0].label + " (" + '{0:.2f}'.format(game_wins / (game_wins + game_loses)) + ")")

    # Если цель достижима в текущем состоянии среды
    currently_edible = edible()

    # После 199990 шага агента начинается отрисовка графического интерфейса пользователя
    if steps == 199990:
        design.toggle_drawing_mode()
    # Каждые 10000 шагов выводится статус обучения модели
    if steps % 10000 == 0 and currently_edible:
        print("Wise agent made", steps, "steps")
    # Процессы среды необходимо замедлить, чтобы пользователь мог следить за прогрессом
    if 199990 < steps:
        time.sleep(0.1)

    # Если агенты не двигаются, счетчик шагов не меняется
    if currently_edible:
        steps += 1
        fitness += 1