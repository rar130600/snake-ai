import collections
import math
import random
from operator import add

import numpy as np
import pandas as pd
from keras.layers.core import Dense
from keras.models import Sequential
from keras.optimizers import Adam
from keras.utils import to_categorical

from Game.Player import Direction


# os.environ['CUDA_VISIBLE_DEVICES'] = '-1'


# Action:
#   [1, 0, 0] - продолжать движение по направлению
#   [0, 1, 0] - повернуть направо
#   [0, 0, 1] - повернуть налево

def checkRight(player, game):
    return (list(map(add, player.position[-1], [player.pos_change, 0])) in player.position) or (  # либо справа игрок
            player.position[-1][0] + player.pos_change > game.border_size + (
            (math.floor(game.width / game.block_size) - 1) * game.block_size))  # либо справа стена


def checkLeft(player, game):
    return (list(map(add, player.position[-1], [-player.pos_change, 0])) in player.position) or (  # либо слева игрок
            player.position[-1][0] - player.pos_change < game.border_size)  # либо слева стена


def checkUp(player, game):
    return (list(map(add, player.position[-1], [0, -player.pos_change])) in player.position) or (  # либо сверху игрок
            player.position[-1][-1] - player.pos_change < game.border_size)  # либо сверху стена


def checkDown(player, game):
    return (list(map(add, player.position[-1], [0, player.pos_change])) in player.position) or (  # либо снизу игрок
            player.position[-1][-1] + player.pos_change > game.border_size + (  # либо снизу стена
            (math.floor(game.height / game.block_size) - 1) * game.block_size))


def getTailDirection(player):
    if len(player.position) <= 2:
        return player.direction
    else:
        if player.position[0][0] < player.position[1][0]:
            return Direction.RIGHT
        elif player.position[0][0] > player.position[1][0]:
            return Direction.LEFT
        elif player.position[0][1] > player.position[1][1]:
            return Direction.UP
        else:
            return Direction.DOWN


class DQNAgent:
    def __init__(self, config):
        self.reward = 0
        self.gamma = 0.9
        self.data_frame = pd.DataFrame()
        self.agent_target = 1
        self.agent_predict = 0
        self.learning_rate = config['LEARNING_RATE']
        self.epsilon = 1  # нужен для включения случайных ходов
        self.epsilon_decay_linear = config['EPSILON_DECAY_LINEAR']
        self.is_train = config['TRAIN']
        self.actual = []
        self.layer_1 = config['LAYER_1_SIZE']
        self.layer_2 = config['LAYER_2_SIZE']
        self.layer_3 = config['LAYER_3_SIZE']
        self.memory = collections.deque(maxlen=config['MEMORY_SIZE'])
        self.batch_size = config['BATCH_SIZE']
        self.weights_path = config['WEIGHTS_PATH']
        self.load_weights = config['LOAD_WEIGHTS']
        self.model = self.createNetwork()

    def createNetwork(self):
        model = Sequential()
        model.add(Dense(units=self.layer_1, activation='relu', input_shape=(15,)))
        model.add(Dense(units=self.layer_2, activation='relu'))
        model.add(Dense(units=self.layer_3, activation='relu'))
        model.add(Dense(units=3, activation='linear'))
        adam = Adam(self.learning_rate)
        model.compile(loss='mse', optimizer=adam)

        if self.load_weights and self.weights_path:
            model.load_weights(self.weights_path)
            print("DQNAgent: weights loaded")

        return model

    def getState(self, game, player, food):
        tail_direction = getTailDirection(player)
        state = [
            # опасность по направлению движения
            (player.direction == Direction.RIGHT and (checkRight(player, game)))  # сейчас двигаемся вправо
            or (player.direction == Direction.LEFT and (checkLeft(player, game)))  # сейчас двигаемся влево
            or (player.direction == Direction.UP and (checkUp(player, game)))  # сейчас двигаемся верх
            or (player.direction == Direction.DOWN and (checkDown(player, game))),  # сейчас двигаемся вниз

            # опасность справа
            (player.direction == Direction.UP and (checkRight(player, game)))  # сейчас двигаемся вверх
            or (player.direction == Direction.DOWN and (checkLeft(player, game)))  # сейчас двигаемся вниз
            or (player.direction == Direction.LEFT and (checkUp(player, game)))  # сейчас двигаемся влево
            or (player.direction == Direction.RIGHT and (checkDown(player, game))),  # сейчас двигаемся вправо

            # опасность слева
            (player.direction == Direction.DOWN and (checkRight(player, game)))  # сейчас двигаемся вверх
            or (player.direction == Direction.UP and (checkLeft(player, game)))  # сейчас двигаемся вниз
            or (player.direction == Direction.RIGHT and (checkUp(player, game)))  # сейчас двигаемся влево
            or (player.direction == Direction.LEFT and (checkDown(player, game))),  # сейчас двигаемся вправо

            # направление хвоста
            tail_direction == Direction.LEFT,
            tail_direction == Direction.RIGHT,
            tail_direction == Direction.UP,
            tail_direction == Direction.DOWN,

            player.direction == Direction.LEFT,  # движение влево
            player.direction == Direction.RIGHT,  # движение вправо
            player.direction == Direction.UP,  # движение вверх
            player.direction == Direction.DOWN,  # движение вниз

            food.pos_x < player.pos_x,  # еда находится слева от головы змеи
            food.pos_x > player.pos_x,  # еда находится справа
            food.pos_y < player.pos_y,  # еда находится выше
            food.pos_y > player.pos_y,  # еда находится ниже
        ]

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, nextState, gameOver):
        self.memory.append((state, action, reward, nextState, gameOver))

    def getReward(self, playerIsEaten, gameOver, gameWin):
        self.reward = 0

        if gameOver and not gameWin:
            self.reward = -10
        elif gameOver and gameWin:
            self.reward = 100
            return self.reward
        elif playerIsEaten:
            self.reward = 10

        return self.reward

    def trainMemoryLong(self):
        if len(self.memory) > self.batch_size:
            mini_sample = random.sample(self.memory, self.batch_size)
        else:
            mini_sample = self.memory

        for state, action, reward, next_state, game_over in mini_sample:
            prediction_new_Q = reward
            if not game_over:
                prediction_new_Q = reward + self.gamma * np.amax(self.model.predict(np.array([next_state]))[0])
            prediction_Q = self.model.predict(np.array([state]))
            prediction_Q[0][np.argmax(action)] = prediction_new_Q
            self.model.fit(np.array([state]), prediction_Q, epochs=1, verbose=0)

    def trainMemoryShort(self, state, action, reward, nextState, gameOver):
        prediction_new_Q = reward

        if not gameOver:
            prediction_new_Q = reward + self.gamma * np.amax(self.model.predict(nextState.reshape((1, 15)))[0])

        prediction_Q = self.model.predict(state.reshape((1, 15)))
        prediction_Q[0][np.argmax(action)] = prediction_new_Q
        self.model.fit(state.reshape((1, 15)), prediction_Q, epochs=1, verbose=0)

    def getAction(self, state, gameCounter):
        if not self.is_train:
            self.epsilon = 0.0
        else:
            # epsilon необходим для внесения случайности действия
            self.epsilon = 1 - (gameCounter * self.epsilon_decay_linear)

        if random.uniform(0, 1) < self.epsilon:
            # выполняем случайное действие
            move = np.array(to_categorical(random.randint(0, 2), num_classes=3), dtype=int)
        else:
            # выполняем действие, предсказанное по состоянию
            prediction = self.model.predict(state.reshape((1, 15)))
            move = np.array(to_categorical(np.argmax(prediction[0]), num_classes=3), dtype=int)

        return move

    def getNewPlayerDirectionFromAction(self, player, action):
        direction_clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        index = direction_clock_wise.index(player.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_direction = direction_clock_wise[index]  # не изменяем направление
        elif np.array_equal(action, [0, 1, 0]):
            new_direction_index = (index + 1) % 4
            new_direction = direction_clock_wise[new_direction_index]  # поворот направо по часовой стрелки
        else:
            new_direction_index = (index - 1) % 4
            new_direction = direction_clock_wise[new_direction_index]  # поворот налево против часовой стрелки

        return new_direction
