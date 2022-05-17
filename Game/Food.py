import math

import pygame

from Game.utils import getRandomCoord, updateScreen


class Food(object):
    def __init__(self, imagePath, gameWidth, gameHeight, blockSize, borderSize):
        self.pos_x = (borderSize + (math.floor(gameWidth / blockSize) * blockSize)) - (
                math.floor((gameWidth / blockSize) / 2) * blockSize)
        self.pos_y = borderSize + (math.floor((gameHeight / blockSize) / 2) * blockSize)
        self.image = pygame.transform.scale(pygame.image.load(imagePath), (blockSize, blockSize))

    def createNewCoord(self, gameWidth, gameHeight, blockSize, borderSize, playerPosition):
        new_x_pos, new_y_pos = getRandomCoord(gameWidth, gameHeight, blockSize, borderSize)

        if [new_x_pos, new_y_pos] not in playerPosition:
            self.pos_x = new_x_pos
            self.pos_y = new_y_pos
            return new_x_pos, new_y_pos
        else:
            self.createNewCoord(gameWidth, gameHeight, blockSize, borderSize, playerPosition)

    def render(self, game):
        game.screen.blit(self.image, (self.pos_x, self.pos_y))
        updateScreen()
