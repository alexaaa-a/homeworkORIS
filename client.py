import socket
import threading


class Client:
    def __init__(self, host, port):
        self.sock = None
        self.host = host
        self.port = port
        self.isConnected = False

    def connect(self, name):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.sock.send(name.encode())
        self.isConnected = True

    def send_message(self, message):
        if self.isConnected:
            self.sock.send(message.encode())

    def receive_message(self, call):
        def recv():
            while self.isConnected:
                try:
                    data = self.sock.recv(1024).decode()
                    call(data)
                except:
                    break

        recv_thread = threading.Thread(target=recv, daemon=True)
        recv_thread.start()

    def disconnect(self):
        self.sock.close()
        self.isConnected = False

