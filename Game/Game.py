import pygame
from Game.Food import Food
from Game.Player import Player
from Game.config import COLOR_GREEN, COLOR_WHITE


class Game:
    def __init__(self, config):
        pygame.display.set_caption(config['GAME_CAPTION'])  # имя окна
        # размеры игрового поля
        self.width = config['GAME_WIDTH']
        self.height = config['GAME_HEIGHT']
        self.block_size = config['BLOCK_SIZE']
        self.border_size = config['BORDER_SIZE']
        self.info_height = config['GAME_INFO_HEIGHT']
        self.background = pygame.transform.scale(
            pygame.image.load(config['BACKGROUND_IMAGE']),
            ((self.border_size * 2) + self.width, (self.border_size * 2) + self.height + self.info_height)
        )

        self.screen = pygame.display.set_mode(
            (self.width + (self.border_size * 2),
             self.height + (self.border_size * 2) + self.info_height)
        )  # создание экрана с размером окна
        self.screen.fill(COLOR_WHITE)

        self.player = Player(
            self.width, self.height, COLOR_GREEN, self.block_size, self.border_size, config['SNAKE_IMAGE_HEAD'],
            config['SNAKE_IMAGE_TAIL']
        )  # создание объекта игрока
        self.food = Food(
            config['FOOD_IMAGE'], self.width, self.height, self.block_size, self.border_size
        )  # создание объекта еды

        self.game_over = False
        self.game_over_time = config['GAME_OVER_TIME']
        self.game_win = False
        self.game_win_time = config['GAME_WIN_TIME']
        self.score = 0  # количество очков
