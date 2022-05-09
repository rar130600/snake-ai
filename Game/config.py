COLOR_WHITE = (255, 255, 255)
COLOR_GREEN = (0, 128, 0)
COLOR_LIGHT_ORANGE = (255, 160, 122)
COLOR_BLACK = (51, 51, 51)


def createConfig():
    config = dict()

    # game
    config['GAME_WIDTH'] = 600
    config['GAME_HEIGHT'] = 600
    config['BORDER_SIZE'] = 10
    config['GAME_INFO_HEIGHT'] = 40
    config['BLOCK_SIZE'] = 20
    config['GAME_CAPTION'] = 'Snake Game'
    config['FOOD_IMAGE'] = './images/food.png'
    config['SNAKE_IMAGE_HEAD'] = './images/snakeGreen.png'
    config['SNAKE_IMAGE_TAIL'] = './images/snakeYellow.png'
    config['BACKGROUND_IMAGE'] = './images/background.png'
    config['SPEED'] = 0
    config['DISPLAY'] = True
    config['AVAILABLE_EMPTY_STEPS'] = 100
    config['GAME_OVER_TIME'] = 0
    config['GAME_WIN_TIME'] = 1000

    # AI
    config['IS_AI'] = True
    config['EPSILON_DECAY_LINEAR'] = 1 / 75
    config['LEARNING_RATE'] = 0.0005  # скорость обучения
    config['LAYER_1_SIZE'] = 50  # количество нейронов в первом слое
    config['LAYER_2_SIZE'] = 300  # количество нейронов во втором слое
    config['LAYER_3_SIZE'] = 50  # количество нейронов в третьем слое
    config['EPISODES'] = 100  # количество эпох
    config['MEMORY_SIZE'] = 2500  # количество памяти
    config['BATCH_SIZE'] = 1000  # размер одного пакета
    config['WEIGHTS_PATH'] = 'weights/weights1.hdf5'  # путь до сохраненных весов
    config['LOAD_WEIGHTS'] = False  # загрузить сохраненные веса
    config['TRAIN'] = True  # тренеровать модель
    config['PLOT_SCORE'] = True  # вывод графиков
    return config
