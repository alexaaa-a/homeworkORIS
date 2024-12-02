# Напишите программу, которая сортирует большой массив чисел,
# используя потоки. Основная идея состоит в том, чтобы разбить массив на
# подмассивы, которые будут сортироваться в отдельных потоках. Затем нужно
# объединить отсортированные подмассивы в единый отсортированный массив

import threading

sorted_sublists = []
lock = threading.Lock()


def sort_list(sublist):
    sorted_sublist = sorted(sublist)
    with lock:
        sorted_sublists.append(sorted_sublist)


def merge_sorted_sublists(sorted_lists):
    result = []
    for lst in sorted_lists:
        result = sorted(result + lst)
    return result


n = int(input("Введите число потоков: "))
num_of_els = int(input("Введите длину массива для сортировки: "))

user_lst = [int(input("Введите элемент списка: ")) for _ in range(num_of_els)]

parts = len(user_lst) // n
threads = []

for i in range(n):
    start = i * parts
    end = (i + 1) * parts if i < n - 1 else len(user_lst)
    sublist = user_lst[start:end]
    th = threading.Thread(target=sort_list, args=(sublist,))
    th.start()
    threads.append(th)

for th in threads:
    th.join()

final = merge_sorted_sublists(sorted_sublists)
print(final)
