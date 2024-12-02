# Создайте модель банкомата, который обслуживает несколько
# клиентов одновременно. Каждый клиент (поток) может снимать деньги с
# общего счета. Используйте синхронизацию, чтобы избежать неправильных
# расчетов остатка.
# Организуйте процесс так, чтобы клиенты ожидали, если на их счёте недостаточно средств.

import threading
from concurrent.futures import ThreadPoolExecutor
import time
import random


class Bank:
    def __init__(self, balance):
        self.balance = balance
        self.condition = threading.Condition()

    def bank_account(self, amt):
        with self.condition:
            while self.balance < amt:
                print(f"Клиент {threading.current_thread().name} ждет. Недостаточно средств на балансе.")
                self.condition.wait()
            self.balance -= amt
            print(f"Клиент {threading.current_thread().name} снял сумму: {amt}. Остаток: {self.balance}")

    def deposit(self, amt):
        with self.condition:
            self.balance += amt
            print(f"Баланс пополнен. Текущая сумма: {self.balance}")
            self.condition.notify_all()


def client(acc, amt):
    time.sleep(1)
    acc.bank_account(amt)


def add_money(acc, amt):
    time.sleep(1)
    acc.deposit(amt)


n = int(input("Введите число клиентов банка: "))
summy = int(input("Введите баланс банка: "))
limit = int(input("Введите лимит для снятия денег одним клиентом: "))
limit_deposit = int(input("Введите лимит для пополнения банковского счета: "))

account = Bank(summy)
threads = 5

with ThreadPoolExecutor(max_workers=threads) as executor:
    for i in range(n):
        amount = random.randint(1, limit)
        executor.submit(client, account, amount)

    for i in range(n // 2):
        amount = random.randint(limit_deposit // 2, limit_deposit)
        executor.submit(add_money, account, amount)
