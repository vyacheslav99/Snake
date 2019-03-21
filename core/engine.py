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

AREA_TYPES = {
    FIELD_GROUP_EMPTY: (FIELD_TYPE_NONE,),
    FIELD_GROUP_BOA: (FIELD_TYPE_HEAD, FIELD_TYPE_BODY),
    FIELD_GROUP_EATS: (FIELD_TYPE_EATS1, FIELD_TYPE_EATS2, FIELD_TYPE_EATS3, FIELD_TYPE_EATS4, FIELD_TYPE_EATS5),
    FIELD_GROUP_BARRIER: (FIELD_TYPE_HOLE, FIELD_TYPE_ROCK)
}

DEATH_TYPES = AREA_TYPES[FIELD_GROUP_BOA] + AREA_TYPES[FIELD_GROUP_BARRIER]

ARRANGE_HELIX = 0
ARRANGE_ZIGZAG = 1
ARRANGE_TYPES = (ARRANGE_HELIX, ARRANGE_ZIGZAG)


class StopGameException(Exception):
    pass


class Engine(object):

    EATS_RAISE_INTERVAL = 15

    def __init__(self, box_width, box_height, boa_size=None, arrange_mech=None):
        self._width = box_width
        self._height = box_height
        self._locked = False
        self._initial_boa_size = boa_size or 2
        self._arrange_mech = arrange_mech or ARRANGE_HELIX

        if self._initial_boa_size >= self._height * self._width:
            raise Exception(f'Задан стартовый размер удавчика ({self._initial_boa_size}), '
                            f'равный или превышающий количество клеток поля ({self._height * self._width})!')

        if self._initial_boa_size < 1:
            raise Exception(f'Задан слишком маленький стартовый размер удавчика: {self._initial_boa_size}!')

        if self._arrange_mech not in ARRANGE_TYPES:
            raise Exception(f'Задан неверный тип расположения удавчика на поле: {self._arrange_mech}! '
                            'Возможные значения: 0 - 2')

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

            if self._arrange_mech == ARRANGE_ZIGZAG:
                self._arrange_zigzag()
            # elif self._arrange_mech == ARRANGE_HELIX:
            #     self._arrange_helix()
            else:
                self._arrange_helix()

            # на старте препятствия накидывать не будем, т.к. под конец они делают прохождение невозможным
            # if len(self._boa) < (self._width + self._height) * 2:
            #     self.create_barriers()

            self._add_eat()

    def clear(self):
        self._initial_boa_size = 2
        self._locked = False
        self._boa = []
        self._boa_moves = []
        self._direct_points = {}
        self._area = [[FIELD_TYPE_NONE for col in range(self._width)] for row in range(self._height)]

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

    def create_barriers(self):
        """ накидывает на поле несколько случайных препятствий """

        while self._locked:
            pass

        try:
            self._locked = True
            for _ in range(random.randint(0, self._width * self._height / 100)):
                top, left = self._rand_coord(FIELD_GROUP_BARRIER)

                if top is None or left is None:
                    return

                of_top = random.choice((-1, 0, 1))
                of_left = random.choice((-1, 0, 1))
                el_type = random.choice(AREA_TYPES[FIELD_GROUP_BARRIER])

                for i in range(random.randint(1, 6)):
                    if i == 0:
                        self._area[top][left] = el_type
                    else:
                        t, l = top + of_top * i, left + of_left * i
                        if self._check_pos(t, l):
                            self._area[t][l] = el_type
        finally:
            self._locked = False

    def remove_barriers(self):
        """ убирает с поля все препятствия """

        while self._locked:
            pass

        try:
            self._locked = True
            for i in range(len(self._area)):
                for j in range(len(self._area[i])):
                    if self._area[i][j] in AREA_TYPES[FIELD_GROUP_BARRIER]:
                        self._area[i][j] = FIELD_TYPE_NONE
        finally:
            self._locked = False

    def cell(self, top, left):
        return self._area[top][left]

    def body_index(self, top, left):
        try:
            return self._boa.index([top, left]) - 1
        except Exception:
            return 0

    def print_debug_info(self):
        print('-= Core parameters =-')
        print(f'Dimensions:  Height: {self._height} Width: {self._width} Area: {self._width * self._height}')
        print(f'Start boa size: {self._initial_boa_size}')
        print(f'Current boa size: {len(self._boa)}')
        print(f'Arrange method: {self._arrange_mech}')
        print(f'Head position:  Top: {self._boa[0][0]} Left: {self._boa[0][1]}')
        print(f'Head direction:  Top: {self._boa_moves[0][0]} Left: {self._boa_moves[0][1]}')

    def _reflect_boa_on_area(self):
        for i, coord in enumerate(self._boa):
            self._area[coord[0]][coord[1]] = FIELD_TYPE_HEAD if i == 0 else FIELD_TYPE_BODY

    def _helix_back(self, center_top, center_left):
        direct = 1  # 0 - слева-направо, 1 - снизу-вверх, 2 - справа-налево, 3 - сверху-вниз
        part_len = 1
        top, left = center_top, center_left + 1
        of_top, of_left = -1, 0
        n = 0
        dp = [-1, 0]

        while len(self._boa) < self._initial_boa_size:
            n += 1
            self._boa.append([top, left])
            self._boa_moves.append([of_top, of_left])

            if dp:
                self._direct_points[(top, left)] = dp
                dp = None

            if direct == 0:
                # слева-направо
                left += 1
                of_top, of_left = 0, 1

                if n == part_len:
                    n = 0
                    direct = 1
                    dp = [-1, 0]
            elif direct == 1:
                # снизу-вверх
                top -= 1
                of_top, of_left = -1, 0

                if n == part_len:
                    n = 0
                    part_len += 2
                    direct = 2
                    dp = [0, -1]
            elif direct == 2:
                # справа-налево
                left -= 1
                of_top, of_left = 0, -1

                if n == part_len:
                    n = 0
                    direct = 3
                    dp = [1, 0]
            elif direct == 3:
                # сверху-вниз
                top += 1
                of_top, of_left = 1, 0

                if n == part_len:
                    n = 0
                    part_len += 2
                    direct = 0
                    dp = [0, 1]

    def _arrange_helix(self):
        direct = 0  # 0 - слева-направо, 1 - сверху-вниз, 2 - справа-налево, 3 - снизу-вверх
        min_top, min_left = 2, 0
        max_top = self._height - 1
        max_left = self._width - 1
        top, left = 0, 0
        of_top, of_left = 0, 1
        dp = None

        while len(self._boa) < self._initial_boa_size:
            self._boa.append([top, left])
            self._boa_moves.append([of_top, of_left])

            if top == self._height // 2 and left == self._width // 2 - 1:
                # мы попали в центр, надо разворачиваться и двигать в обратном направлении
                self._helix_back(top, left)
                break

            if dp:
                self._direct_points[(top, left)] = dp
                dp = None

            if direct == 0:
                # слева-направо
                left += 1
                of_top, of_left = 0, 1

                if left >= max_left:
                    direct = 1
                    max_left -= 2
                    dp = [1, 0]
            elif direct == 1:
                # сверху-вниз
                top += 1
                of_top, of_left = 1, 0

                if top >= max_top:
                    direct = 2
                    max_top -= 2
                    dp = [0, -1]
            elif direct == 2:
                # справа-налево
                left -= 1
                of_top, of_left = 0, -1

                if left <= min_left:
                    direct = 3
                    min_left += 2
                    dp = [-1, 0]
            elif direct == 3:
                # снизу-вверх
                top -= 1
                of_top, of_left = -1, 0

                if top <= min_top:
                    direct = 0
                    min_top += 2
                    dp = [0, 1]

        self._boa.reverse()
        self._boa_moves.reverse()
        self._reflect_boa_on_area()

    def _zigzag_back(self, head_top, head_left):
        left = head_left - 1
        top = head_top

        self._boa.append([top, left])
        self._boa_moves.append([0, -1])
        self._direct_points[(top, left)] = [-1, 0]

        while len(self._boa) < self._initial_boa_size:
            top -= 1
            self._boa.append([top, left])
            self._boa_moves.append([-1, 0])

    def _arrange_zigzag(self):
        direct = 1  # 1 - слева-направо, -1 - справа-налево
        top, left = 0, 0
        min_left = 0
        f = False

        while len(self._boa) < self._initial_boa_size:
            self._boa.append([top, left])
            self._boa_moves.append([0, direct])
            left += direct

            if left == min_left or left == self._width - 1:
                min_left = 1
                direct *= -1
                self._boa.append([top, left])

                if top == self._height - 1:
                    self._boa_moves.append([0, -1])
                    self._zigzag_back(top, left)
                    break
                else:
                    self._boa_moves.append([1, 0])
                    self._direct_points[(top, left)] = [1, 0]
                    top += 1
                    self._direct_points[(top, left)] = [0, direct]

        self._boa.reverse()
        self._boa_moves.reverse()
        self._reflect_boa_on_area()

    def _add_eat(self):
        top, left = self._rand_coord(FIELD_GROUP_EATS)

        if top is None or left is None:
            return

        self._area[top][left] = random.choice(AREA_TYPES[FIELD_GROUP_EATS])

    def _check_pos(self, top, left):
        """ Проверяет, свободны ли на доске точки с заданными координатами """
        if top < 0 or top >= self._height or left < 0 or left >= self._width or self._area[top][left] in DEATH_TYPES:
            return False

        return True

    def _check_pos_raise(self, top, left, barriers_only=False):
        if top < 0 or top >= self._height or left < 0 or left >= self._width:
            raise StopGameException('Удавчик убился об стену!')
        if not barriers_only and self._area[top][left] == FIELD_TYPE_BODY:
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
        if [horiz * -1, vert * -1] == self._boa_moves[0]:
            # исключим вариант поворота на 180% (т.е. внутрь себя)
            return

        self._direct_points[tuple(self._boa[0])] = [horiz, vert]

    def _rand_coord(self, cell_type_group):
        coords = tuple((t, l) for t in range(self._width) for l in range(self._height)
                       if self._check_pos(t, l) and self._area[t][l] not in AREA_TYPES[cell_type_group])

        if not coords:
            return None, None

        res = random.choice(coords)
        return res[0], res[1]

    def _check_to_win(self):
        for top in range(self._width):
            for left in range(self._height):
                if self._area[top][left] in AREA_TYPES[FIELD_GROUP_EMPTY] + AREA_TYPES[FIELD_GROUP_EATS]:
                    return False

        return True

    def _try_move(self):
        """ Центральный метод игры, обработка шага игры """
        try:
            while self._locked:
                pass

            # проверить, вдруг победил
            if self._check_to_win():
                raise StopGameException('Ура! Победа!')

            self._locked = True
            last = copy.copy(self._boa[len(self._boa)-1])

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
                    self._check_pos_raise(*self._boa[i], barriers_only=True)

            # если в новом месте жратва - надо удлинить хвост
            if self._area[self._boa[0][0]][self._boa[0][1]] in AREA_TYPES[FIELD_GROUP_EATS]:
                self._boa.append(last)
                self._boa_moves.append(copy.copy(self._boa_moves[len(self._boa_moves)-1]))
            else:
                self._area[last[0]][last[1]] = FIELD_TYPE_NONE

            self._reflect_boa_on_area()
            self._check_pos_raise(*self._boa[0])

            # появление еды через каждые n шагов
            self._to_rise -= 1

            if self._to_rise <= 0:
                self._to_rise = self.EATS_RAISE_INTERVAL
                self._add_eat()
        finally:
            self._locked = False
