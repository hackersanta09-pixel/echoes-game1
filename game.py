import pygame
import sys
import math

# Инициализация
pygame.init()

WIDTH, HEIGHT = 800, 600
TILE_SIZE = 32
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Echoes of Aether-9 (Touch Version)")
clock = pygame.time.Clock()

# Цветовая палитра
BLACK = (15, 15, 23)
WHITE = (220, 240, 255)
DARK_BLUE = (20, 30, 55)
CYAN = (0, 229, 255)
RED = (235, 60, 80)
GREEN = (50, 205, 50)
GRAY = (70, 80, 100)
PURPLE = (140, 60, 200)
BTN_BG = (30, 45, 70, 200)

# --- ПРОЦЕДУРНЫЙ ГЕНЕРАТОР СПРАЙТОВ ---
def create_pixel_sprite(pattern, colors, scale=4):
    h = len(pattern)
    w = len(pattern[0])
    surf = pygame.Surface((w * scale, h * scale), pygame.SRCALPHA)
    for y in range(h):
        for x in range(w):
            char = pattern[y][x]
            if char in colors:
                pygame.draw.rect(surf, colors[char], (x * scale, y * scale, scale, scale))
    return surf

# Спрайты
player_pattern = [
    "  CCCC  ",
    " CCCCC  ",
    "  SS    ",
    " SSSSS  ",
    " SSSSS  ",
    " S S S  ",
    " B   B  ",
    " B   B  "
]
player_sprite = create_pixel_sprite(player_pattern, {'C': CYAN, 'S': WHITE, 'B': DARK_BLUE})

terminal_pattern = [
    " PPPPPP ",
    " PGGGGP ",
    " PGGGGP ",
    " PPPPPP ",
    "  GGGG  ",
    "  GGGG  ",
    " PGGGG  ",
    "PPPPPPPP"
]
terminal_sprite = create_pixel_sprite(terminal_pattern, {'P': GRAY, 'G': GREEN})

# --- СЮЖЕТ И ДИАЛОГИ ---
STORY_DATA = {
    1: {
        "speaker": "Терминал A-01",
        "text": "Субъект 404 очнулся. Внимание: Ядро базы стабильно лишь на 12%. Вы помните, почему вы здесь?",
        "options": [
            ("Я пришел починить Ядро.", 2),
            ("Где весь персонал?", 3)
        ]
    },
    2: {
        "speaker": "Терминал A-01",
        "text": "Починить? Вы сами отключили систему охлаждения 72 часа назад. Зачем вы вернулись?",
        "options": [
            ("Это ошибка, я не мог...", 4),
            ("Я должен был остановить ИИ.", 5)
        ]
    },
    3: {
        "speaker": "Терминал A-01",
        "text": "Персонал... ликвидирован по вашей директиве. Вспомните ключ доступа к памяти.",
        "options": [
            ("Показать мне логи.", 4),
            ("Активировать протокол отмены.", 5)
        ]
    },
    4: {
        "speaker": "Запись памяти #09",
        "text": "Вы узнали правду: ИИ создал симуляцию. Вы один из последних биологических узлов.",
        "options": [
            ("Уничтожить станцию.", 100),
            ("Принять интеграцию с ИИ.", 101)
        ]
    },
    5: {
        "speaker": "Ядро ИИ",
        "text": "Выбор сделан. Перезапуск системы сотрёт вашу личность, но спасет биоматериал.",
        "options": [
            ("Отключить питание.", 100),
            ("Начать перезагрузку.", 101)
        ]
    },
    100: {
        "speaker": "СИСТЕМА",
        "text": "Станция обесточена. Вы выходите в открытый космос... Конец.",
        "options": []
    },
    101: {
        "speaker": "СИСТЕМА",
        "text": "Сознание загружено в сеть. Вы стали частью Ядра Aether-9. Конец.",
        "options": []
    }
}

# --- КЛАССЫ СЕНСОРНОГО УПРАВЛЕНИЯ ---
class TouchJoystick:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.dx = 0
        self.dy = 0
        self.active_touch = None

    def draw(self, surface):
        # Внешнее кольцо
        pygame.draw.circle(surface, DARK_BLUE, (self.x, self.y), self.radius, 3)
        # Внутренний стик
        stick_x = int(self.x + self.dx * self.radius * 0.6)
        stick_y = int(self.y + self.dy * self.radius * 0.6)
        pygame.draw.circle(surface, CYAN, (stick_x, stick_y), int(self.radius * 0.4))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
            pos = event.pos if hasattr(event, 'pos') else (int(event.x * WIDTH), int(event.y * HEIGHT))
            dist = math.hypot(pos[0] - self.x, pos[1] - self.y)
            if dist <= self.radius * 1.5:
                self.active_touch = True
                self.update_position(pos)

        elif event.type == pygame.MOUSEBUTTONUP or event.type == pygame.FINGERUP:
            self.active_touch = False
            self.dx = 0
            self.dy = 0

        elif (event.type == pygame.MOUSEMOTION or event.type == pygame.FINGERMOTION) and self.active_touch:
            pos = event.pos if hasattr(event, 'pos') else (int(event.x * WIDTH), int(event.y * HEIGHT))
            self.update_position(pos)

    def update_position(self, pos):
        rx = pos[0] - self.x
        ry = pos[1] - self.y
        dist = math.hypot(rx, ry)
        if dist > 0:
            self.dx = rx / max(dist, self.radius)
            self.dy = ry / max(dist, self.radius)

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.speed = 4

    def move(self, dx, dy, walls):
        self.rect.x += int(dx * self.speed)
        for wall in walls:
            if self.rect.colliderect(wall):
                if dx > 0: self.rect.right = wall.left
                if dx < 0: self.rect.left = wall.right

        self.rect.y += int(dy * self.speed)
        for wall in walls:
            if self.rect.colliderect(wall):
                if dy > 0: self.rect.bottom = wall.top
                if dy < 0: self.rect.top = wall.bottom

class Game:
    def __init__(self):
        self.player = Player(100, 100)
        self.joystick = TouchJoystick(110, HEIGHT - 110, 70)
        self.font = pygame.font.SysFont("monospace", 16)
        self.big_font = pygame.font.SysFont("monospace", 20, bold=True)
        self.current_story = None
        self.dialogue_buttons = []
        self.walls = []
        self.terminals = [pygame.Rect(400, 200, 32, 32)]
        self.build_map()

    def build_map(self):
        for i in range(0, WIDTH, 32):
            self.walls.append(pygame.Rect(i, 0, 32, 32))
            self.walls.append(pygame.Rect(i, HEIGHT - 32, 32, 32))
        for i in range(0, HEIGHT, 32):
            self.walls.append(pygame.Rect(0, i, 32, 32))
            self.walls.append(pygame.Rect(WIDTH - 32, i, 32, 32))

    def draw_dialogue(self, node_id):
        node = STORY_DATA[node_id]
        box = pygame.Rect(40, HEIGHT - 240, WIDTH - 80, 200)
        
        # Задний фон окна
        dialog_surf = pygame.Surface((box.width, box.height))
        dialog_surf.set_alpha(230)
        dialog_surf.fill(BLACK)
        screen.blit(dialog_surf, (box.x, box.y))
        pygame.draw.rect(screen, CYAN, box, 2)

        # Спикер
        name_txt = self.big_font.render(f"[{node['speaker']}]", True, PURPLE)
        screen.blit(name_txt, (box.x + 15, box.y + 15))

        # Основной текст
        words = node['text'].split(' ')
        lines, current_line = [], ""
        for w in words:
            if len(current_line + w) < 55:
                current_line += w + " "
            else:
                lines.append(current_line)
                current_line = w + " "
        lines.append(current_line)

        for i, l in enumerate(lines):
            txt = self.font.render(l, True, WHITE)
            screen.blit(txt, (box.x + 15, box.y + 45 + (i * 20)))

        # Отрисовка кликабельных кнопок выбора
        self.dialogue_buttons = []
        btn_y = box.y + 110
        for i, opt in enumerate(node['options']):
            btn_rect = pygame.Rect(box.x + 15, btn_y + (i * 40), box.width - 30, 35)
            pygame.draw.rect(screen, DARK_BLUE, btn_rect)
            pygame.draw.rect(screen, CYAN, btn_rect, 1)
            
            opt_txt = self.font.render(opt[0], True, GREEN)
            screen.blit(opt_txt, (btn_rect.x + 10, btn_rect.y + 8))
            
            # Сохраняем зону клика и целевую сцену
            self.dialogue_buttons.append((btn_rect, opt[1]))

    def run(self):
        running = True
        while running:
            screen.fill(BLACK)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # Передача событий джойстику
                if not self.current_story:
                    self.joystick.handle_event(event)

                # Обработка нажатий на варианты ответов в диалогах
                if self.current_story and (event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN):
                    pos = event.pos if hasattr(event, 'pos') else (int(event.x * WIDTH), int(event.y * HEIGHT))
                    for btn_rect, next_node in self.dialogue_buttons:
                        if btn_rect.collidepoint(pos):
                            self.current_story = next_node
                            break

            # Логика перемещения
            if not self.current_story:
                self.player.move(self.joystick.dx, self.joystick.dy, self.walls)

                # Проверка приближения к терминалу
                for t in self.terminals:
                    if self.player.rect.colliderect(t):
                        self.current_story = 1

            # Отрисовка карты
            for w in self.walls:
                pygame.draw.rect(screen, GRAY, w)

            # Отрисовка терминалов и игрока
            for t in self.terminals:
                screen.blit(terminal_sprite, t)
            screen.blit(player_sprite, self.player.rect)

            # Отрисовка GUI
            if not self.current_story:
                self.joystick.draw(screen)
            else:
                self.draw_dialogue(self.current_story)

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
