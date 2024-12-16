import socket
import threading
from utils import send_pickle, rec_pickle


class Room:
    def __init__(self, name):
        self.name = name
        self.clients = {}
        self.usedCities = []
        self.turn = 0
        self.isActive = False
        self.banned = set()

    def add_client(self, client, name):
        if client in self.banned:
            send_pickle(client, {'type': 'message', 'data': 'Вы забанены'})
        else:
            self.clients[client] = name

    def remove_client(self, client):
        if client in self.banned:
            send_pickle(client, {'type': 'message', 'data': 'Вы забанены'})
        if client in self.clients:
            del self.clients[client]


class Server:
    def __init__(self, host, port):
        self.sock = None
        self.host = host
        self.port = port
        self.server_active = True
        self.rooms = [Room(f'Room{i}') for i in range(1, 6)]

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind((self.host, self.port))
            self.sock.listen(5)
            print("Сервер запущен. Ожидание подключения...")
        except socket.error as e:
            print(f"Ошибка при запуске сервера: {e}")
            return

        accept_thread = threading.Thread(target=self.accept_incoming_connections)
        accept_thread.start()

    def accept_incoming_connections(self):
        while self.server_active:
            try:
                client, client_address = self.sock.accept()
                print(f"Подключен клиент: {client_address}")
                threading.Thread(target=self.handle_client, args=(client,)).start()
            except Exception as e:
                print(f"Ошибка подключения клиента: {e}")
                break

    def handle_client(self, client):
        try:
            name = rec_pickle(client)["data"]
            if not name:
                send_pickle(client, {"type": "message", "data": "Имя не может быть пустым."})
                client.close()
                return

            send_pickle(client, {"type": "message", "data": "Добро пожаловать! Вы вне комнаты."})
            while True:
                msg = rec_pickle(client)
                if msg["type"] == "command" and msg["data"].startswith("change"):
                    room_name = msg["data"].split()[1]
                    room = self.change_room(client, name, room_name)
                    if len(room.clients) > 2:
                        send_pickle(client, {'type': 'message', 'data': 'Комната переполнена, выберите другую.'})
                        room.remove_client(client)
                        continue
                    send_pickle(client, {"type": "message", "data": f"Вы подключились к {room.name}."})
                    break
        except Exception as e:
            print(f"Ошибка обработки клиента: {e}")

    def change_room(self, client, name, room_name):
        for room in self.rooms:
            if client in room.clients:
                room.remove_client(client)
                self.broadcast(room, f"{name} покинул комнату.")

        for room in self.rooms:
            if room.name == room_name:
                room.add_client(client, name)
                self.broadcast(room, f"{name} присоединился к комнате.")
                if len(room.clients) > 1 and not room.isActive:
                    room.isActive = True
                    threading.Thread(target=self.start_game, args=(room,)).start()
                return room

    def start_game(self, room):
        room.usedCities = []
        room.turn = 0

        while room.isActive:
            clients = list(room.clients.keys())
            current_client = clients[room.turn]
            current_name = room.clients[current_client]

            send_pickle(current_client, {"type": "message", "data": "Ваш ход. Введите город:"})
            msg = rec_pickle(current_client)

            if msg["type"] == "message":
                city = msg["data"]

                if not city:
                    send_pickle(current_client, {"type": "message", "data": "Город не может быть пустым."})
                    continue

                if city in room.usedCities:
                    send_pickle(current_client, {"type": "message", "data": "Этот город уже был. Попробуйте снова."})
                    continue

                if room.usedCities and room.usedCities[-1][-1].lower() != city[0].lower():
                    send_pickle(current_client, {"type": "message", "data": f"Город должен начинаться с буквы '{room.usedCities[-1][-1]}'. Попробуйте снова."})
                    continue

                room.usedCities.append(city)
                self.broadcast(room, f"{current_name} назвал город: {city}")

                room.turn = (room.turn + 1) % len(clients)

            elif msg["type"] == "command" and msg["data"] == "exit":
                self.broadcast(room, f"{current_name} покинул игру.")
                room.remove_client(current_client)
                current_client.close()

                if len(room.clients) < 2:
                    self.broadcast(room, "Игра завершена. Недостаточно игроков. Выберите другую комнату")
                    for client in room.clients:
                        self.handler(client, room.clients[client])
                        del room.clients[client]
                    break

            elif msg["type"] == "command" and msg["data"].startswith("change"):
                print('lalala')
                self.change_room(current_client, room.clients[current_client], msg['data'][7:])

                if len(room.clients) < 2:
                    self.broadcast(room, "Игра завершена. Недостаточно игроков. Выберите другую комнату")
                    for client in room.clients:
                        self.handler(client, room.clients[client])
                        del room.clients[client]
                    break

            elif msg["type"] == "command" and msg["data"].startswith("ban"):
                send_pickle(current_client, {'type': 'message', 'data': 'Введите имя для бана: '})
                tg_name = rec_pickle(current_client)['data']
                room.banned.add(self.get_key(room.clients, tg_name))
                cl = self.get_key(room.clients, tg_name)
                room.remove_client(self.get_key(room.clients, tg_name))
                self.handler(cl, tg_name)

                if len(room.clients) < 2:
                    self.broadcast(room, "Игра завершена. Недостаточно игроков. Выберите другую комнату")
                    for client in room.clients:
                        self.handler(client, room.clients[client])
                        del room.clients[client]
                    break

    def handler(self, client, name):
        msg = rec_pickle(client)
        if msg["type"] == "command":
            if msg["data"].startswith("change"):
                self.change_room(client, name, msg["data"][7:])
        elif msg['type'] == 'message':
            send_pickle(client, {"type": "message", "data": "Выберите другую комнату."})

    def get_key(self, my_dict, val):
        for key, value in my_dict.items():
            if val == value:
                return key

    def broadcast(self, room, message):
        for client in room.clients.keys():
            try:
                send_pickle(client, {"type": "message", "data": message})
            except Exception as e:
                print(f"Ошибка отправки сообщения: {e}")
