import random
import copy

FIELD_TYPE_NONE = 0
FIELD_TYPE_EATS1 = 1
FIELD_TYPE_EATS2 = 2
FIELD_TYPE_EATS3 = 3
FIELD_TYPE_EATS4 = 4
FIELD_TYPE_EATS5 = 5
FIELD_TYPE_HEAD = 6
FIELD_TYPE_BODY = 7
FIELD_TYPE_HOLE = 8
FIELD_TYPE_ROCK = 9

FIELD_GROUP_EMPTY = 'empty'
FIELD_GROUP_BOA = 'boa'
FIELD_GROUP_EATS = 'eats'
FIELD_GROUP_BARRIER = 'barrier'

AreaTypes = {
    FIELD_GROUP_EMPTY: (FIELD_TYPE_NONE,),
    FIELD_GROUP_BOA: (FIELD_TYPE_HEAD, FIELD_TYPE_BODY),
    FIELD_GROUP_EATS: (FIELD_TYPE_EATS1, FIELD_TYPE_EATS2, FIELD_TYPE_EATS3, FIELD_TYPE_EATS4, FIELD_TYPE_EATS5),
    FIELD_GROUP_BARRIER: (FIELD_TYPE_HOLE, FIELD_TYPE_ROCK)
}

DEATH_TYPES = AreaTypes[FIELD_GROUP_BOA] + AreaTypes[FIELD_GROUP_BARRIER]


class StopGameException(Exception):
    pass


class Engine(object):

    EATS_RAISE_INTERVAL = 15

    def __init__(self, box_width, box_height):
        self._width = box_width
        self._height = box_height
        self._locked = False

        # кол-во шагов до появления еды
        self._to_rise = 0

        # матрица игрового поля, содержит тип фигуры в заданной точке
        self._area = []

        # набор координат точек, при прохождении через которые, меняется направление движения, и собственно
        # флаги изменения направления
        self._direct_points = {}

        # змейка, массив текущих координат на поле (top, left)
        self._boa = []

        # змейка, массив смещений координат относительно соответсвующей точки массива реальных координат,
        # описывает направление движения элемента на поле (top, left)
        self._boa_moves = []

    def start(self):
        if not self._boa:
            self._to_rise = self.EATS_RAISE_INTERVAL
            self._boa = [[1, self._width // 2], [0, self._width // 2]]
            self._boa_moves = [[1, 0], [1, 0]]
            self._area[self._boa[0][0]][self._boa[0][1]] = FIELD_TYPE_HEAD
            self._area[self._boa[1][0]][self._boa[1][1]] = FIELD_TYPE_BODY
            self._create_barriers()
            self._add_eat()

    def clear(self):
        self._locked = False
        self._boa = []
        self._boa_moves = []
        self._direct_points = {}
        self._area = [[FIELD_TYPE_NONE for col in range(self._width)] for row in range(self._height)]

    def cell(self, top, left):
        return self._area[top][left]

    def length(self):
        return len(self._boa)

    def move(self):
        """ переместиться на шаг вперед """
        self._try_move()

    def turn_right(self):
        """ повернуть вправо """
        self._change_direction(0, 1)

    def turn_left(self):
        """ повернуть влево """
        self._change_direction(0, -1)

    def turn_up(self):
        """ провернуть вверх """
        self._change_direction(-1, 0)

    def turn_down(self):
        """ повернуть вниз """
        self._change_direction(1, 0)

    def body_index(self, top, left):
        try:
            return self._boa.index([top, left]) - 1
        except Exception:
            return 0

    def _create_barriers(self):
        """ накидывает на поле несколько случайных препятствий """
        for _ in range(random.randint(0, self._width * self._height / 100)):
            top, left = self._rand_coord(FIELD_GROUP_BARRIER, 0, self._height - 1, 0, self._width - 1)
            of_top = random.choice((-1, 0, 1))
            of_left = random.choice((-1, 0, 1))
            el_type = random.choice(AreaTypes[FIELD_GROUP_BARRIER])

            for i in range(random.randint(1, 8)):
                if i == 0:
                    self._area[top][left] = el_type
                else:
                    t, l = top + of_top * i, left + of_left * i
                    if self._check_pos(t, l):
                        self._area[t][l] = el_type

    def _add_eat(self):
        top, left = self._rand_coord(FIELD_GROUP_EATS, 0, self._height - 1, 0, self._width - 1)
        self._area[top][left] = random.choice(AreaTypes[FIELD_GROUP_EATS])

    def _check_pos(self, top, left):
        """ Проверяет, свободны ли на доске точки с заданными координатами """
        if top < 0 or top >= self._height or left < 0 or left >= self._width or self._area[top][left] in DEATH_TYPES:
            return False

        return True

    def _check_pos_raise(self, top, left):
        if top < 0 or top >= self._height or left < 0 or left >= self._width:
            raise StopGameException('Удавчик убился об стену!')
        if self._area[top][left] == FIELD_TYPE_BODY:
            if self._boa[1] == [top, left]:
                raise StopGameException('Удавчик свернулся внутрь себя!')
            else:
                raise StopGameException('Удавчик съел сам себя!')
        if self._area[top][left] == FIELD_TYPE_HOLE:
            raise StopGameException('Удавчик провалился в дыру!')
        if self._area[top][left] == FIELD_TYPE_ROCK:
            raise StopGameException('Удавчик протаранил скалу!')

    def _change_direction(self, horiz, vert):
        """ изменяет направление движения в заданной точке"""

        # исключим вариант поворота на 180% (т.е. внутрь себя)
        if [horiz * -1, vert * -1] == self._boa_moves[0]:
            return

        self._direct_points[tuple(self._boa[0])] = [horiz, vert]

    def _rand_coord(self, cell_type_group, top_min, top_max, left_min, left_max):
        top = random.randint(top_min, top_max)
        left = random.randint(left_min, left_max)

        while not self._check_pos(top, left) or self._area[top][left] in AreaTypes[cell_type_group]:
            top = random.randint(top_min, top_max)
            left = random.randint(left_min, left_max)

        return top, left

    def _check_to_win(self):
        for top in range(self._width):
            for left in range(self._height):
                if self._area[top][left] in AreaTypes[FIELD_GROUP_EMPTY] + AreaTypes[FIELD_GROUP_EATS]:
                    return False

        return True

    def _try_move(self):
        """ Центральный метод игры, обработка шага игры """
        try:
            while self._locked:
                pass

            self._locked = True
            last = copy.copy(self._boa[len(self._boa)-1])
            prolong = False

            # пробуем переместиться
            for i in range(len(self._boa)):
                # сначала проверим, если тут точка поворота - надо поменять направление движения точки удавчика
                if tuple(self._boa[i]) in self._direct_points:
                    self._boa_moves[i] = copy.copy(self._direct_points[tuple(self._boa[i])])
                    if i == len(self._boa) - 1:
                        # удалить пройденную точку поворота после того, как ее прошел последний элемент
                        self._direct_points.pop(tuple(self._boa[i]))

                # вычисляем новые координаты
                for j in range(len(self._boa[i])):
                    self._boa[i][j] += self._boa_moves[i][j]

                if i == 0:
                    # можно ли занять новую позицию
                    self._check_pos_raise(*self._boa[i])

                    # если в новом месте жратва - надо будет удлинить хвост
                    if self._area[self._boa[i][0]][self._boa[i][1]] in AreaTypes[FIELD_GROUP_EATS]:
                        prolong = True

            if prolong:
                self._boa.append(last)
                self._boa_moves.append(copy.copy(self._boa_moves[len(self._boa_moves)-1]))
            else:
                self._area[last[0]][last[1]] = FIELD_TYPE_NONE

            for i, coord in enumerate(self._boa):
                self._area[coord[0]][coord[1]] = FIELD_TYPE_HEAD if i == 0 else FIELD_TYPE_BODY

            # проверить, вдруг победил
            if self._check_to_win():
                raise StopGameException('Ура! Победа!')

            # появление еды через каждые n шагов
            self._to_rise -= 1

            if self._to_rise <= 0:
                self._to_rise = self.EATS_RAISE_INTERVAL
                self._add_eat()
        finally:
            self._locked = False
