from tkinter import *
from tkinter import ttk

# Класс отвечает за графический интерфейс пользователя
class Design:
    # Элементы пути, пройденного отслеживаемым агентом
    agent_paths = []
    # Идентификаторы отслеживаемых агентов
    tracking_agents = []

    # Конструктор принимает количество агентов в системе, положения препятствий и
    # точки преждевременного завершения игры на плоскости
    def __init__(self, agent_count, obstacles_pos, giveup_pos) -> None:
        # Настройка графического окна приложения
        self.master = Tk()
        self.w = Canvas(self.master, width=310, height=310, scrollregion=(-1,-5, 5, 5))
        self.w.grid(column=1, row=0, padx=10, pady=0)
        # Параметр обновления содержания графического окна (False в режиме обучения)
        self.enable_drawing = False

        # Создание фона для уровня
        self.w.create_rectangle(0, 0, 300, 300, fill='white')

        # Создание графического представления агентов
        self.agents_rect = []
        self.agent_photos = []
        self.agent_last_pos = []
        for agent_id in range(agent_count):
            # Изображения агентов находятся в файлах player№.png
            self.agent_photos.append(PhotoImage(file = f"player{agent_id}.png"))
            self.agents_rect.append(self.w.create_image(2, 2, image=self.agent_photos[-1]))
            # Сохранение предыдущего положения для отрисовки путей
            self.agent_last_pos.append(None)
        # Создание графического представления препятствий
        for obstacle in obstacles_pos:
            # Препятствия обозначаются серым цветом
            self.w.create_rectangle(30*obstacle['x'], 30*obstacle['y'], 30*(obstacle['x']+1), 30*(obstacle['y']+1), fill='lightgray')
        # Создание графического представления цели (текстура в файле pig.png)
        self.pig_photo = PhotoImage(file = 'pig.png')
        self.target_rect = self.w.create_image(0, 0, image=self.pig_photo)
        # Создание графического представления точки преждевременного завершения игры
        # Отмечается синим кругом
        self.w.create_oval(30*giveup_pos['x']+5, 30*giveup_pos['y']+5, 30*(giveup_pos['x']+1)-5, 30*(giveup_pos['y']+1)-5, fill='lightblue', outline="white")

        # Добавление строки состояния уверенности в целенаправленности напарника
        self.strategy_canvas = Canvas(self.master, width=310, height=40, scrollregion=(-5,-5, 5, 5))
        self.strategy_canvas.grid(column=1, row=1, padx=0, pady=10)
        # Создание графического представления строки состояния
        self.strategy_canvas.create_oval(0, 0, 30, 30, fill="white")
        self.strategy_canvas.create_oval(270, 0, 300, 30, fill="white")
        self.strategy_canvas.create_rectangle(15, 0, 285, 30, fill="white", outline="white")
        self.strategy_canvas.create_line(15, 0, 286, 0)
        self.strategy_canvas.create_line(15, 30, 286, 30)
        self.strategy_bar = self.strategy_canvas.create_oval(5, 5, 25, 25, fill="lightgreen")
        # Добавление подсказок по сторонам строки состояния
        self.r_label = ttk.Label(self.master, text="R", font=("Arial", 20))
        self.r_label.grid(column=0, row=1, padx=10, pady=10)
        self.f_label = ttk.Label(self.master, text="F", font=("Arial", 20))
        self.f_label.grid(column=2, row=1, padx=10, pady=10)

    # Отрисовка сущности в новом положении
    def move_pig(self, target_pos):
        # Проверка на необходимость обновления графического окна
        if not self.enable_drawing:
            return
        self.w.moveto(self.target_rect, 30*target_pos['x']+5, 30*target_pos['y']+5)

    # Отрисовка агента в новом положении
    def move_agent(self, agent_id, agent_pos):
        # Проверка на необходимость обновления графического окна
        if not self.enable_drawing:
            return
        # Отрисовка пути, пройденного агентом
        self.draw_path(agent_id, agent_pos)
        self.w.moveto(self.agents_rect[agent_id], 30*agent_pos['x']+2, 30*agent_pos['y']+2)

    # Переключение параметра, отвечающего за необходимость обновления графического окна
    def toggle_drawing_mode(self):
        self.enable_drawing = not self.enable_drawing

    # Включить отслеживание пути для агента под номером agent_id
    def track_agent(self, agent_id):
        self.tracking_agents.append(agent_id)

    # Отрисовка пути, пройденного агентом
    def draw_path(self, agent_id, new_pos):
        # Проверка, отслеживается ли данный агент
        if agent_id not in self.tracking_agents:
            return
        # добавление нового элемента пути
        if self.agent_last_pos[agent_id] != None:
            self.agent_paths.append(self.w.create_line(30*self.agent_last_pos[agent_id]['x']+15,\
                                                       30*self.agent_last_pos[agent_id]['y']+15,\
                                                       30*new_pos['x']+15, 30*new_pos['y']+15, width=3))
        # Обновление цвета пути, чтобы показать течение времени
        for id, path in enumerate(self.agent_paths):
            red = 255 - 255 * (id+1) // len(self.agent_paths)
            self.w.itemconfig(path, fill="#%02x%02x%02x" % (255, red, red))
        # Обновление последнего положения агента
        self.agent_last_pos[agent_id] = new_pos

    # Обновление содержимого графического окна
    def update(self, value, right_side, title):
        # Проверка на необходимость обновления графического окна
        if not self.enable_drawing:
            return
        # Обновление заголовка окна
        self.master.title(title)
        # Обновление строки состояния
        self.strategy_canvas.moveto(self.strategy_bar, 270*value+5)
        self.strategy_canvas.itemconfig(self.strategy_bar, fill="lightgreen" if ["R", "F"][round(value)] == right_side else "red")
        self.r_label.configure(underline=right_side != "R")
        self.f_label.configure(underline=right_side == "R")
        # Отрисовка всех обновлений на экране
        self.master.update()

    # Очистка всех путей агентов при сбросе игрового прогресса
    def clear_paths(self):
        if not self.enable_drawing:
            return
        for path in self.agent_paths:
            self.w.delete(path)
        self.agent_last_pos = [None] * len(self.agent_last_pos)
        self.agent_paths.clear()