# Main Pygame loop for parking lot simulation
import pygame
from sim.parking_lot import ParkingLot
from sim.car import Car
from sim.metrics import Metrics
from sim.visualization import draw_parking_lot, SLOT_SIZE, MARGIN, ENTRY_ROAD_WIDTH
import random

ROWS, COLS = 5, 10
SCREEN_W = ENTRY_ROAD_WIDTH + COLS * (SLOT_SIZE + MARGIN)
SCREEN_H = ROWS * (SLOT_SIZE + MARGIN)
FPS = 30

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption('Parking Lot Optimizer')
        self.clock = pygame.time.Clock()
        self.lot = ParkingLot(ROWS, COLS)
        self.metrics = Metrics()
        self.cars = []
        self.time = 0
        self.spawn_timer = 0
        self.font = pygame.font.SysFont(None, 24)

    def spawn_car(self):
        car = Car.random_car(self.time)
        free_slots = self.lot.get_free_slots()
        if free_slots:
            slot = random.choice(free_slots)
            self.lot.occupy(*slot)
            car.slot = slot
            self.metrics.record_park(car.wait_time)
            leave_time = self.time + car.parking_duration
            self.cars.append({'car': car, 'leave_time': leave_time})
        else:
            self.metrics.record_fail()

    def update(self):
        self.time += 1/FPS
        self.spawn_timer += 1/FPS
        # Poisson process: spawn car on average every 3 seconds
        if self.spawn_timer > random.expovariate(1/3):
            self.spawn_car()
            self.spawn_timer = 0
        # Remove cars whose time is up
        for c in list(self.cars):
            if c['leave_time'] <= self.time:
                self.lot.free(*c['car'].slot)
                self.cars.remove(c)

    def draw_metrics(self):
        occ = self.lot.occupancy_percent()
        txt = f"Occupancy: {occ:.0f}%  Parked: {self.metrics.parked}  Failed: {self.metrics.failed}  Avg wait: {self.metrics.avg_wait():.1f}  Reward: {self.metrics.rewards}"
        img = self.font.render(txt, True, (255,255,255))
        self.screen.blit(img, (10, SCREEN_H-30))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            self.update()
            draw_parking_lot(self.screen, self.lot, [c['car'] for c in self.cars])
            self.draw_metrics()
            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()

if __name__ == '__main__':
    Game().run()
