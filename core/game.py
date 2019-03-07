import random
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QFrame
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QIcon

from . import engine


class Tetris(QMainWindow):

    def __init__(self, app):
        super().__init__()

        self.app = app
        self.box = GameBox(self)
        self.setCentralWidget(self.box)
        self.setWindowIcon(QIcon('app.ico'))
        self.setWindowTitle('Удавчик')

        self.statusbar = self.statusBar()
        self.box.msg2Statusbar[str].connect(self.statusbar.showMessage)

        self.resize(380, 385)
        self.center()
        self.show()

        self.box.start()

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)


class GameBox(QFrame):

    msg2Statusbar = pyqtSignal(str)
    InitialSpeed = 1000
    AccInterval = 2000 * 60
    Accelerator = 0.9
    BoxWidth = 20
    BoxHeight = 20

    def __init__(self, parent):
        super().__init__(parent)

        self.speed = self.InitialSpeed
        self.isStarted = False
        self.isPaused = False
        self.engine = engine.Engine(GameBox.BoxWidth, GameBox.BoxHeight)
        self.timer = QBasicTimer()
        self.acc_timer = QBasicTimer()
        self.setFocusPolicy(Qt.StrongFocus)

    def start(self):
        if self.isStarted:
            self.stop()

        self.engine.clear()
        self.msg2Statusbar.emit(f'Размер: {self.engine.length()}')
        self.isPaused = False
        self.isStarted = True
        self.speed = self.InitialSpeed
        self.engine.start()
        self.timer.start(self.speed, self)
        self.acc_timer.start(self.AccInterval, self)
        self.update()

    def stop(self, message='Кабздец!'):
        if not self.isStarted:
            return

        self.timer.stop()
        self.acc_timer.stop()
        self.isStarted = False
        self.isPaused = False
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
                self.parent().app.quit()

            if key == Qt.Key_S:
                self.start()

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

            else:
                super(GameBox, self).keyPressEvent(event)
        except engine.StopGameException as e:
            self.stop(str(e))
        finally:
            self.update_ui()

    def timerEvent(self, event):
        try:
            if event.timerId() == self.timer.timerId():
                self.engine.move()
            elif event.timerId() == self.acc_timer.timerId():
                self.speed *= self.Accelerator
                if not self.isPaused:
                    self.timer.stop()
                    self.timer.start(self.speed, self)
            else:
                super(GameBox, self).timerEvent(event)
        except engine.StopGameException as e:
            self.stop(str(e))
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
        colors = {
            engine.FIELD_TYPE_NONE: 0xECE9D8,
            engine.FIELD_TYPE_EATS1: 0xFF4500,
            engine.FIELD_TYPE_EATS2: 0xEEEE00,
            engine.FIELD_TYPE_EATS3: 0x00CDCD,
            engine.FIELD_TYPE_EATS4: 0x0000CD,
            engine.FIELD_TYPE_EATS5: 0xCD0000,
            engine.FIELD_TYPE_HEAD: 0x008B00,
            engine.FIELD_TYPE_BODY: 0x66CD00,
            engine.FIELD_TYPE_HOLE: 0x171717,
            engine.FIELD_TYPE_ROCK: 0x5E6965
        }

        w = left * self.scale_width()
        h = top * self.scale_height()

        painter = QPainter(self)
        color = QColor(colors[sq_type])

        if sq_type == engine.FIELD_TYPE_NONE:
            painter.fillRect(w, h, self.scale_width(), self.scale_height(), color)
            return
        elif sq_type == engine.FIELD_TYPE_BODY:
            coef = self.engine.body_index(top, left) * 10
            color.setGreen(color.green() + coef)

        painter.fillRect(w + 1, h + 1, self.scale_width() - 2, self.scale_height() - 2, color)

        painter.setPen(color.lighter())
        painter.drawLine(w, h + self.scale_height() - 1, w, h)
        painter.drawLine(w, h, w + self.scale_width() - 1, h)

        painter.setPen(color.darker(150))
        painter.drawLine(w + 1, h + self.scale_height() - 1, w + self.scale_width() - 1, h + self.scale_height() - 1)
        painter.drawLine(w + self.scale_width() - 1, h + self.scale_height() - 1, w + self.scale_width() - 1, h + 1)
