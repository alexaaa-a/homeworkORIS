from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QTextEdit, QLineEdit, QMainWindow
import sys
from client import Client
from PyQt6.QtCore import QThread


class RoomLoaderThread(QThread):
    rooms_loaded = pyqtSignal(list)

    def __init__(self, client):
        super().__init__()
        self.client = client

    def run(self):
        try:
            data = self.client.receive_rooms()
            if data is not None:
                rooms = data.get("rooms", [])
                self.rooms_loaded.emit(rooms)
            else:
                self.rooms_loaded.emit([])
        except Exception as e:
            print(f"Ошибка при загрузке комнат: {e}")
            self.rooms_loaded.emit([])


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
        try:
            if not name:
                self.text_edit.append("Имя не может быть пустым!")
                return

            self.client.connect(name)
            self.name_window.close()
            self.client.receive_message(self.handle_msg)

            self.text_edit.append("Вы подключены. Ждём список комнат... \n"
                                  "Список доступных команд: \n"
                                  "/ban <nickname> забанить пользователя \n"
                                  "/change сменить комнату \n"
                                  "/exit покинуть игру")
        except Exception as e:
            self.text_edit.append(f"Ошибка подключения: {e}")

    def on_button_click(self):
        text = self.input_line.text()
        self.input_line.clear()

        if text.startswith('/'):
            self.client.send_command(text[1:])
        else:
            self.client.send_message(text)

    def handle_msg(self, message):
        if message.startswith("rooms:"):
            self.text_edit.append("Загрузка комнат...")
            self.load_rooms_thread = RoomLoaderThread(self.client)
            self.load_rooms_thread.rooms_loaded.connect(self.show_rooms_window)
            self.load_rooms_thread.start()
        elif message.startswith("room_created:"):
            room_name = message[len("room_created:"):]
            self.client.send_data({"type": "command", "data": f"join_room {room_name}"})
            self.text_edit.append(f"Вы создали и подключились к комнате {room_name}.")
        else:
            self.message_received.emit(message)

    def display_message(self, message):
        self.text_edit.append(message)

    def show_rooms_window(self, rooms):
        self.rooms_window = QWidget()
        self.rooms_window.setWindowTitle("Выберите или создайте комнату")
        self.rooms_window.setGeometry(100, 100, 400, 300)
        self.rooms_window.setFixedSize(400, 300)

        layout_rooms = QVBoxLayout()

        if rooms:
            for room in rooms:
                QApplication.processEvents()
                button_room = QPushButton(f"Комната: {room}")
                button_room.clicked.connect(lambda _, r=room: self.on_room_selected(r))
                layout_rooms.addWidget(button_room)

        create_room_button = QPushButton("Создать новую комнату")
        create_room_button.clicked.connect(self.create_room)
        layout_rooms.addWidget(create_room_button)

        self.rooms_window.setLayout(layout_rooms)
        self.rooms_window.show()

    def create_room(self):
        room_name = f"Room_{self.client}_{len(self.client.sock.getpeername())}"
        self.client.send_command(f"create_room {room_name}")
        self.rooms_window.close()

    def on_room_selected(self, room_name):
        self.rooms_window.close()
        self.client.send_data({"type": "command", "data": f"join_room {room_name}"})
        self.text_edit.append(f"Вы присоединились к комнате {room_name}.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GraphicClient()
    window.show()
    sys.exit(app.exec())
