# 2. Напишите программу для поиска простых чисел в заданном
# диапазоне с использованием многопоточности. Разбейте диапазон на части и
# назначьте каждому потоку свою часть для поиска простых чисел

import threading
from math import sqrt


def search_primes(start, end):
    for i in range(start, end):
        k = 0
        for j in range(2, int(sqrt(i)) + 1):
            if i % j == 0:
                k += 1
        if k == 0:
            res.append(i)


res = []

n = int(input("Введите число потоков: "))
rangePrimes = int(input("Введите конец диапазона, в котором нужно найти простые числа: "))
parts = rangePrimes // n
myThreads = []

for i in range(n):
    st = i * parts + 1
    en = (i + 1) * parts + 1 if i < n - 1 else rangePrimes + 1
    th = threading.Thread(target=search_primes, args=(st, en,))
    th.start()
    myThreads.append(th)

for th in myThreads:
    th.join()

res.remove(1)
print(res)
