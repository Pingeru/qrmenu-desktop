import sys

from PyQt5.QtWidgets import QApplication

from view.main_window import Main_Window


def main():
    app = QApplication(sys.argv)
    window = Main_Window()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
