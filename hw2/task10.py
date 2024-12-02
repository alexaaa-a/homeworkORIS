# 10. Смоделируйте систему автопарковки с ограниченным
# количеством мест. Автомобили приезжают и уезжают в случайное время.
# Имплементируйте логику, проверяющую наличие свободных мест перед заездом
# автомобиля.
# Симулируйте время, которое автомобиль проводит на парковке, и его последующий выезд,
# освобождая тем самым место.

import random
import time


class Parking:
    def __init__(self, total_spots):
        self.total_spots = total_spots
        self.occupied_spots = 0

    def enter(self):
        if self.occupied_spots < self.total_spots:
            self.occupied_spots += 1
            print(f"Автомобиль заехал. Свободных мест осталось: {self.total_spots - self.occupied_spots}")
            parking_time = random.randint(1, 10)
            print(f"Автомобиль будет на парковке {parking_time} секунд.")
            time.sleep(parking_time)
            self.exit()
        else:
            print("Парковка полна. Невозможно заехать.")

    def exit(self):
        if self.occupied_spots > 0:
            self.occupied_spots -= 1
            print(f"Автомобиль уехал. Свободных мест теперь: {self.total_spots - self.occupied_spots}")
        else:
            print("Нет автомобилей на парковке.")


parking = Parking(5)

while True:
    action = input("Введите 'заезд', чтобы автомобиль заехал, или 'выезд', чтобы автомобиль уехал: ").strip().lower()
    if action == 'заезд':
        parking.enter()
    elif action == 'выезд':
        parking.exit()
    else:
        print("Неверная команда. Пожалуйста, введите 'заезд' или 'выезд'.")


