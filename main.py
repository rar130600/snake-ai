import pygame
from IPython import display
from matplotlib import pyplot as plt

from DQNAgent import DQNAgent
from Game.Game import Game
from Game.Player import Direction
from Game.config import createConfig
from Game.utils import render, getMeanAndStdev

plt.ion()


def drawPlot(plotCounter, plotScore, plotMean):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.xlabel('Number of Games')
    plt.ylabel('Score')
    plt.plot(plotCounter, plotScore)
    plt.plot(plotCounter, plotMean)
    plt.ylim(ymin=0)
    plt.xlim(xmin=0)
    plt.legend(loc='upper right')
    plt.show(block=False)


def run(configObject):
    pygame.init()
    agent = DQNAgent(configObject)
    best_score = 0
    total_score = 0
    game_counter = 0
    plot_score = []
    plot_counter = []
    plot_mean = []

    best_model_score = []
    best_model_game_number = []

    while game_counter < configObject['EPOCHS']:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # инициализация классов
        game = Game(configObject)
        player = game.player
        food = game.food

        if not configObject['IS_AI']:
            player.direction = Direction.NOPE

        if configObject['DISPLAY']:
            render(game, player, food, best_score)

        new_best_score = best_score
        while not game.game_over:
            if not configObject['IS_AI']:
                direction = player.direction
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        quit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT and (direction != Direction.RIGHT):
                            direction = Direction.LEFT
                        elif event.key == pygame.K_RIGHT and (direction != Direction.LEFT):
                            direction = Direction.RIGHT
                        elif event.key == pygame.K_UP and (direction != Direction.DOWN):
                            direction = Direction.UP
                        elif event.key == pygame.K_DOWN and (direction != Direction.UP):
                            direction = Direction.DOWN
                player.move(direction, game, food)
            else:
                state_old = agent.getState(game, player, food)
                action = agent.getAction(state_old, game_counter)
                direction = agent.getNewPlayerDirectionFromAction(player, action)

                player_is_eaten = player.move(direction, game, food)
                state_new = agent.getState(game, player, food)
                reward = agent.getReward(player_is_eaten, game.game_over, game.game_win)

                if configObject['TRAIN']:
                    # тренеруем короткую память на основе нового состояния и награды
                    agent.trainMemoryShort(state_old, action, reward, state_new, game.game_over)
                    # сохраняем новые данные в долговременной памяти
                    agent.remember(state_old, action, reward, state_new, game.game_over)

            if new_best_score < game.score:
                new_best_score = game.score

            if configObject['DISPLAY']:
                render(game, player, food, new_best_score)
                pygame.time.wait(configObject['SPEED'])

        if configObject['TRAIN']:
            agent.trainMemoryLong()

        if configObject['TRAIN'] and configObject['WEIGHTS_PATH'] and configObject[
            'SAVE_WEIGHTS'] and game.score >= best_score:
            agent.model.save_weights(configObject['WEIGHTS_PATH'])

        if new_best_score > best_score:
            best_model_score.append(new_best_score)
            best_model_game_number.append(game_counter)

        best_score = new_best_score

        game_counter += 1
        total_score += game.score
        print(f'Game {game_counter},    Score: {game.score}')
        plot_score.append(game.score)
        plot_counter.append(game_counter)
        plot_mean.append(total_score / game_counter)

        if config['PLOT_SCORE_EVERY_GAME'] and game_counter > 1:
            drawPlot(plot_counter, plot_score, plot_mean)

    mean, stdev = getMeanAndStdev(plot_score)

    if configObject['PLOT_SCORE']:
        drawPlot(plot_counter, plot_score, plot_mean)

    print(f'Total Score = {total_score}, Mean = {mean}, Stdev = {stdev}')
    print('Best Model score: ', best_model_score)
    print('Best Model game number: ', best_model_game_number)


if __name__ == '__main__':
    pygame.font.init()
    config = createConfig()
    run(config)
