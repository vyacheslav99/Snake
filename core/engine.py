import random

FIELD_TYPE_NONE = 0
FIELD_TYPE_EATS = 1
FIELD_TYPE_HEAD = 2
FIELD_TYPE_BODY = 3


class StopGameException(Exception):
    pass


class Engine(object):

    EATS_RAISE_INTERVAL = 10

    def __init__(self, box_width, box_height):
        self.__width = box_width
        self.__height = box_height
        self.__locked = False
        self.__eaten = 0


        # кол-во шагов до появления еды
        self.__to_rise = 0

        # матрица игрового поля, содержит тип фигуры в заданной точке
        self.__terrarium = []

        # координаты головы змеи
        self.__headRow = 0
        self.__headCol = 0

        # набор координат точек, при прохождении через которые, меняется направление движения, и собственно
        # флаги изменения направления
        self.__direct_points = {}

        # змейка, массив смещений координат, позволяющих вычислить следующее положение элемента на поле (top, left)
        self.__snake = []

    def start(self):
        if not self.__snake:
            self.__to_rise = self.EATS_RAISE_INTERVAL
            self.__snake = [[1, 0]]
            self.__headRow = 0
            self.__headCol = self.__width // 2
            self.__terrarium[self.__headRow][self.__headCol] = FIELD_TYPE_HEAD

    def clear(self):
        self.__locked = False
        self.__eaten = 0
        self.__snake = []
        self.__direct_points = {}
        self.__terrarium = [[FIELD_TYPE_NONE for col in range(self.__width)] for row in range(self.__height)]

    def cell(self, top, left):
        return self.__terrarium[top][left]

    def eaten(self):
        return self.__eaten

    def length(self):
        return len(self.__snake)

    def move(self):
        """ переместиться на шаг вперед """
        self.__try_move()

    def turn_right(self):
        """ повернуть вправо """
        self.__change_direction(0, 1)

    def turn_left(self):
        """ повернуть влево """
        self.__change_direction(0, -1)

    def turn_up(self):
        """ провернуть вверх """
        self.__change_direction(-1, 0)

    def turn_down(self):
        """ повернуть вниз """
        self.__change_direction(1, 0)

    def __calc_pos(self, top, left):
        """ вычисляет реальные координаты всех точек змейки на поле от заданной точки по смещениям координат """
        pass
        # return [[centerTop + offset[0], centerLeft + offset[1]] for offset in self.__snake]

    def __check_pos(self, pos):
        """ Проверяет, свободны ли на доске точки с заданными координатами """
        for coord in pos:
            if coord[0] < 0 or coord[0] >= self.__height or coord[1] < 0 or coord[1] >= self.__width \
                or self.__terrarium[coord[0]][coord[1]] > 1:
                return False

        return True

    def __change_direction(self, top, left):
        """ изменяет направление движения в заданной точке"""
        pass

    def __try_move(self):
        """ Центральный метод игры, обработка шага игры """

        try:
            while self.__locked:
                pass

            #todo: не забыть тут же сделать появление еды через каждые n шагов
            self.__locked = True
        finally:
            self.__locked = False
