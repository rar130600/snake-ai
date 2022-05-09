import numpy as np
import pygame
import seaborn as sns
from DQNAgent import DQNAgent
from Game.Game import Game
from Game.Player import Direction
from Game.config import createConfig
from Game.utils import render, getMeanAndStdev
from matplotlib import pyplot as plt


def initAIGame(game, player, food, agent):
    state_old = agent.getState(game, player, food)
    action = [1, 0, 0]
    direction = agent.getNewPlayerDirectionFromAction(player, action)
    player_is_eaten = player.move(direction, game, food)
    state_new = agent.getState(game, player, food)
    reward = agent.getReward(player_is_eaten, game.game_over, game.game_win)
    agent.remember(state_old, action, reward, state_new, game.game_over)
    agent.trainMemoryLong()


def test(configObject):
    configObject['LOAD_WEIGHTS'] = True
    configObject['TRAIN'] = False
    run(configObject)


def drawPlot(plotCounter, plotScore, isTrain):
    sns.set(color_codes=True, font_scale=1.5)
    sns.set_style("white")
    plt.figure(figsize=(13, 8))
    fit_reg = True
    if not isTrain:
        fit_reg = False
    ax = sns.regplot(
        np.array([plotCounter])[0],
        np.array([plotScore])[0],
        # color="#36688D",
        x_jitter=.1,
        scatter_kws={ "color": "#36688D" },
        label='Data',
        fit_reg=fit_reg,
        line_kws={ "color": "#F49F05" }
    )
    # Plot the average line
    y_mean = [np.mean(plotScore)] * len(plotCounter)
    ax.plot(plotCounter, y_mean, label='Mean', linestyle='--')
    ax.legend(loc='upper right')
    ax.set(xlabel='Номер игры', ylabel='Количество набранных очков')
    plt.ylim(0, 65)
    plt.show()


def run(configObject):
    pygame.init()
    agent = DQNAgent(configObject)
    best_score = 0
    total_score = 0
    game_counter = 0
    plot_score = []
    plot_counter = []

    while game_counter < configObject['EPISODES']:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # инициализация классов
        game = Game(configObject)
        player = game.player
        food = game.food

        if configObject['IS_AI']:
            # initAIGame(game, player, food, agent)
            print()
        else:
            player.direction = Direction.NOPE

        if configObject['DISPLAY']:
            render(game, player, food, best_score)
            
        print('GAME OVER BEFORE = ', game.game_over)

        while not game.game_over:  # and (emptySteps < config['AVAILABLE_EMPTY_STEPS']):
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

            if best_score < game.score:
                best_score = game.score

            if configObject['DISPLAY']:
                render(game, player, food, best_score)
                pygame.time.wait(configObject['SPEED'])

        print('GAME OVER AFTER = ', game.game_over)

        if configObject['TRAIN']:
            agent.trainMemoryLong()

        game_counter += 1
        total_score += game.score
        print(f'Game {game_counter},    Score: {game.score}')
        plot_score.append(game.score)
        plot_counter.append(game_counter)

    mean, stdev = getMeanAndStdev(plot_score)
    if configObject['TRAIN'] and configObject['WEIGHTS_PATH']:
        agent.model.save_weights(configObject['WEIGHTS_PATH'])
        test(configObject)

    if configObject['PLOT_SCORE']:
        drawPlot(plot_counter, plot_score, configObject['TRAIN'])

    print(f'Total Score = {total_score}, Mean = {mean}, Stdev = {stdev}')


if __name__ == '__main__':
    pygame.font.init()
    config = createConfig()
    run(config)
