"""
Программа не несет пользы, только для решения задач в учебном заведение.


Задачи программы: зделать задачи по компютерной граффике
в задачи входит
Часть 1: алгоритм рисования линии ЦДА или Брезенхема;           /   алгоритм рисования линии ЦДА
Часть 2: один из алгоритмов заливки: треугольников,             /   треугольников
построченная заливка, заливка с затравкой;                      /
Часть 3: алгоритм фильтрации (любой).                           /   Усредняющий фильтр 3×3 (Mean Filter)


"""
from operator import truediv
from PIL import Image
import pygame
import sys
import numpy as np

# Инициализация Pygame
pygame.init()

# Параметры окна
WIDTH, HEIGHT = 300, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("компютерная граффика")
image = r"C:\Users\admin\Desktop\ycheba\grafica\i.png"

# Цвета
# возможность выбрать цвет каким рисовать  по первой букве
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
GRAY = (128, 128, 128)

# Инструменты
LINE_TOOL = 0               #   для рисование линии
TRIANGLE_FILL_TOOL = 1      #   для рисование триугольков
FILTER_TOOL = 2             #   фильтр
image_ = 3


class PaintApp:

    def __init__(self):
        self.screen = screen
        self.width = WIDTH
        self.height = HEIGHT

        # Создание поверхностей
        self.drawing_surface = pygame.Surface((WIDTH, HEIGHT))
        self.drawing_surface.fill(WHITE)
        self.temp_surface = pygame.Surface((WIDTH, HEIGHT))

        # Переменные состояния
        self.current_tool = LINE_TOOL
        self.current_color = BLACK
        self.points = []  # Для хранения точек
        self.drawing = False
        self.last_pos = None

        # Шрифт для интерфейса
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        # self.image = image_fon()

    def draw_pixel(self, surface, x, y, color):
        """Отрисовка пикселя"""
        if 0 <= x < self.width and 0 <= y < self.height:
            surface.set_at((int(x), int(y)), color)

    def dda_line(self, surface, x0, y0, x1, y1, color):
        """Алгоритм ЦДА для рисования линии"""
        # Ввод двух конечных точек отрезка — (x1, y1) и (x2, y2).

        # Вычисление разницы между координатами x и y конечных точек — dx и dy соответственно.
        dx = x1 - x0
        dy = y1 - y0



        steps = max(abs(dx), abs(dy))

        # условия если точки будут находиться в одной точке
        if steps == 0:
            self.draw_pixel(surface, x0, y0, color)
            return

        # Вычисление наклона линии — m = dy/dx.
        x_inc = dx / steps
        y_inc = dy / steps

        x = x0
        y = y0

        # Цикл по координатам x линии, увеличение на 1 каждый раз,
        # и вычисление соответствующей координаты y с помощью уравнения y = y1 + m(x — x1)
        for _ in range(int(steps) + 1):
            self.draw_pixel(surface, round(x), round(y), color)
            x += x_inc
            y += y_inc

    # метод отрисовка треугольника с его заливкой есть первоночальные переменные в виде 3 точек
    def triangle_fill(self, surface, x1, y1, x2, y2, x3, y3, color):
        """Алгоритм заливки треугольника"""

        # Находим bounding box
        min_x = max(0, min(x1, x2, x3))
        max_x = min(self.width - 1, max(x1, x2, x3))
        min_y = max(0, min(y1, y2, y3))
        max_y = min(self.height - 1, max(y1, y2, y3))
        # можно ли поставить фильтр блума (не применяеться, не нашел практического применения в данной области )
        # Проверяем каждую точку в bounding box
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                if self.point_in_triangle(x, y, x1, y1, x2, y2, x3, y3):
                    self.draw_pixel(surface, x, y, color)


    def point_in_triangle(self, px, py, x1, y1, x2, y2, x3, y3):
        """Проверка принадлежности точки треугольнику"""

        """ Барицентрические координаты — это способ представления точки относительно вершин треугольника. Любая точка внутри треугольника может быть выражена как:
        
        P=a⋅A+b⋅B+c⋅C,где a+b+c=1
        Где abc — весовые коэффициенты (координаты). Если они все находятся в диапазоне от 0 до 1, то точка лежит внутри треугольника
        """


        # Используем барицентрические координаты

        # denom - Это детерминант матрицы, используемый для решения системы уравнений

        denom = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)

        # если 0 значит лежит на вершине треугольника и проверка не возможна
        if denom == 0:
            return False

        a = ((y2 - y3) * (px - x3) + (x3 - x2) * (py - y3)) / denom
        b = ((y3 - y1) * (px - x3) + (x1 - x3) * (py - y3)) / denom
        c = 1 - a - b

        # если все 3 точки находяться от 0 до 1 то точка находиться внутри треугольника
        return 0 <= a <= 1 and 0 <= b <= 1 and 0 <= c <= 1

    def image_fon(self, surface):

        return pygame.image.load(image).convert()

    def draw_pixel(self, surface, x, y, color):
        surface.set_at((x, y), color)
    def get_pixel(self, surface, x, y):
        return surface.get_at((x, y))[:3]


    def apply_filter(self, surface):
        """Алгоритм фильтрации (усредняющий фильтр 3x3)"""
        # Получаем массив пикселей



        # Открытие изображения
        image_l = Image.open(image)  # Замените на путь к вашему изображению

        # Преобразование изображения в массив NumPy
        image_array = np.array(image_l)

        print(image_array)
        # Ядро фильтра (например, фильтр выделения границ)
        kernel = np.array([
            [0, -1, 0],
            [-1, 4, -1],
            [0, -1, 0]
        ])

        h, w = image_array.shape[:2]
        kh, kw = kernel.shape
        pad_h, pad_w = kh // 2, kw // 2

        # Поддержка только grayscale пока что (для простоты)
        if len(image_array.shape) == 3:
            image_array = np.mean(image_array, axis=2).astype(np.uint8)

        padded_img = np.pad(image_array, ((pad_h, pad_h), (pad_w, pad_w)), mode='edge')
        output = np.zeros_like(image_array)

        for i in range(h):
            for j in range(w):
                region = padded_img[i:i + kh, j:j + kw]
                output[i, j] = np.sum(region * kernel)


        return

    def handle_events(self):
        """Обработка событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # ЛКМ
                    self.handle_left_click(event.pos)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # ЛКМ
                    self.handle_left_release(event.pos)

            elif event.type == pygame.MOUSEMOTION:
                self.handle_mouse_motion(event.pos)

            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event.key)

        return True

    def handle_left_click(self, pos):
        """Обработка нажатия ЛКМ"""
        self.drawing = True
        self.last_pos = pos

        if self.current_tool == LINE_TOOL:
            if len(self.points) == 0:
                self.points.append(pos)
            elif len(self.points) == 1:
                self.points.append(pos)
                # Рисуем линию
                self.dda_line(self.drawing_surface,
                              self.points[0][0], self.points[0][1],
                              self.points[1][0], self.points[1][1],
                              self.current_color)
                self.points = []

        elif self.current_tool == TRIANGLE_FILL_TOOL:
            self.points.append(pos)
            if len(self.points) == 3:
                # Заливаем треугольник
                self.triangle_fill(self.drawing_surface,
                                   self.points[0][0], self.points[0][1],
                                   self.points[1][0], self.points[1][1],
                                   self.points[2][0], self.points[2][1],
                                   self.current_color)
                self.points = []

    def handle_left_release(self, pos):
        """Обработка отпускания ЛКМ"""
        self.drawing = False

    def handle_mouse_motion(self, pos):
        """Обработка движения мыши"""
        self.last_pos = pos

    def handle_keydown(self, key):
        """Обработка нажатия клавиш"""
        if key == pygame.K_1:
            self.current_tool = LINE_TOOL
            self.points = []
        elif key == pygame.K_2:
            self.current_tool = TRIANGLE_FILL_TOOL
            self.points = []
        elif key == pygame.K_3:
            self.current_tool = FILTER_TOOL
        elif key == pygame.K_4:
            self.current_tool = image_
        elif key == pygame.K_c:
            # Очистка экрана
            self.drawing_surface.fill(WHITE)
            self.points = []
        elif key == pygame.K_r:
            self.current_color = RED
        elif key == pygame.K_g:
            self.current_color = GREEN
        elif key == pygame.K_b:
            self.current_color = BLUE
        elif key == pygame.K_k:
            self.current_color = BLACK
        elif key == pygame.K_w:
            self.current_color = WHITE

    def draw_interface(self):
        """Отрисовка интерфейса"""
        # Отрисовка основного холста
        self.screen.blit(self.drawing_surface, (0, 0))

        # Отрисовка временных элементов
        self.temp_surface.fill((0, 0, 0, 0))  # Прозрачный фон

        # Предпросмотр для линии
        if self.current_tool == LINE_TOOL and len(self.points) == 1 and self.last_pos:
            self.dda_line(self.temp_surface,
                          self.points[0][0], self.points[0][1],
                          self.last_pos[0], self.last_pos[1],
                          (100, 100, 255))

        # Предпросмотр для треугольника
        elif self.current_tool == TRIANGLE_FILL_TOOL and len(self.points) >= 1 and self.last_pos:
            # Рисуем линии от существующих точек к текущей позиции
            for point in self.points:
                self.dda_line(self.temp_surface,
                              point[0], point[1],
                              self.last_pos[0], self.last_pos[1],
                              (100, 255, 100))
            # Рисуем линии между уже установленными точками
            if len(self.points) == 2:
                self.dda_line(self.temp_surface,
                              self.points[0][0], self.points[0][1],
                              self.points[1][0], self.points[1][1],
                              (100, 255, 100))
            elif len(self.points) == 3:
                self.dda_line(self.temp_surface,
                              self.points[0][0], self.points[0][1],
                              self.points[1][0], self.points[1][1],
                              (100, 255, 100))
                self.dda_line(self.temp_surface,
                              self.points[1][0], self.points[1][1],
                              self.points[2][0], self.points[2][1],
                              (100, 255, 100))
                self.dda_line(self.temp_surface,
                              self.points[2][0], self.points[2][1],
                              self.points[0][0], self.points[0][1],
                              (100, 255, 100))

        # # Применение временной поверхности
        # self.screen.blit(self.temp_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        #
        # # Панель инструментов
        # pygame.draw.rect(self.screen, GRAY, (0, 0, 200, 100))
        # pygame.draw.rect(self.screen, BLACK, (0, 0, 200, 100), 2)

        # Текст инструментов
        tool_text = [
            "ИНСТРУМЕНТЫ:",
            f"1 - Линия (ЦДА) {'[АКТИВНО]' if self.current_tool == LINE_TOOL else ''}",
            f"2 - Треугольник {'[АКТИВНО]' if self.current_tool == TRIANGLE_FILL_TOOL else ''}",
            f"3 - Фильтр {'[АКТИВНО]' if self.current_tool == FILTER_TOOL else ''}"
        ]

        # for i, text in enumerate(tool_text):
        #     text_surface = self.small_font.render(text, True, BLACK)
        #     self.screen.blit(text_surface, (10, 10 + i * 20))

        # Текст цветов
        color_text = [
            "ЦВЕТА:",
            f"R - Красный | G - Зеленый",
            f"B - Синий | K - Черный",
            f"W - Белый | Текущий: {self.current_color}"
        ]

        # for i, text in enumerate(color_text):
        #     text_surface = self.small_font.render(text, True, BLACK)
        #     self.screen.blit(text_surface, (10, 120 + i * 20))

        # Текст команд
        command_text = [
            "КОМАНДЫ:",
            "C - Очистить экран"
        ]

        # for i, text in enumerate(command_text):
        #     text_surface = self.small_font.render(text, True, BLACK)
        #     self.screen.blit(text_surface, (10, 200 + i * 20))

        # Применение фильтра
        if self.current_tool == FILTER_TOOL:
            filtered_surface = self.apply_filter(self.drawing_surface)
            self.screen.blit(filtered_surface, (0, 0))

        if self.current_tool == image_:
            image_fon = self.image_fon(self.drawing_surface)  # Вызываем функцию
            self.screen.blit(image_fon, (0, 0))

    def run(self):
        """Основной цикл программы"""
        clock = pygame.time.Clock()
        running = True

        while running:
            running = self.handle_events()
            self.draw_interface()
            pygame.display.flip()
            clock.tick(60)


        pygame.quit()
        sys.exit()


# Запуск программы
if __name__ == "__main__":
    app = PaintApp()
    app.run()
