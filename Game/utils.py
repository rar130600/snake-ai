import math
import statistics
from random import randint

import pygame.display
from Game.config import COLOR_BLACK, COLOR_WHITE


def getRandomCoord(gameWidth, gameHeight, blockSize, borderSize):
    return borderSize + (randint(0, math.floor(gameWidth / blockSize) - 1) * blockSize), \
           borderSize + (randint(0, math.floor(gameHeight / blockSize) - 1) * blockSize)


def updateScreen():
    pygame.display.update()


def renderUi(game, bestScore):
    my_font = pygame.font.SysFont('Segoe UI', 20)
    my_font_bold = pygame.font.SysFont('Segoe UI', 20, True)

    text_score = my_font.render('SCORE: ', True, COLOR_BLACK)
    text_score_value = my_font.render(str(game.score), True, COLOR_BLACK)
    text_best_score = my_font_bold.render('BEST SCORE: ', True, COLOR_BLACK)
    text_best_score_value = my_font_bold.render(str(bestScore), True, COLOR_BLACK)

    # game.screen.blit(game.background, (0, 0))
    pygame.draw.rect(
        game.screen, COLOR_BLACK,
        pygame.Rect(game.border_size, game.border_size, game.width, game.height)
    )
    game.screen.blit(text_score, (game.border_size, (game.border_size * 2) + game.height + 5))
    game.screen.blit(text_score_value, (game.border_size + 70, (game.border_size * 2) + game.height + 5))
    game.screen.blit(
        text_best_score, ((game.border_size * 2) + game.width - 190, (game.border_size * 2) + game.height + 5)
    )
    game.screen.blit(
        text_best_score_value, ((game.border_size * 2) + game.width - 65, (game.border_size * 2) + game.height + 5)
    )


def render(game, player, food, bestScore):
    game.screen.fill(COLOR_WHITE)
    renderUi(game, bestScore)
    player.render(game)
    food.render(game)


def getMeanAndStdev(array):
    return statistics.mean(array), statistics.stdev(array)
