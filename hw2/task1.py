# 1. Напишите программу для создания нескольких потоков и вывода
# их имен.

import threading


def just_fun():
    print(f"Сейчас поток {threading.current_thread().name}")
    print(f"Поток {threading.current_thread().name} завершился")


n = int(input("Введите число потоков: "))
threads = []

for _ in range(n):
    th = threading.Thread(target=just_fun)
    threads.append(th)
    th.start()

for i in threads:
    i.join()

print("Все потоки завершились")
