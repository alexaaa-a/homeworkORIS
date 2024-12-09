from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
import sys
from server import Server
import threading


class GraphicServer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.server = Server('127.0.0.1', 8080)
        self.setWindowTitle('Сервер')
        self.setGeometry(100, 100, 600, 400)
        self.setFixedSize(600, 400)

        self.layout = QVBoxLayout()
        self.button = QPushButton("Включить сервер")
        self.button.clicked.connect(self.on_button_click)
        self.layout.addWidget(self.button)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setLayout(self.layout)

    def on_button_click(self):
        threading.Thread(target=self.server.connect, daemon=True).start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GraphicServer()
    window.show()
    sys.exit(app.exec())
