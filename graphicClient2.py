from PyQt6.QtWidgets import QApplication
import sys
from graphicClient import GraphicClient

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GraphicClient()
    window.show()
    sys.exit(app.exec())