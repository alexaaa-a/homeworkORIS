from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QTextEdit, QLineEdit, QMainWindow
import sys
from client import Client


class GraphicClient(QMainWindow):
    message_received = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.client = Client("127.0.0.1", 8080)
        self.setWindowTitle("Чат")
        self.setGeometry(100, 100, 600, 400)
        self.setFixedSize(600, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.layout = QVBoxLayout()

        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText('Введите сообщение...')
        self.input_line.returnPressed.connect(self.on_button_click)

        self.button = QPushButton("Отправить")
        self.button.clicked.connect(self.on_button_click)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)

        self.layout.addWidget(self.text_edit)
        self.layout.addWidget(self.input_line)
        self.layout.addWidget(self.button)

        central_widget.setLayout(self.layout)

        self.message_received.connect(self.display_message)
  
        self.show_name_input_window()

    def show_name_input_window(self):
        self.name_window = QWidget(self)
        self.name_window.setWindowTitle("Введите имя")
        self.name_window.setGeometry(100, 100, 300, 200)
        self.name_window.setFixedSize(300, 200)

        name_input = QLineEdit(self.name_window)
        name_input.setPlaceholderText("Введите ваше имя")
        button_name = QPushButton("Отправить", self.name_window)

        layout_name = QVBoxLayout()
        layout_name.addWidget(name_input)
        layout_name.addWidget(button_name)
        self.name_window.setLayout(layout_name)

        button_name.clicked.connect(lambda: self.on_name_input(name_input.text()))

        self.name_window.show()

    def on_name_input(self, name):
        self.name_window.close()
        self.client.connect(name)
        self.client.receive_message(self.handle_msg)

    def on_button_click(self):
        text = self.input_line.text()
        self.input_line.clear()
        self.client.send_message(text)

    def handle_msg(self, message):
        self.message_received.emit(message)

    def display_message(self, message):
        self.text_edit.append(message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GraphicClient()
    window.show()
    sys.exit(app.exec())
