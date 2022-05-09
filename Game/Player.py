import math
from enum import Enum

import pygame
from Game.utils import updateScreen


class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4
    NOPE = 5


class Player:
    def __init__(self, gameWidth, gameHeight, color, blockSize, borderSize, headImage, tailImage):
        self.pos_x = borderSize + (math.floor((gameWidth / blockSize) / 4) * blockSize)
        self.pos_y = borderSize + (math.floor((gameHeight / blockSize) / 2) * blockSize)
        self.position = []
        self.position.append([self.pos_x, self.pos_y])
        self.color = color
        self.image_head = pygame.transform.scale(pygame.image.load(headImage), (blockSize, blockSize))
        self.image_tail = pygame.transform.scale(pygame.image.load(tailImage), (blockSize, blockSize))
        self.direction = Direction.RIGHT
        self.pos_change = blockSize

    def updatePosition(self, x, y):
        if self.position[-1][0] != x or self.position[-1][1] != y:
            if len(self.position) > 1:
                for i in range(0, len(self.position) - 1):
                    self.position[i][0], self.position[i][1] = self.position[i + 1]
            self.position[-1][0] = x
            self.position[-1][1] = y

    def move(self, direction, game, food):
        # if self.is_eaten:
        #     self.position.append([self.pos_x, self.pos_y])
        #     self.is_eaten = False
        is_eaten = False

        if direction == Direction.NOPE:
            return is_eaten

            # передвигаем игрока в нужное направление
        self.direction = direction
        if self.direction == Direction.RIGHT:
            self.pos_x += self.pos_change
        elif self.direction == Direction.LEFT:
            self.pos_x -= self.pos_change
        elif self.direction == Direction.DOWN:
            self.pos_y += self.pos_change
        elif self.direction == Direction.UP:
            self.pos_y -= self.pos_change

        # если произошла коллизия с границами карты или игрок врезался в себя
        if (self.pos_x < game.border_size) or \
                (self.pos_x > game.border_size + ((math.floor(game.width / game.block_size) - 1) * game.block_size)) or \
                (self.pos_y < game.border_size) or \
                (self.pos_y > game.border_size + ((math.floor(game.height / game.block_size) - 1) * game.block_size)) or \
                ([self.pos_x, self.pos_y] in self.position):
            game.game_over = True

        # если игрок нашел еду
        if self.pos_x == food.pos_x and self.pos_y == food.pos_y:
            food.createNewCoord(game.width, game.height, game.block_size, game.border_size, self.position)
            self.position.append([self.pos_x, self.pos_y])
            game.score += 1
            is_eaten = True

        # если игрок победил
        if ((game.width / game.block_size) * (game.height / game.block_size)) == len(self.position):
            game.game_over = True
            game.game_win = True
            return is_eaten

        self.updatePosition(self.pos_x, self.pos_y)
        return is_eaten

    def render(self, game):
        if game.game_over:
            pygame.time.wait(game.game_over_time)
        elif game.game_win:
            pygame.time.wait(game.game_win_time)
        else:
            i = 0
            for [x, y] in self.position[::-1]:
                if (i % 2 == 0):
                    image = self.image_head
                else:
                    image = self.image_tail
                game.screen.blit(image, (x, y))
                i += 1

            updateScreen()
