# Напишите программу, которая параллельно вычисляет значения
# сложной математической функции (например, факториал, числа Фибоначчи
# или другое), используя несколько потоков.
# Дайте пользователю возможность задавать количество потоков.
# Каждый поток должен принимать на вход числа, на которых нужно произвести вычисления,
# и возвращать результат.
# Итоги вычислений всех потоков должны выводиться после завершения всех вычислений

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
    print(f"Поток {i} начал свою работу")
    threads.append(th)

for x in range(len(threads)):
    threads[x].join()
    print(f"Поток {x} завершил работу. Результат его выполнения: {res[x]}")

print(f"Итоговый результат: {functools.reduce(lambda x, y: x * y, res)}")