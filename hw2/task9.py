# 9. Разработайте приложение-калькулятор, которое выполняет
# сложные математические вычисления, такие как вычисление факториалов,
# возведение в степень и интеграция, используя многопоточность для
# параллельного выполнения операций.
# Каждое вычисление запускается в отдельном потоке.
# Объедините результаты вычислений из всех потоков.
# Позаботьтесь об обработке ошибок и исключений, чтобы приложение оставалось
# стабильным даже при сбоях в отдельных вычислениях.

import threading
import math
import sympy as sp


def factorial(n):
    try:
        result = math.factorial(n)
        print(f"Факториал {n}! = {result}")
        return result
    except Exception as e:
        print(f"Ошибка при вычислении факториала: {e}")
        return None


def exponentiation(base, exponent):
    try:
        result = base ** exponent
        print(f"{base} в степени {exponent} = {result}")
        return result
    except Exception as e:
        print(f"Ошибка при вычислении степени: {e}")
        return None


def calculate_integral(expr, variable):
    try:
        integral = sp.integrate(expr, variable)
        print(f"Интеграл {expr} по {variable} = {integral}")
        return integral
    except Exception as e:
        print(f"Ошибка при вычислении интеграла: {e}")
        return None



print("Выберите операцию:")
print("1. Вычисление факториала")
print("2. Возведение в степень")
print("3. Вычисление интеграла")
choice = input("Введите номер операции (1/2/3): ")

threads = []
results = []

if choice == "1":
    n = int(input("Введите число для вычисления факториала: "))
    thread = threading.Thread(target=lambda: results.append(factorial(n)))
    threads.append(thread)

elif choice == "2":
    base = float(input("Введите основание: "))
    exponent = float(input("Введите показатель степени: "))
    thread = threading.Thread(target=lambda: results.append(exponentiation(base, exponent)))
    threads.append(thread)

elif choice == "3":
    expr = input("Введите выражение для интегрирования (например, x**2 + 2*x + 1): ")
    variable = sp.Symbol(input("Введите переменную (например, x): "))
    thread = threading.Thread(target=lambda: results.append(calculate_integral(sp.sympify(expr), variable)))
    threads.append(thread)

else:
    print("Неверный выбор!")

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()

print("\nРезультаты вычислений:")
for result in results:
    print(result)


