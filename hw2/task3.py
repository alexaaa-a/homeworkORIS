# Напишите программу для вычисления факториала числа с
# использованием нескольких потоков.

import threading
import functools


def factorial(start, end):
    k = 1
    for j in range(start, end):
        k *= j
    res.append(k)


res = []
n = int(input("Введите количество потоков: "))
num = int(input("Введите число, факториал которого нужно найти: "))

parts = num // n
threads = []

for i in range(n):
    st = i * parts + 1
    en = parts * (i + 1) + 1 if i < n - 1 else num + 1
    th = threading.Thread(target=factorial, args=(st, en))
    th.start()
    threads.append(th)

for th in threads:
    th.join()


print(functools.reduce(lambda x, y: x * y, res))
