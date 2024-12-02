# Реализуйте программу для параллельного поиска файлов в разных
# каталогах с использованием потоков. Программа должна находить файлы,
# соответствующие определенному паттерну, например, по расширению или
# имени.
# Используйте потоки, чтобы обрабатывать каждый каталог параллельно.
# Реализуйте механизм сбора результатов из всех потоков и отображение их пользователю.
# Обеспечьте контроль над количеством одновременно активных потоков.

import os
import fnmatch
from queue import Queue
from threading import Thread, Lock


def search_files(directory, pattern, result_queue, lock):
    try:
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if fnmatch.fnmatch(filename, pattern):
                    lock.acquire()
                    try:
                        result_queue.put(os.path.join(root, filename))
                    finally:
                        lock.release()
    except Exception as e:
        lock.acquire()
        try:
            print(f"Ошибка {directory}: {e}")
        finally:
            lock.release()


def threaded_search(directories, pattern, max_threads):
    threads = []
    result_queue = Queue()
    lock = Lock()

    for directory in directories:
        while len(threads) >= max_threads:
            for t in threads:
                if not t.is_alive():
                    threads.remove(t)

        thread = Thread(target=search_files, args=(directory, pattern, result_queue, lock))
        threads.append(thread)
        thread.start()

    for t in threads:
        t.join()

    results = []
    while not result_queue.empty():
        results.append(result_queue.get())

    return results



try:
    directories_to_search = input("Введите пути к каталогам для поиска (через запятую): ").split(",")
    directories_to_search = [d.strip() for d in directories_to_search if d.strip()]

    if not directories_to_search:
        raise ValueError("Не указаны каталоги для поиска.")

    search_type = input("Искать по имени или расширению файла? Введите 'имя' или 'расширение': ").strip().lower()
    if search_type not in ['имя', 'расширение']:
        raise ValueError("Некорректный тип поиска. Введите 'имя' или 'расширение'.")

    if search_type == 'имя':
        search_pattern = input("Введите имя файла (например, myfile.txt): ").strip()
    else:
        search_pattern = f"*.{input('Введите расширение файлов (например, txt): ').strip()}"

    if not search_pattern:
        raise ValueError("Паттерн поиска не может быть пустым.")

    max_active_threads = input("Введите максимальное количество активных потоков: ").strip()
    if not max_active_threads.isdigit() or int(max_active_threads) <= 0:
        raise ValueError("Некорректное количество потоков. Введите положительное целое число.")

    max_active_threads = int(max_active_threads)

    print("Запуск поиска...")
    found_files = threaded_search(directories_to_search, search_pattern, max_active_threads)

    print("Поиск завершён. Найденные файлы:")
    for file in found_files:
        print(file)

except ValueError as ve:
    print(f"Ошибка: {ve}")
except Exception as e:
    print(f"Произошла ошибка: {e}")