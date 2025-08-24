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
        self.color = None  # Fixed color to prevent blinking
        self.park_start_time = None  # When the car actually parked
        self.leaving = False  # Whether car is leaving the lot

    @staticmethod
    def random_car(current_time, mean_duration=10):
        duration = random.randint(mean_duration//2, mean_duration*3//2)
        return Car(arrival_time=current_time, parking_duration=duration)

    def set_path(self, path):
        self.path = path
        self.path_idx = 0
        if path:
            self.x, self.y = path[0]
        # Assign a fixed color to prevent blinking
        import random
        colors = [(0, 100, 200), (200, 50, 50), (50, 150, 50), (200, 200, 50)]
        self.color = random.choice(colors)

    def start_leaving(self, exit_path):
        """Set the car to start leaving with the given exit path"""
        self.leaving = True
        self.parked = False
        self.path = exit_path
        self.path_idx = 0

    def move_along_path(self, speed=1.5, current_time=0):
        if not self.path or self.path_idx >= len(self.path):
            return False  # Return False when path is complete
        
        # If we're at the last waypoint, we're done
        if self.path_idx == len(self.path) - 1:
            if not self.leaving and not self.parked:
                self.parked = True
                self.park_start_time = current_time
            return False
        
        tx, ty = self.path[self.path_idx + 1]
        dx, dy = tx - self.x, ty - self.y
        dist = (dx**2 + dy**2) ** 0.5
        
        if dist < speed:
            self.x, self.y = tx, ty
            self.path_idx += 1
        else:
            self.x += speed * dx / dist
            self.y += speed * dy / dist
        
        return True  # Return True while still moving
