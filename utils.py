import pickle
import struct


def send_pickle(sock, data):
    try:
        serialized_data = pickle.dumps(data)
        data_length = len(serialized_data)
        print(f"Отправляем данные: {data}, длина: {data_length}")
        sock.sendall(struct.pack("!I", data_length))
        sock.sendall(serialized_data)
    except Exception as e:
        print(f"Ошибка при отправке данных: {e}")


def rec_pickle(sock):
    try:
        length_bytes = sock.recv(4)
        if not length_bytes:
            print("Ошибка: не удалось получить длину данных.")
            return None
        data_length = struct.unpack("!I", length_bytes)[0]
        print(f"Ожидаем данные длиной: {data_length}")

        data = b""
        while len(data) < data_length:
            packet = sock.recv(data_length - len(data))
            if not packet:
                print("Ошибка: соединение прервано.")
                return None
            data += packet

        deserialized_data = pickle.loads(data)
        print(f"Получены данные: {deserialized_data}")
        return deserialized_data
    except Exception as e:
        print(f"Ошибка при десериализации данных: {e}")
        return None




