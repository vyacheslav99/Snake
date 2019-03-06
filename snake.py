import sys
from PyQt5.QtWidgets import QApplication

from core import game


def main():
    app = QApplication([])
    tetris = game.Tetris(app)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
