# Car object and spawn logic
import random

class Car:
    def __init__(self, arrival_time, parking_duration):
        self.arrival_time = arrival_time
        self.parking_duration = parking_duration
        self.slot = None
        self.wait_time = 0

    @staticmethod
    def random_car(current_time, mean_duration=10):
        duration = random.randint(mean_duration//2, mean_duration*3//2)
        return Car(arrival_time=current_time, parking_duration=duration)
