import os, sys
import random
import json
import pickle
import datetime
import copy
from colour import Color

from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QFrame, QMessageBox
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QIcon

from . import engine, utils


class Snake(QMainWindow):

    def __init__(self, app, speed=None, length=None, arrange_mech=None, freeze=True):
        super().__init__()

        self.app = app
        self.box = GameBox(self, speed=speed, length=length, arrange_mech=arrange_mech, freeze=freeze)
        self.setCentralWidget(self.box)
        self.setWindowIcon(QIcon('app.ico'))
        self.setWindowTitle('Удавчик')

        self.statusbar = self.statusBar()
        self.box.msg2Statusbar[str].connect(self.statusbar.showMessage)

        self.resize(380, 385)
        self.center()
        self.show()

        self.box.start(self.box.load())

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)

    def closeEvent(self, event):
        self.box.save()
        super(Snake, self).closeEvent(event)


class GameBox(QFrame):

    msg2Statusbar = pyqtSignal(str)
    InitialSpeed = 800
    AccInterval = 2000 * 60
    Accelerator = 0.9
    BoxWidth = 20
    BoxHeight = 20

    Colors = {
        engine.FIELD_TYPE_NONE: '#ece9d8',
        engine.FIELD_TYPE_EATS1: '#ee7600',
        engine.FIELD_TYPE_EATS2: '#ffff00',
        engine.FIELD_TYPE_EATS3: '#cd1076',
        engine.FIELD_TYPE_EATS4: '#0000cd',
        engine.FIELD_TYPE_EATS5: '#cd0000',
        engine.FIELD_TYPE_HEAD: '#008b00',
        engine.FIELD_TYPE_BODY: ('#7fff00', '#ff1493'),
        engine.FIELD_TYPE_HOLE: '#171717',
        engine.FIELD_TYPE_ROCK: '#5e6965'
    }

    def __init__(self, parent, speed=None, length=None, arrange_mech=None, freeze=True):
        super().__init__(parent)

        self._initial_speed = speed or self.InitialSpeed

        if self._initial_speed <= 0:
            raise Exception(f'Задана неверная начальная скорость: {self._initial_speed}! '
                            'Скорость игры не может быть меньше 1!')

        self.start_time = None
        self.save_file = 'autosave.dat'
        self.freeze_speed = freeze
        self.speed = 0
        self.isStarted = False
        self.isPaused = False
        self._sp_interval = 1
        self.engine = engine.Engine(GameBox.BoxWidth, GameBox.BoxHeight, boa_size=length, arrange_mech=arrange_mech)
        self.timer = QBasicTimer()
        self.acc_timer = QBasicTimer()
        self.spark_timer = QBasicTimer()
        self.setFocusPolicy(Qt.StrongFocus)

    def save(self):
        try:
            fn = os.path.normpath(os.path.join(os.path.split(sys.argv[0])[0], self.save_file))

            if os.path.exists(fn):
                os.unlink(fn)

            if not self.isStarted:
                return

            data = bytes(json.dumps({
                'speed': self.speed,
                'freeze': self.freeze_speed,
                'start_time': self.start_time.timestamp()
            }), 'utf-8')

            obj = pickle.dumps(self.engine)

            with open(fn, 'wb') as f:
                f.write(utils.int_to_bytes(len(data)))
                f.write(data)
                f.write(obj)
        except Exception as e:
            print(f'{e}')

    def load(self):
        try:
            fn = os.path.normpath(os.path.join(os.path.split(sys.argv[0])[0], self.save_file))

            if not os.path.exists(fn):
                return False

            with open(fn, 'rb') as f:
                data_sz = utils.int_from_bytes(f.read(utils.int_size()))
                data = f.read(data_sz).decode('utf-8')
                obj = f.read()

            data = json.loads(data)
            obj = pickle.loads(obj)

            self._initial_speed = data['speed']
            self.freeze_speed = data['freeze']
            self.start_time = datetime.datetime.fromtimestamp(data['start_time']) if 'start_time' in data else None
            self.engine = obj
            return True
        except Exception as e:
            print(f'{e}')
            return False

    def start(self, after_load=False):
        self.spark_timer.stop()

        if self.isStarted:
            self.stop()

        if not after_load:
            self.engine.clear()

        self._sp_alg = random.choice((0, 1))
        self.body_gradient = list(Color(self.Colors[engine.FIELD_TYPE_BODY][0]).range_to(
            Color(self.Colors[engine.FIELD_TYPE_BODY][1]), (self.BoxWidth * self.BoxHeight) - 1))

        self.msg2Statusbar.emit(f'Размер: {self.engine.length()}')
        self.isPaused = False
        self.isStarted = True
        self.speed = self._initial_speed
        self.engine.start()
        self.timer.start(self.speed, self)
        self.acc_timer.start(self.AccInterval, self)

        if not after_load or not self.start_time:
            self.start_time = datetime.datetime.now()

        self.update()

        if after_load:
            self.pause()

    def stop(self, message='Кабздец!'):
        if not self.isStarted:
            return

        self.timer.stop()
        self.acc_timer.stop()
        self.isStarted = False
        self.isPaused = False
        # self._initial_speed = self.InitialSpeed
        # self.freeze_speed = False
        self.msg2Statusbar.emit(f'{message}   Размер: {self.engine.length()}')
        self.update()

    def pause(self):
        if not self.isStarted:
            return

        self.isPaused = not self.isPaused

        if self.isPaused:
            self.timer.stop()
            self.acc_timer.stop()
            self.msg2Statusbar.emit('-= ПАУЗА =-')
            self.update()
        else:
            self.msg2Statusbar.emit(f'Размер: {self.engine.length()}')
            self.timer.start(self.speed, self)
            self.acc_timer.start(self.AccInterval, self)

    def sparkle(self, method):
        if method == 0:
            # win
            c1, c2 = '#ff0000', '#0000ff'
        else:
            # lose
            c1, c2 = '#8b0000', '#ff0000'

        self.body_gradient = list(Color(c1).range_to(Color(c2), self.engine.length()))
        self.spark_timer.start(self._sp_interval, self)

    def sparkle_step(self):
        """ Кое-какие шаги для подготовки к отрисовке мигания """

        if self._sp_alg == 0:
            # случайно: перемешаем массив цветов
            random.shuffle(self.body_gradient)
        elif self._sp_alg == 1:
            # вдоль тела: сдвинем массив цветов назад
            for i in range(len(self.body_gradient)):
                if i < len(self.body_gradient) - 1:
                    self.body_gradient[i] = self.body_gradient[i + 1]
                else:
                    self.body_gradient[i] = self.body_gradient[0]

    def print_debug_info(self):
        self.engine.print_debug_info()

        print('')
        print('-= Game parameters =-')
        print(f'Started: {self.isStarted}')
        print(f'Paused: {self.isPaused}')

        if self.isStarted:
            print(f'Start time: {self.start_time}')
            print(f'Total left time: {datetime.datetime.now() - self.start_time}')

        print(f'Initial speed: {self._initial_speed}')
        print(f'Current speed: {self.speed}')
        print(f'Acceleration coefficient: {self.Accelerator}')
        print(f'Acceleration frozen: {self.freeze_speed}')

        print('')
        print('-= Window =-')
        print(f'Top: {self.parent().geometry().top()}')
        print(f'Left: {self.parent().geometry().left()}')
        print(f'Height: {self.parent().geometry().height()}')
        print(f'Width: {self.parent().geometry().width()}')
        print(f'Area Height: {self.contentsRect().height()}')
        print(f'Area Width: {self.contentsRect().width()}')

    def scale_width(self):
        """ масштабирование - рассчитывает размер стороны квадрата в пикселях по оси X (ширина) """
        return self.contentsRect().width() // self.BoxWidth

    def scale_height(self):
        """ масштабирование - рассчитывает размер стороны квадрата в пикселях по оси Y (высота) """
        return self.contentsRect().height() // self.BoxHeight

    def keyPressEvent(self, event):
        key = event.key()

        try:
            if key == Qt.Key_Escape:
                # self.parent().app.quit()
                self.parent().close()

            if key == Qt.Key_S:
                self.start()

            elif key == Qt.Key_I:
                self.print_debug_info()

            elif key in (Qt.Key_P, Qt.Key_Space):
                self.pause()

            elif not self.isStarted or self.isPaused:
                return

            elif key == Qt.Key_Right:
                self.engine.turn_right()

            elif key == Qt.Key_Left:
                self.engine.turn_left()

            elif key == Qt.Key_Up:
                self.engine.turn_up()

            elif key == Qt.Key_Down:
                self.engine.turn_down()

            elif key == Qt.Key_B:
                self.engine.create_barriers()

            elif key == Qt.Key_C:
                self.engine.remove_barriers()

            else:
                super(GameBox, self).keyPressEvent(event)
        except engine.StopGameException as e:
            self.stop(str(e))
            self.sparkle(e.code)
        finally:
            self.update_ui()

    def timerEvent(self, event):
        try:
            if event.timerId() == self.timer.timerId():
                self.engine.move()
            elif event.timerId() == self.acc_timer.timerId() and not self.freeze_speed:
                self.speed *= self.Accelerator
                if not self.isPaused:
                    self.timer.stop()
                    self.timer.start(self.speed, self)
            elif event.timerId() == self.spark_timer.timerId():
                self.sparkle_step()
                self.update_ui()
            else:
                super(GameBox, self).timerEvent(event)
        except engine.StopGameException as e:
            self.stop(str(e))
            self.sparkle(e.code)
        finally:
            self.update_ui()

    def paintEvent(self, event):
        for i in range(self.BoxHeight):
            for j in range(self.BoxWidth):
                self.draw_square(j, i, self.engine.cell(i, j))

    def update_ui(self):
        if self.isStarted and not self.isPaused:
            self.msg2Statusbar.emit(f'Размер: {self.engine.length()}')
        self.update()

    def draw_square(self, left, top, sq_type):
        """ отрисовка квадратика """

        w = left * self.scale_width()
        h = top * self.scale_height()

        painter = QPainter(self)

        if sq_type == engine.FIELD_TYPE_NONE:
            painter.fillRect(w, h, self.scale_width(), self.scale_height(), QColor(self.Colors[sq_type]))
            return
        elif sq_type == engine.FIELD_TYPE_BODY:
            color = QColor(self.body_gradient[self.engine.body_index(top, left)].get_hex())
        else:
            color = QColor(self.Colors[sq_type])

        painter.fillRect(w + 1, h + 1, self.scale_width() - 2, self.scale_height() - 2, color)

        painter.setPen(color.lighter())
        painter.drawLine(w, h + self.scale_height() - 1, w, h)
        painter.drawLine(w, h, w + self.scale_width() - 1, h)

        painter.setPen(color.darker(150))
        painter.drawLine(w + 1, h + self.scale_height() - 1, w + self.scale_width() - 1, h + self.scale_height() - 1)
        painter.drawLine(w + self.scale_width() - 1, h + self.scale_height() - 1, w + self.scale_width() - 1, h + 1)
