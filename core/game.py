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
        self.setWindowTitle('Snake')

        self.statusbar = self.statusBar()
        self.box.msg2Statusbar[str].connect(self.statusbar.showMessage)

        self.resize(600, 600)
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
    AccInterval = 1000 * 60
    Accelerator = 0.8
    BoxWidth = 30
    BoxHeight = 30

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
        self.msg2Statusbar.emit(f'Lenght: {self.engine.length()}, Eaten: {self.engine.eaten()}')
        self.isPaused = False
        self.isStarted = True
        self.speed = self.InitialSpeed
        self.engine.start()
        self.timer.start(self.speed, self)
        self.acc_timer.start(self.AccInterval, self)
        self.update()

    def stop(self):
        if not self.isStarted:
            return

        self.timer.stop()
        self.acc_timer.stop()
        self.isStarted = False
        self.isPaused = False
        self.msg2Statusbar.emit(f'Game Over!   Lenght: {self.engine.length()}, Eaten: {self.engine.eaten()}')
        self.update()

    def pause(self):
        if not self.isStarted:
            return

        self.isPaused = not self.isPaused

        if self.isPaused:
            self.timer.stop()
            self.acc_timer.stop()
            self.msg2Statusbar.emit('-= PAUSED =-')
            self.update()
        else:
            self.msg2Statusbar.emit(f'Lenght: {self.engine.length()}, Eaten: {self.engine.eaten()}')
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
            self.stop()
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
            self.stop()
        finally:
            self.update_ui()

    def paintEvent(self, event):
        for i in range(self.BoxHeight):
            for j in range(self.BoxWidth):
                self.draw_square(j * self.scale_width(), i * self.scale_height(), self.engine.cell(i, j))

    def update_ui(self):
        if self.isStarted and not self.isPaused:
            self.msg2Statusbar.emit(f'Lenght: {self.engine.length()}, Eaten: {self.engine.eaten()}')
        self.update()

    def draw_square(self, w, h, sq_type):
        """ отрисовка квадратика """
        colors = (0xECE9D8, 0xCD2990, 0x8B1A1A, 0x008B00)
        color_hex = colors[sq_type]
        #todo: сделать расчет градиента для тела и случайного цвета еды

        painter = QPainter(self)
        color = QColor(color_hex)

        if sq_type == 0:
            painter.fillRect(w, h, self.scale_width(), self.scale_height(), color)
            return

        painter.fillRect(w + 1, h + 1, self.scale_width() - 2, self.scale_height() - 2, color)

        painter.setPen(color.lighter())
        painter.drawLine(w, h + self.scale_height() - 1, w, h)
        painter.drawLine(w, h, w + self.scale_width() - 1, h)

        painter.setPen(color.darker())
        painter.drawLine(w + 1, h + self.scale_height() - 1, w + self.scale_width() - 1, h + self.scale_height() - 1)
        painter.drawLine(w + self.scale_width() - 1, h + self.scale_height() - 1, w + self.scale_width() - 1, h + 1)
