import pygame
import sys
import numpy as np
from collections import deque

# Инициализация Pygame
pygame.init()

# Параметры окна
WIDTH, HEIGHT = 300, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint с ЦДА, заливкой треугольников и фильтрацией")

# Цвета
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
LINE_TOOL = 0
TRIANGLE_FILL_TOOL = 1
FILTER_TOOL = 2


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

    def draw_pixel(self, surface, x, y, color):
        """Отрисовка пикселя"""
        if 0 <= x < self.width and 0 <= y < self.height:
            surface.set_at((int(x), int(y)), color)

    def dda_line(self, surface, x0, y0, x1, y1, color):
        """Алгоритм ЦДА для рисования линии"""
        dx = x1 - x0
        dy = y1 - y0

        steps = max(abs(dx), abs(dy))

        if steps == 0:
            self.draw_pixel(surface, x0, y0, color)
            return

        x_inc = dx / steps
        y_inc = dy / steps

        x = x0
        y = y0

        for _ in range(int(steps) + 1):
            self.draw_pixel(surface, round(x), round(y), color)
            x += x_inc
            y += y_inc

    def triangle_fill(self, surface, x1, y1, x2, y2, x3, y3, color):
        """Алгоритм заливки треугольника"""
        # Находим bounding box
        min_x = max(0, min(x1, x2, x3))
        max_x = min(self.width - 1, max(x1, x2, x3))
        min_y = max(0, min(y1, y2, y3))
        max_y = min(self.height - 1, max(y1, y2, y3))

        # Проверяем каждую точку в bounding box
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                if self.point_in_triangle(x, y, x1, y1, x2, y2, x3, y3):
                    self.draw_pixel(surface, x, y, color)

    def point_in_triangle(self, px, py, x1, y1, x2, y2, x3, y3):
        """Проверка принадлежности точки треугольнику"""
        # Используем барицентрические координаты
        denom = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
        if denom == 0:
            return False

        a = ((y2 - y3) * (px - x3) + (x3 - x2) * (py - y3)) / denom
        b = ((y3 - y1) * (px - x3) + (x1 - x3) * (py - y3)) / denom
        c = 1 - a - b

        return 0 <= a <= 1 and 0 <= b <= 1 and 0 <= c <= 1

    def apply_filter(self, surface):
        """Алгоритм фильтрации (усредняющий фильтр 3x3)"""
        # Получаем массив пикселей
        pixels = pygame.surfarray.array3d(surface)
        filtered_pixels = np.zeros_like(pixels)

        height, width = pixels.shape[:2]

        # Применяем усредняющий фильтр 3x3
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                # Накапливаем значения в int32, чтобы не было переполнения

                r_sum = 0
                g_sum  = 0
                b_sum  = 0
                # r_sum : int = 0
                # g_sum : int = 0
                # b_sum : int = 0
                count = 0
                try:
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < width and 0 <= ny < height:
                                r_sum += int(pixels[ny, nx, 0])
                                g_sum += int(pixels[ny, nx, 1])
                                b_sum += int(pixels[ny, nx, 2])
                                count += 1
                except Exception as e:
                    print(e)

                if count > 0:
                    filtered_pixels[y, x, 0] = np.clip(r_sum // count, 0, 255)
                    filtered_pixels[y, x, 1] = np.clip(g_sum // count, 0, 255)
                    filtered_pixels[y, x, 2] = np.clip(b_sum // count, 0, 255)

        # Преобразуем обратно в поверхность
        filtered_surface = pygame.surfarray.make_surface(filtered_pixels.swapaxes(0, 1))
        return filtered_surface

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
