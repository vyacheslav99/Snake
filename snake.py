import sys
import argparse
from PyQt5.QtWidgets import QApplication

from core import game


def main():
    ap = argparse.ArgumentParser()

    ap.add_argument('-s', '--speed', type=int,
                    help='Установить начальную скорость игры (1 шаг в заданный промежуток времени, в мс). '
                         'По умолчанию 800 мс')
    ap.add_argument('-l', '--length', type=int, help='Установить начальный размер удавчика. По умолчанию 2 клетки')
    ap.add_argument('-a', '--arrange_mech', type=int,
                    help='Способ расположения нового удава на поле при старте игры: '
                         '0 - спираль (улитка), 1 - зигзаг. По умолчанию 0')
    ap.add_argument('-f', '--no_freeze', action='store_true', help='Наращивать скорость')
    args = ap.parse_args()

    app = QApplication(sys.argv)
    snake = game.Snake(app, speed=args.speed, length=args.length, arrange_mech=args.arrange_mech,
                       freeze=not args.no_freeze)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
