import sys
import argparse
from PyQt5.QtWidgets import QApplication

from core import game


def main():
    ap = argparse.ArgumentParser()

    ap.add_argument('-d', '--difficulty', type=int, default=2, help='Установить начальную сложность игры (1 - 5)')
    ap.add_argument('-l', '--length', type=int, help='Установить начальный размер удавчика. По умолчанию 2 клетки')
    ap.add_argument('-a', '--arrange_mech', type=int,
                    help='Способ расположения нового удава на поле при старте игры: '
                         '0 - спираль (улитка), 1 - зигзаг. По умолчанию 0')
    args = ap.parse_args()

    app = QApplication(sys.argv)
    snake = game.Snake(app, difficulty=args.difficulty, length=args.length, arrange_mech=args.arrange_mech)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
