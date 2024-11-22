import socket
import threading


class Server:
    def __init__(self, host, port):
        self.sock = None
        self.host = host
        self.port = port
        self.clients = []
        self.names = []
        self.addresses = []
        self.usedCities = []
        self.isActive = True
        self.turn = 0
        self.server_active = True
        self.lock = threading.Lock()

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
                with self.lock:
                    self.clients.append(client)
                    self.addresses.append(client_address)
                print(f"Подключен клиент: {client_address}")

                name = client.recv(1024).decode()
                self.names.append(name)
                self.broadcast(f"{name} присоединился к игре!")

                if len(self.clients) == 2:
                    self.broadcast("Два игрока подключены! Игра начинается!")
                    game_thread = threading.Thread(target=self.game)
                    game_thread.start()

            except socket.error as e:
                print(f"Ошибка подключения клиента: {e}")
                break

    def game(self):
        self.usedCities = []
        self.isActive = True
        self.turn = 0

        while self.isActive and len(self.clients) == 2:
            with self.lock:
                curr_client = self.clients[self.turn]
                next_turn = (self.turn + 1) % 2

            try:
                curr_client.send("Введите город: ".encode())
                city = curr_client.recv(1024).decode().strip()

                if city in self.usedCities:
                    curr_client.send("Такой город уже был. Попробуйте снова.\n".encode())
                    continue

                if self.usedCities and self.usedCities[-1][-1].lower() != city[0].lower():
                    curr_client.send(
                        f"Город должен начинаться с буквы '{self.usedCities[-1][-1]}'. Попробуйте снова.\n".encode()
                    )
                    continue

                self.usedCities.append(city)
                self.broadcast(f"{self.names[self.turn]}: {city}")

                self.turn = next_turn

            except socket.error:
                self.broadcast(f"Игрок {self.turn + 1} отключился. Игра завершена.")
                self.isActive = False
                break

        self.end_game()

    def broadcast(self, message):
        print(message)
        with self.lock:
            for client in self.clients:
                try:
                    client.send(message.encode())
                except:
                    continue

    def end_game(self):
        with self.lock:
            self.isActive = False
            for client in self.clients:
                try:
                    client.send("Игра завершена. Спасибо за участие!".encode())
                    client.close()
                except:
                    pass
            self.clients.clear()
            self.addresses.clear()

    def disconnect(self):
        self.server_active = False
        self.end_game()
        if self.sock:
            self.sock.close()
        print("Сервер завершил работу.")
