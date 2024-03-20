from PyQt5.QtWidgets import *
from Windows.window import MainWindow
from qt_material import apply_stylesheet
import sys


def run_app():
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        apply_stylesheet(app, theme='dark_lightgreen.xml')
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    run_app()
