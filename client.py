import socket
import threading
from utils import send_pickle, rec_pickle


class Client:
    def __init__(self, host, port):
        self.sock = None
        self.host = host
        self.port = port
        self.isConnected = False

    def connect(self, name):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        send_pickle(self.sock, {"type": "message", "data": name})
        self.isConnected = True

    def send_message(self, message):
        if self.isConnected:
            send_pickle(self.sock, {"type": "message", "data": message})

    def receive_message(self, callback):
        def recv():
            while self.isConnected:
                try:
                    data = rec_pickle(self.sock)
                    if data:
                        callback(data["data"])
                    else:
                        print("Соединение с сервером прервано.")
                        self.isConnected = False
                        break
                except Exception as e:
                    print(f"Ошибка при получении сообщения: {e}")
                    self.isConnected = False
                    break

        recv_thread = threading.Thread(target=recv, daemon=True)
        recv_thread.start()

    def disconnect(self):
        self.sock.close()
        self.isConnected = False

    def send_data(self, data):
        send_pickle(self.sock, data)

    def game_state(self, state):
        print("Состояние игры обновлено!")
        print(f"Использованные города: {state['used_cities']}")
        print(f"Игроки: {state['players']}")
        print(f"Ход игрока: {state['players'][state['turn']]}")

    def send_command(self, command):
        try:
            send_pickle(self.sock, {"type": "command", "data": command})
            print(f"Отправлена команда: {command}")
        except Exception as e:
            print(f"Ошибка отправки команды: {e}")

    def receive_rooms(self):
        send_pickle(self.sock, {"type": "command", "data": "get_rooms"})
        data = rec_pickle(self.sock)
        return data





