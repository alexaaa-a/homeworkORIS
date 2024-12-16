from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QTextEdit, QLineEdit, QMainWindow, \
    QComboBox
import sys
from client import Client


class GraphicClient(QMainWindow):
    message_received = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.client = Client("127.0.0.1", 8080)

        self.setWindowTitle("Чат")
        self.setGeometry(100, 100, 600, 400)
        self.setFixedSize(650, 450)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.main_layout = QVBoxLayout()

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.main_layout.addWidget(self.text_edit)

        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText('Введите сообщение...')
        self.input_line.returnPressed.connect(self.on_button_click)
        self.main_layout.addWidget(self.input_line)

        self.button_layout = QVBoxLayout()

        self.btn_send = QPushButton("Отправить")
        self.btn_send.clicked.connect(self.on_button_click)
        self.button_layout.addWidget(self.btn_send)

        self.btn_exit = QPushButton("Выйти из игры")
        self.btn_exit.clicked.connect(self.on_exit)
        self.button_layout.addWidget(self.btn_exit)

        self.btn_ban = QPushButton("Забанить игрока")
        self.btn_ban.clicked.connect(lambda: self.client.send_command(f"ban {self.input_line.text()}"))
        self.button_layout.addWidget(self.btn_ban)

        self.btn_change_room = QPushButton("Сменить комнату", self)
        self.btn_change_room.clicked.connect(self.on_room_change)
        self.button_layout.addWidget(self.btn_change_room)

        self.main_layout.addLayout(self.button_layout)
        self.rooms = ['Room1', 'Room2', 'Room3', 'Room4', 'Room5']
        self.rooms_combo_box = QComboBox(self)
        self.rooms_combo_box.addItems(self.rooms)
        self.main_layout.addWidget(self.rooms_combo_box)

        central_widget.setLayout(self.main_layout)

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

    def on_exit(self):
        self.client.send_command("exit")
        self.close()

    @pyqtSlot()
    def on_room_change(self):
        selected_room = self.rooms_combo_box.currentText()
        self.client.send_command(f"change {selected_room}")
        self.text_edit.clear()

    def on_name_input(self, name):
        try:
            if not name:
                self.text_edit.append("Имя не может быть пустым!")
                return

            self.client.connect(name)
            self.name_window.close()
            self.client.receive_message(self.handle_msg)

            self.text_edit.append("Вы подключены.")
        except Exception as e:
            self.text_edit.append(f"Ошибка подключения: {e}")

    @pyqtSlot()
    def on_button_click(self):
        text = self.input_line.text()
        self.input_line.clear()

        if text.startswith('/'):
            self.client.send_command(text[1:])
        else:
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
