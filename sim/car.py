# Car object and spawn logic
import random

class Car:
    def __init__(self, arrival_time, parking_duration):
        self.arrival_time = arrival_time
        self.parking_duration = parking_duration
        self.slot = None
        self.wait_time = 0
        self.x = 0  # Current x position (for animation)
        self.y = 0  # Current y position (for animation)
        self.path = []  # List of (x, y) waypoints to follow
        self.path_idx = 0
        self.parked = False

    @staticmethod
    def random_car(current_time, mean_duration=10):
        duration = random.randint(mean_duration//2, mean_duration*3//2)
        return Car(arrival_time=current_time, parking_duration=duration)

    def set_path(self, path):
        self.path = path
        self.path_idx = 0
        if path:
            self.x, self.y = path[0]

    def move_along_path(self, speed=4):
        if self.parked or not self.path or self.path_idx >= len(self.path)-1:
            return
        tx, ty = self.path[self.path_idx+1]
        dx, dy = tx - self.x, ty - self.y
        dist = (dx**2 + dy**2) ** 0.5
        if dist < speed:
            self.x, self.y = tx, ty
            self.path_idx += 1
            if self.path_idx == len(self.path)-1:
                self.parked = True
        else:
            self.x += speed * dx / dist
            self.y += speed * dy / dist
