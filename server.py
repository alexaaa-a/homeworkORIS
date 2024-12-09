import socket
import threading
from utils import send_pickle, rec_pickle


class Room:
    def __init__(self, name):
        self.name = name
        self.clients = []
        self.names = []
        self.usedCities = []
        self.turn = 0
        self.isActive = True
        self.admins = []


class Server:
    def __init__(self, host, port):
        self.sock = None
        self.host = host
        self.port = port
        self.server_active = True
        self.lock = threading.Lock()
        self.rooms = {}

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

                name = rec_pickle(client)["data"]
                if not name:
                    send_pickle(client, {"type": "message", "data": "Ошибка: Имя не может быть пустым."})
                    client.close()
                    continue

                room_name = self.comm_room(client)

                if not room_name:
                    send_pickle(client, {"type": "message", "data": "Ошибка: Имя комнаты не указано."})
                    client.close()
                    continue

                with self.lock:
                    if room_name not in self.rooms:
                        self.rooms[room_name] = Room(room_name)
                    room = self.rooms[room_name]

                with self.lock:
                    room.clients.append(client)
                    room.names.append(name)

                self.broadcast(room, f"{name} присоединился к комнате!")
                send_pickle(client, {"type": "message", "data": "Вы успешно подключены к комнате!"})
                print(f"{name} успешно подключился к комнате {room_name}.")

                if len(room.clients) == 2:
                    game_thread = threading.Thread(target=self.game, args=(room,))
                    game_thread.start()

            except Exception as e:
                print(f"Ошибка подключения клиента: {e}")
                break

    def game(self, room: Room):
        room.usedCities = []
        room.isActive = True
        room.turn = 0

        while room.isActive:
            with self.lock:
                curr_client = room.clients[room.turn]
                next_turn = (room.turn + 1) % 2

            try:
                send_pickle(curr_client, {"type": "message", "data": "Введите город: "})
                city = rec_pickle(curr_client)['data']

                if (city == 'exit' or city == 'change') and len(room.clients) == 2:
                    self.handle_command(curr_client, room, city)
                    break

                elif city.startswith('ban ') and len(room.clients) == 2 and room.turn == 0:
                    self.handle_command(curr_client, room, city)
                    break

                if city in room.usedCities:
                    send_pickle(curr_client, {"type": "message", "data": "Такой город уже был. Попробуйте снова.\n"})
                    continue

                if room.usedCities and room.usedCities[-1][-1].lower() != city[0].lower():
                    send_pickle(curr_client,
                        {"type": "message", "data": f"Город должен начинаться с буквы '{room.usedCities[-1][-1]}'. Попробуйте снова.\n"}
                    )
                    continue

                room.usedCities.append(city)
                self.broadcast(room, f"{room.names[room.turn]}: {city}")

                room.turn = next_turn

            except socket.error:
                self.broadcast(room, f"Игрок {room.names[room.turn]} отключился. Игра завершена.")
                room.isActive = False
                break

        self.end_game(room)

    def broadcast(self, room, message):
        for client in room.clients:
            send_pickle(client, {"type": "message", "data": message})

    def end_game(self, room):
        room.isActive = False
        for client in room.clients:
            try:
                send_pickle(client, {"type": "message", "data": "Игра завершена. Спасибо за участие!"})
                client.close()
            except:
                pass
        del self.rooms[room.name]

    def stateOfGame(self, client, room):
        state = {"type": "state", "data": {
            "usedCities": room.usedCities,
            "players": room.names,
            "turn": room.turn
        }
                 }
        send_pickle(client, state)

    def exit(self, client, room: Room):
        idx = room.clients.index(client)
        name = room.names.pop(idx)
        room.clients.remove(client)
        self.broadcast(room, f"Игрок {name} покинул игру.")
        client.close()

        if not room.clients:
            self.rooms.pop(room)

    def change(self, client, room):
        index = room.clients.index(client)
        name = room.names[index]
        self.broadcast(room, f"{name} покинул комнату.")

        send_pickle(client, {"type": "rooms", "data": f" rooms: {[r for r in self.rooms.keys()]}"})
        send_pickle(client, {"type": "message", "data": "Выберите новую комнату:"})

        new_room_name = rec_pickle(client)["data"]
        new_room = next((r for r in self.rooms.keys() if r == new_room_name), None)

        if new_room:
            new_room.clients.append(client)
            self.broadcast(new_room, f"{name} присоединился к комнате {new_room.name}.")
        else:
            send_pickle(client, {"type": "message", "data": "Комната не найдена. Вы остались в текущей комнате."})
            room.clients.append(client)

        room.clients.remove(client)

    def ban(self, client, room, target_name):
        if client not in room.admins:
            send_pickle(client, {"type": "message", "data": "Вы не администратор и не можете банить игроков."})
            return

        target_client = next((c for c, n in zip(room.clients, room.names) if n == target_name), None)
        if target_client:
            room.clients.remove(target_client)
            room.names.remove(target_name)
            send_pickle(target_client, {"type": "message", "data": "Вы были заблокированы администратором."})
            target_client.close()
            self.broadcast(room, f"Игрок {target_name} был заблокирован.")
        else:
            send_pickle(client, {"type": "message", "data": "Игрок с таким именем не найден."})

    def handle_command(self, client, room, command):
        if command == "exit":
            self.exit(client, room)
        elif command == "change":
            self.change(client, room)
        elif command.startswith("ban "):
            self.ban(client, room, command.split(" ", 1)[1])
        else:
            send_pickle(client, {"type": "message", "data": "Неизвестная команда"})

    def comm_room(self, client):
        try:
            room_names = ", ".join(self.rooms.keys()) or "Нет доступных комнат"
            send_pickle(client, {"type": "message", "data": f"Доступные комнаты: {room_names} \n"
                                                            f"Для создания новой комнаты или присоединения к "
                                                            f"существующей введите команду /join_room <название комнаты>"})

            response = rec_pickle(client)
            if not response or response.get("type") != "command" or not response.get("data").startswith("join_room"):
                send_pickle(client, {"type": "error", "data": "Ошибка: Не указана комната для подключения."})
                return None

            room_name = response["data"].split(" ", 1)[1] if " " in response["data"] else None
            return room_name
        except Exception as e:
            print(f"Ошибка в методе comm_room: {e}")
            return None

    def join_room(self, client, current_room, new_room_name):
        if new_room_name not in self.rooms:
            send_pickle(client, {"type": "message", "data": "Комната не найдена."})
            return

        if current_room:
            current_room.clients.remove(client)
            idx = current_room.clients.index(client)
            current_room.names.pop(idx)
            self.broadcast(current_room, f"Игрок покинул комнату.")
            if not current_room.clients:
                del self.rooms[current_room.name]

        new_room = self.rooms[new_room_name]
        new_room.clients.append(client)
        new_room.admins.append(client)
        send_pickle(client, {"type": "message", "data": f"Вы вошли в комнату {new_room_name}"})
        self.broadcast(new_room, "Новый игрок присоединился!")



